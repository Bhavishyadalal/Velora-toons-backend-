import logging
import httpx
import pytest
from app import network
from app.network import SourceError,source_failure
from app.main import app,CACHE,BUCKETS
from fastapi.testclient import TestClient

@pytest.mark.parametrize('status,code',[(401,'source_auth_required'),(403,'source_access_denied'),(429,'source_rate_limited'),(503,'source_unavailable')])
def test_status_diagnostic_is_specific_and_sanitized(status,code,caplog):
    with caplog.at_level(logging.WARNING):
        exc=source_failure('https://watchanimeworld.one/private?token=DO_NOT_LOG',status)
    assert exc.code==code
    assert exc.upstream_status==status
    assert exc.source_host=='watchanimeworld.one'
    assert len(exc.request_id)==12
    assert 'DO_NOT_LOG' not in caplog.text
    assert '/private' not in caplog.text

def test_generic_403_is_not_assumed_verification():
    assert source_failure('https://watchanimeworld.one/',403).code=='source_access_denied'
    assert source_failure('https://watchanimeworld.one/',403,verification=True).code=='source_verification_required'

def test_retry_after_is_bounded():
    assert source_failure('https://watchanimeworld.one/',429,retry_after='9999999').retry_after==3600
    assert source_failure('https://watchanimeworld.one/',429,retry_after='bad').retry_after is None

@pytest.mark.asyncio
@pytest.mark.parametrize('status,body,header,code',[
 (403,'Access denied',{},'source_access_denied'),
 (403,'<title>Just a moment...</title>',{},'source_verification_required'),
 (403,'',{'cf-mitigated':'challenge'},'source_verification_required'),
 (429,'Please wait',{'retry-after':'60'},'source_rate_limited'),
])
async def test_fetch_response_preserves_reason_without_retry(monkeypatch,status,body,header,code):
    async def allowed(url):pass
    monkeypatch.setattr(network,'public_dns',allowed)
    calls=[]
    def handler(request):
        calls.append(request.url)
        return httpx.Response(status,text=body,headers=header)
    f=network.Fetcher()
    await f.client.aclose()
    f.client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(SourceError) as result:await f.get('https://watchanimeworld.one/')
        assert result.value.code==code
        assert result.value.upstream_status==status
        assert len(calls)==1
    finally:await f.close()

def test_api_error_details_and_healthy_backend(monkeypatch):
    CACHE.clear();BUCKETS.clear()
    with TestClient(app) as client:
        async def denied(url):raise source_failure(url,403)
        monkeypatch.setattr(client.app.state.fetcher,'get',denied)
        response=client.get('/api/catalog')
        error=response.json()['error']
        assert response.status_code==502
        assert error['upstream_status']==403
        assert error['code']=='source_access_denied'
        assert response.headers['cache-control']=='no-store'
        assert client.get('/health').status_code==200
