"""Optional normal-UI season navigation. No anti-bot or access-control bypass."""
import asyncio
from urllib.parse import urlsplit
from .network import SourceError, public_dns
from .parsers import soup, episodes
SLOTS=asyncio.Semaphore(1)

async def browser_season(url,number):
    try:
        from playwright.async_api import async_playwright, TimeoutError as BrowserTimeout
    except ImportError as e:
        raise SourceError('Dynamic seasons require the optional browser image. Open this season on the source website.','season_unavailable') from e
    await public_dns(url)
    async with SLOTS:
        try:
            async with async_playwright() as p:
                browser=await p.chromium.launch(headless=True)
                try:
                    context=await browser.new_context(service_workers='block')
                    # Only the source's scripts/API can load. Ads, popups and video hosts are unnecessary.
                    async def route(r):
                        u=urlsplit(r.request.url)
                        if u.scheme=='https' and u.hostname=='watchanimeworld.one' and r.request.resource_type not in ('image','media','font'):
                            await r.continue_()
                        else:await r.abort()
                    await context.route('**/*',route)
                    tab=await context.new_page()
                    tab.set_default_timeout(12000)
                    await tab.goto(url,wait_until='domcontentloaded',timeout=20000)
                    content=await tab.content()
                    if 'cf-chl-' in content or 'Just a moment...' in content[:2000]:
                        raise SourceError('The source requires verification. Open the source page.','source_restricted')
                    option=tab.locator(f'a[data-season="{number}"]')
                    if not await option.count():
                        raise SourceError('This season is not listed by the source.','season_unavailable')
                    if not await option.first.is_visible():
                        await tab.locator('.choose-season button').first.click()
                    await option.first.click()
                    # Read the normal UI result, never call hidden application internals.
                    await tab.wait_for_function('(season) => Array.from(document.querySelectorAll("a[href*=\"/episode/\"]")).some(a => new RegExp("-"+season+"x[0-9]+/?$").test(a.href))',arg=number,timeout=15000)
                    result=episodes(soup(await tab.content()),url)
                    return [e for e in result if e['season']==number]
                finally:
                    await browser.close()
        except SourceError:raise
        except Exception as e:
            raise SourceError('The dynamic season could not be loaded. Open the source page or try later.','season_unavailable') from e
