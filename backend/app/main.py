import asyncio
import base64
import json
import os
import re
import time
from collections import OrderedDict, defaultdict, deque
from contextlib import asynccontextmanager
from urllib.parse import urlsplit
from fastapi import FastAPI, Request, Query, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .network import Fetcher, SourceError
from . import parsers

TTL=300
CACHE=OrderedDict()
LOCKS={}
BUCKETS=OrderedDict()

def encode(url):
    path=urlsplit(url).path
    return base64.urlsafe_b64encode(path.encode()).decode().rstrip('=')

def decode(ref):
    try:
        path=base64.b64decode(ref+'='*(-len(ref)%4),altchars=b'-_',validate=True).decode()
    except Exception:
        raise SourceError('Invalid content identifier.','invalid_id')
    if not re.fullmatch(r'/(series|movies|episode)/[a-zA-Z0-9_-]{1,240}/?',path):
        raise SourceError('Invalid content identifier.','invalid_id')
    return parsers.SOURCE+path

def decorate(items):
    return [{**i,'id':encode(i['url'])} for i in items]

@asynccontextmanager
async def lifespan(app):
    app.state.fetcher=Fetcher()
    yield
    await app.state.fetcher.close()

app=FastAPI(title='Velora Toons API',version='1.0.1',lifespan=lifespan)
origins=[x.strip().rstrip('/') for x in os.getenv('ALLOWED_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
if '*' in origins:
    raise RuntimeError('Use explicit ALLOWED_ORIGINS, never a wildcard.')
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET'],allow_headers=['Content-Type'],allow_credentials=False)

@app.middleware('http')
async def limits(request:Request, call_next):
    if request.url.path.startswith('/api/'):
        # Do not trust arbitrary X-Forwarded-For. Configure a known proxy at deployment.
        key=request.client.host if request.client else 'unknown'
        now=time.monotonic()
        q=BUCKETS.setdefault(key,deque())
        BUCKETS.move_to_end(key)
        while q and q[0]<now-60:q.popleft()
        if len(q)>=90:
            return JSONResponse({'error':{'code':'rate_limited','message':'Too many requests. Please wait one minute.'}},429,headers={'Retry-After':'60'})
        q.append(now)
        while len(BUCKETS)>2000:BUCKETS.popitem(last=False)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    return response

@app.exception_handler(SourceError)
async def source_error(request,exc):
    status=400 if exc.code in ('invalid_id','destination_blocked') else 502
    error={'code':exc.code,'message':exc.message}
    for name in ('upstream_status','source_host','retry_after','request_id'):
        value=getattr(exc,name,None)
        if value is not None:error[name]=value
    headers={'Cache-Control':'no-store'}
    if exc.retry_after is not None:headers['Retry-After']=str(exc.retry_after)
    return JSONResponse({'error':error},status,headers=headers)

async def page(request,url):
    now=time.monotonic()
    if url in CACHE and CACHE[url][0]>now:
        CACHE.move_to_end(url)
        return CACHE[url][1]
    lock=LOCKS.setdefault(url,asyncio.Lock())
    async with lock:
        if url in CACHE and CACHE[url][0]>time.monotonic():return CACHE[url][1]
        try:
            body=await request.app.state.fetcher.get(url)
            CACHE[url]=(time.monotonic()+TTL,body)
            CACHE.move_to_end(url)
            while len(CACHE)>48:CACHE.popitem(last=False)
            return body
        finally:
            # Keep only a bounded set of per-key locks. Each lock is temporary metadata.
            if len(LOCKS)>100:LOCKS.clear()

@app.api_route('/health',methods=['GET','HEAD'])
async def health(response:Response):
    response.headers['Cache-Control']='no-store'
    return {'status':'ok','service':'velora-toons','version':'1.0.1','media_proxy':False}

@app.get('/api/catalog')
async def catalog(request:Request,kind:str=Query('cartoon',pattern='^(cartoon|anime|movies)$'),page_number:int=Query(1,ge=1,le=30),q:str=Query('',max_length=100)):
    if q.strip():
        from urllib.parse import urlencode
        url=parsers.SOURCE+('/' if page_number==1 else f'/page/{page_number}/')+'?'+urlencode({'s':q.strip()})
    else:
        category='cartoon' if kind=='movies' else kind
        url=parsers.SOURCE+f'/category/type/{category}/'+('' if page_number==1 else f'page/{page_number}/')+('?type=movies' if kind=='movies' else '?type=series')
    result=parsers.catalogue(await page(request,url))
    return {**result,'items':decorate(result['items']),'page':page_number,'source':url,'fetched_at':int(time.time())}

@app.get('/api/title/{ref}')
async def title(ref:str,request:Request):
    url=decode(ref)
    if '/episode/' in url:raise SourceError('Choose a series or movie.','invalid_id')
    result=parsers.title_page(await page(request,url),url)
    result['id']=ref
    result['episodes']=decorate(result['episodes'])
    result['season_note']='Only episodes actually returned by the source are listed. Other seasons may need to be opened on the source website.'
    return result

@app.get('/api/resolve/{ref}')
async def resolve(ref:str,request:Request):
    url=decode(ref)
    if '/series/' in url:raise SourceError('Choose an episode first.','invalid_id')
    html=await page(request,url)
    frames=parsers.players(html,url)
    result=[]
    for target in parsers.direct_candidates(html,url):
        if await request.app.state.fetcher.probe_media(target):
            result.append({'label':'Direct video','language':'unknown','language_name':'Original audio','url':target,'mode':'direct','download_url':target,'verified':'head_video_mime'})
    for frame in frames[:6]:
        target=frame['url']
        if urlsplit(target).hostname=='watchanimeworld.one' and urlsplit(target).path.startswith('/dub-player/t/'):
            try:
                languages=parsers.wrapper(await page(request,target))
            except SourceError:
                languages=[]
            if languages:
                result.extend({'label':f"Abyss · {l['language_name']}",'language':l['language'],'language_name':l['language_name'],'url':l['url'],'mode':'embed','download_url':None,'verified':'public_wrapper'} for l in languages)
                continue
        result.append({'label':frame['label'],'language':'unknown','language_name':'Provider audio','url':target,'mode':'embed','download_url':None,'verified':'source_iframe'})
    result.sort(key=lambda p: (p['mode']!='direct',p['language']=='unknown'))
    return {'id':ref,'source':url,'players':result,'download_note':('A direct video URL passed a HEAD content-type check. Browser codec support and seeking depend on the host.' if any(p['mode']=='direct' for p in result) else 'No independently verified direct download was provided. Provider player links are not media file links.'),'expires_in':300}

@app.get('/api/season/{ref}')
async def season(ref:str,request:Request,number:int=Query(...,ge=1,le=999)):
    url=decode(ref)
    if '/series/' not in url:raise SourceError('Choose a series.','invalid_id')
    data=parsers.title_page(await page(request,url),url)
    if number not in data['seasons']:
        raise SourceError('This season is not listed by the source.','season_unavailable')
    available=[e for e in data['episodes'] if e['season']==number]
    if available:return {'episodes':decorate(available),'season':number,'note':'Episodes returned by the public source page.'}
    if os.getenv('ENABLE_BROWSER_SEASONS','0')!='1':
        raise SourceError('This season needs the optional browser adapter, which is disabled on this server. Use Source page to choose it there.','season_unavailable')
    from .seasons import browser_season
    key=f'{url}#season={number}'
    if key in CACHE and CACHE[key][0]>time.monotonic():available=CACHE[key][1]
    else:
        available=await browser_season(url,number)
        CACHE[key]=(time.monotonic()+TTL,available)
        while len(CACHE)>48:CACHE.popitem(last=False)
    return {'episodes':decorate(available),'season':number,'note':'Loaded through the source’s normal season selector.'}
