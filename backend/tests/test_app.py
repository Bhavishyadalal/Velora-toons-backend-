from pathlib import Path
import base64
import pytest
from fastapi.testclient import TestClient
from app import parsers
from app.main import app,encode,decode,CACHE,BUCKETS,LOCKS
from app.network import SourceError,validate_url

F=Path(__file__).parent/'fixtures'
def fixture(name):return (F/(name+'.html')).read_text()

def test_catalogue_real_selectors_and_filter():
    parsed=parsers.catalogue(fixture('catalogue'))
    assert len(parsed['items'])==1
    assert parsed['items'][0]['title']=='Test & Adventure'
    assert parsed['items'][0]['poster'].startswith('https://image.tmdb.org/')
    assert parsed['has_more']

def test_title_seasons_not_invented_and_episode_number():
    parsed=parsers.title_page(fixture('title'),'https://watchanimeworld.one/series/test-adventure/')
    assert parsed['seasons']==[1,2]
    assert parsed['default_season']==2
    assert [e['number'] for e in parsed['episodes']]==[1,2]

def test_lazy_iframes_and_ad_filtering():
    frames=parsers.players(fixture('episode'),'https://watchanimeworld.one/episode/test-adventure-2x1/')
    assert len(frames)==2
    assert frames[1]['url']=='https://watchanimeworld.one/dub-player/t/123/'

def test_wrapper_json_only_and_not_soon():
    found=parsers.wrapper(fixture('wrapper'))
    assert [v['language'] for v in found]==['hin','eng']
    assert parsers.wrapper('<script>var CONFIG = dangerousFunction()</script>')==[]
    assert parsers.wrapper('<script>var CONFIG = {"prefix":"https://evil.example/","ready":{"eng":"test123"}}</script>')==[]

@pytest.mark.parametrize('url',['http://watchanimeworld.one/','https://127.0.0.1/','https://watchanimeworld.one.evil.example/','https://u:p@watchanimeworld.one/','https://watchanimeworld.one:999/','file:///etc/passwd'])
def test_fetch_destination_restriction(url):
    with pytest.raises(SourceError):validate_url(url)

@pytest.mark.parametrize('path',['//evil.example/x','/series/../x/','/wp-admin/','/series/test/?q=1','/episode/%2fprivate/'])
def test_invalid_refs(path):
    ref=base64.urlsafe_b64encode(path.encode()).decode().rstrip('=')
    with pytest.raises(SourceError):decode(ref)

class FakeFetcher:
    async def get(self,url):
        if '/category/' in url or '?s=' in url:return fixture('catalogue')
        if '/series/' in url:return fixture('title')
        if '/episode/' in url:return fixture('episode')
        if '/dub-player/' in url:return fixture('wrapper')
        raise SourceError('Removed','removed')

@pytest.fixture
def client():
    CACHE.clear();BUCKETS.clear();LOCKS.clear()
    with TestClient(app) as c:
        c.app.state.fetcher.get=FakeFetcher().get
        yield c

def test_api_catalogue_detail_and_resolution(client):
    listing=client.get('/api/catalog').json()
    item=listing['items'][0]
    detail=client.get('/api/title/'+item['id']).json()
    episode=detail['episodes'][0]
    result=client.get('/api/resolve/'+episode['id']).json()
    assert len(result['players'])==3
    assert any(p['language']=='hin' for p in result['players'])
    assert all(p['download_url'] is None for p in result['players'])
    assert all(p['mode']=='embed' for p in result['players'])

def test_season_error_not_wrong_default_episodes(client,monkeypatch):
    monkeypatch.setenv('ENABLE_BROWSER_SEASONS','0')
    ref=encode('https://watchanimeworld.one/series/test-adventure/')
    current=client.get('/api/season/'+ref+'?number=2')
    assert current.status_code==200
    other=client.get('/api/season/'+ref+'?number=1')
    assert other.status_code==502
    assert other.json()['error']['code']=='season_unavailable'
    assert 'episodes' not in other.json()

def test_cors_restricted_and_health(client):
    assert client.get('/health').json()['media_proxy'] is False
    assert client.get('/health',headers={'Origin':'https://evil.example'}).headers.get('access-control-allow-origin') is None
    assert client.get('/health',headers={'Origin':'http://localhost:5173'}).headers['access-control-allow-origin']=='http://localhost:5173'

def test_validation_and_bad_ids(client):
    assert client.get('/api/catalog?kind=evil').status_code==422
    assert client.get('/api/catalog?page_number=999').status_code==422
    assert client.get('/api/title/invalid').status_code==400

def test_rate_limit(client):
    for _ in range(90):assert client.get('/api/title/invalid').status_code==400
    assert client.get('/api/title/invalid').status_code==429

def test_direct_candidates_explicit_video_only():
    html='<video src="https://storage.googleapis.com/bucket/video.mp4"></video><video src="http://127.0.0.1/test.mp4"></video><script>let url="https://storage.googleapis.com/not-explicit.mp4"</script><video src="https://storage.googleapis.com/chunk.mp4#mp4/chunk/1"></video>'
    assert parsers.direct_candidates(html,parsers.SOURCE)==['https://storage.googleapis.com/bucket/video.mp4']

@pytest.mark.asyncio
async def test_direct_probe_head_and_mime(monkeypatch):
    import httpx
    from app import network
    async def dns(*args,**kwargs):return [(None,None,None,None,('8.8.8.8',443))]
    monkeypatch.setattr('asyncio.get_running_loop',lambda: type('Loop',(),{'getaddrinfo':staticmethod(dns)})())
    # This isolated test uses no network. A known transport inspects the method.
    seen=[]
    def handler(request):
        seen.append(request.method)
        return httpx.Response(200,headers={'content-type':'video/mp4'})
    f=network.Fetcher()
    await f.client.aclose()
    f.client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        assert await f.probe_media('https://storage.googleapis.com/bucket/a.mp4')
        assert not await f.probe_media('https://evil.example/a.mp4')
        assert seen==['HEAD']
    finally:await f.close()
