"""Bounded HTTPS fetcher. Clients never supply arbitrary destination URLs."""
import asyncio
import ipaddress
import logging
import uuid
import socket
from urllib.parse import urlsplit, urljoin
import httpx

logger = logging.getLogger(__name__)

ALLOWED = {'watchanimeworld.one','watchanimeworld.top','player.abyssplayer.com','play.zephyrix.org'}
class SourceError(Exception):
    def __init__(self, message, code='source_unavailable', *, upstream_status=None,
                 source_host=None, retry_after=None, request_id=None):
        self.message, self.code = message, code
        self.upstream_status = upstream_status
        self.source_host = source_host
        self.retry_after = retry_after
        self.request_id = request_id
        super().__init__(message)


def source_failure(url, status, *, verification=False, retry_after=None):
    # Expose only status/hostname and a correlation ID, never page bodies,
    # cookies, request URLs, query strings or signed player tokens.
    host = urlsplit(url).hostname
    request_id = uuid.uuid4().hex[:12]
    if verification:
        code = 'source_verification_required'
        message = 'The source requires browser verification. This server cannot complete it. You can open the source website directly.'
    elif status == 401:
        code = 'source_auth_required'
        message = 'The source requires authentication (HTTP 401). Public catalogue access is unavailable to this server.'
    elif status == 403:
        code = 'source_access_denied'
        message = 'The source denied this server access (HTTP 403). Your Velora backend is online; the source did not allow the catalogue request.'
    elif status == 429:
        code = 'source_rate_limited'
        message = 'The source is rate limiting this server (HTTP 429). Wait before trying again.'
    else:
        code = 'source_unavailable'
        message = f'The source returned HTTP {status}. Try again later.'
    delay = None
    if isinstance(retry_after, str) and retry_after.isdigit():
        delay = min(max(int(retry_after), 1), 3600)
    logger.warning('source_fetch_failed host=%s status=%s code=%s request_id=%s', host, status, code, request_id)
    return SourceError(message, code, upstream_status=status, source_host=host,
                       retry_after=delay, request_id=request_id)

def validate_url(url):
    p=urlsplit(url)
    if p.scheme!='https' or p.hostname not in ALLOWED or p.username or p.password or p.port not in (None,443):
        raise SourceError('This destination is not supported.', 'destination_blocked')
    return url

async def public_dns(url):
    host=urlsplit(validate_url(url)).hostname
    try:
        infos=await asyncio.wait_for(asyncio.get_running_loop().getaddrinfo(host,443,type=socket.SOCK_STREAM),8)
    except (OSError,asyncio.TimeoutError) as e:
        raise SourceError('The source hostname could not be reached.') from e
    if not infos or any(not ipaddress.ip_address(row[4][0]).is_global for row in infos):
        raise SourceError('A source resolved to a private address.', 'destination_blocked')

class Fetcher:
    def __init__(self):
        self.client=httpx.AsyncClient(timeout=httpx.Timeout(18,connect=8), follow_redirects=False, trust_env=True, headers={'User-Agent':'VeloraToons/1.0 (+public catalogue reader)','Accept':'text/html,application/xhtml+xml'}, limits=httpx.Limits(max_connections=8,max_keepalive_connections=4))
        self.slots=asyncio.Semaphore(4)
    async def close(self):
        await self.client.aclose()
    async def get(self,url):
        async with self.slots:
            for _ in range(4):
                await public_dns(url)
                try:
                    async with self.client.stream('GET',url) as r:
                        if r.status_code in (301,302,303,307,308):
                            location=r.headers.get('location')
                            if not location:
                                raise SourceError('The source returned an invalid redirect.')
                            url=validate_url(urljoin(url,location))
                            continue
                        if r.status_code in (404,410):
                            raise SourceError('This source has been removed or is unavailable.','removed')
                        if r.status_code in (401,403,429):
                            # A status code alone does not prove bot detection.
                            # Read a small bounded error prefix to distinguish an
                            # explicit verification page from ordinary denial.
                            prefix = bytearray()
                            async for chunk in r.aiter_bytes(chunk_size=8192):
                                prefix.extend(chunk[:32768-len(prefix)])
                                if len(prefix) >= 32768:
                                    break
                            error_text = prefix.decode('utf-8', errors='replace')
                            verification = (r.headers.get('cf-mitigated') == 'challenge'
                                            or 'cf-chl-' in error_text
                                            or 'Just a moment...' in error_text[:2000])
                            raise source_failure(url, r.status_code, verification=verification,
                                                 retry_after=r.headers.get('retry-after'))
                        r.raise_for_status()
                        ctype=r.headers.get('content-type','').lower()
                        if 'html' not in ctype and 'text/' not in ctype:
                            raise SourceError('The source returned an unexpected format.')
                        chunks=[]; size=0
                        async for chunk in r.aiter_bytes():
                            size+=len(chunk)
                            if size>3_000_000:
                                raise SourceError('The source page exceeded the metadata limit.')
                            chunks.append(chunk)
                        body=b''.join(chunks).decode('utf-8',errors='replace')
                        if 'cf-chl-' in body or 'Just a moment...' in body[:2000]:
                            raise source_failure(url, r.status_code, verification=True)
                        return body
                except httpx.HTTPStatusError as e:
                    raise source_failure(url, e.response.status_code) from e
                except httpx.HTTPError as e:
                    raise SourceError('The source did not respond successfully. Try again later.') from e
            raise SourceError('The source redirected too many times.')

    async def probe_media(self,url):
        # HEAD only: no movie bytes traverse this server. Only explicit source video URLs.
        p=urlsplit(url)
        if p.scheme!='https' or p.hostname not in {'storage.googleapis.com','video-downloads.googleusercontent.com'} or p.fragment or p.username or p.password or p.port not in (None,443):
            return False
        try:
            infos=await asyncio.wait_for(asyncio.get_running_loop().getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM),8)
            if not infos or any(not ipaddress.ip_address(row[4][0]).is_global for row in infos):return False
            async with self.slots:
                r=await self.client.head(url,follow_redirects=False)
            return r.status_code==200 and r.headers.get('content-type','').split(';')[0].strip() in {'video/mp4','video/webm','video/x-matroska'}
        except (OSError,httpx.HTTPError,asyncio.TimeoutError):return False
