"""Pure parsers. No execution of source scripts and no invented episode lists."""
import json
import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup

SOURCE = 'https://watchanimeworld.one'
LANGS = {'hin':'Hindi','eng':'English','tam':'Tamil','tel':'Telugu','ben':'Bengali','mal':'Malayalam','kan':'Kannada'}

def clean(value):
    return re.sub(r'\s+', ' ', value or '').strip()

def soup(html):
    return BeautifulSoup(html, 'html.parser')

def text(node):
    return clean(node.get_text(' ', strip=True)) if node else ''

def image(node, base=SOURCE):
    if not node:
        return ''
    raw = node.get('data-src') or node.get('src') or ''
    return urljoin(base, raw) if raw and not raw.startswith('data:') else ''

def catalogue(html, base=SOURCE):
    doc = soup(html)
    items, seen = [], set()
    for card in doc.select('article.post'):
        a = card.select_one('a.lnk-blk[href]') or card.select_one('a[href*="/series/"], a[href*="/movies/"]')
        if not a:
            continue
        url = urljoin(base, a['href'])
        if urlsplit(url).hostname != urlsplit(SOURCE).hostname or not re.match(r'^/(series|movies)/[^/]+/?$', urlsplit(url).path):
            continue
        title = text(card.select_one('.entry-title')) or clean(a.get('title'))
        if not title or url in seen:
            continue
        seen.add(url)
        items.append({'title':title, 'url':url, 'poster':image(card.select_one('img')), 'badge':text(card.select_one('.post-ql')), 'year':text(card.select_one('.year')), 'kind':'movie' if '/movies/' in url else 'series'})
    nxt = doc.select_one('a.next[href], a.next.page-numbers[href], .nav-links a[rel="next"]')
    return {'items':items, 'has_more':bool(nxt)}

def episodes(doc, base):
    result, seen = [], set()
    for a in doc.select('a[href*="/episode/"]'):
        url = urljoin(base, a.get('href',''))
        path = urlsplit(url).path
        if urlsplit(url).hostname != urlsplit(SOURCE).hostname or not re.match(r'^/episode/[^/]+/?$', path) or url in seen:
            continue
        seen.add(url)
        m = re.search(r'-(\d+)x(\d+)/?$', path)
        card = a.find_parent(['article','li']) or a.parent
        label = text(card.select_one('.entry-title, .title, h2, h3, h4')) or text(a) or (f'Episode {int(m[2])}' if m else 'Episode')
        result.append({'title':label, 'url':url, 'season':int(m[1]) if m else None, 'number':int(m[2]) if m else None, 'poster':image(card.select_one('img'))})
    return result

def title_page(html, url):
    doc = soup(html)
    heading = doc.select_one('h1.entry-title, h1')
    og = doc.select_one('meta[property="og:image"]')
    desc = doc.select_one('.description, .entry-content .description, .overview, .entry-content')
    seasons = []
    for a in doc.select('[data-season]'):
        val = a.get('data-season','')
        if val.isdigit() and int(val) not in seasons:
            seasons.append(int(val))
    eps = episodes(doc, url)
    default = eps[0]['season'] if eps else None
    return {'title':text(heading) or 'Untitled', 'url':url, 'poster':urljoin(url, og['content']) if og and og.get('content') else image(doc.select_one('.post-thumbnail img, .poster img')), 'description':text(desc)[:1800], 'seasons':seasons, 'default_season':default, 'episodes':eps, 'kind':'movie' if '/movies/' in url else 'series'}

def players(html, url):
    doc = soup(html)
    found = []
    for frame in doc.select('iframe'):
        raw = frame.get('data-src') or frame.get('src')
        if not raw:
            continue
        target = urljoin(url, raw)
        path = urlsplit(target).path
        host = urlsplit(target).hostname
        if host not in {'watchanimeworld.one','watchanimeworld.top','player.abyssplayer.com','play.zephyrix.org'}:
            continue
        parent = frame.find_parent(id=re.compile(r'^options-'))
        label_a = doc.select_one(f'a[href="#{parent["id"]}"]') if parent else None
        label = text(label_a) or ('Abyss' if '/dub-player/' in path else 'Provider player')
        if target not in [x['url'] for x in found]:
            found.append({'label':label, 'url':target})
    return found

def wrapper(html):
    """Decode only a JSON literal, never eval JavaScript."""
    for script in soup(html).select('script:not([src])'):
        raw = script.string or script.get_text()
        match = re.search(r'\b(?:var|const|let)\s+CONFIG\s*=\s*',raw)
        if not match:
            continue
        try:
            cfg, _ = json.JSONDecoder().raw_decode(raw[match.end():].lstrip())
        except (ValueError, TypeError):
            continue
        if not isinstance(cfg,dict) or cfg.get('prefix') != 'https://player.abyssplayer.com/':
            continue
        result=[]
        ready=cfg.get('ready',{})
        if not isinstance(ready,dict):
            continue
        for lang, code in ready.items():
            if isinstance(code,str) and re.fullmatch(r'[A-Za-z0-9_-]{3,100}',code) and re.fullmatch(r'[a-z]{2,4}',lang):
                result.append({'language':lang,'language_name':LANGS.get(lang,lang.upper()), 'url':cfg['prefix']+code})
        return result
    return []

def direct_candidates(html,url):
    """Only explicit video/source elements; never promote JS chunk URLs to files."""
    result=[]
    for tag in soup(html).select('video[src], video source[src]'):
        target=urljoin(url,tag.get('src',''))
        p=urlsplit(target)
        host=p.hostname or ''
        if p.scheme=='https' and not p.fragment and not p.username and not p.password and p.port in (None,443) and (host=='storage.googleapis.com' or host=='video-downloads.googleusercontent.com'):
            if target not in result:result.append(target)
    return result[:2]
