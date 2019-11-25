import json
import time

import aiohttp_etag
from aiohttp import web


def create_app(handler, method='GET'):
    app = web.Application()
    aiohttp_etag.setup(app)
    app.router.add_route(method, '/', handler)
    return app


async def test_text_etag(aiohttp_client):

    async def handler(request):
        return web.Response(text='OK')

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    resp_text = await resp.text()
    assert resp_text == 'OK'
    assert resp.headers.get("Etag") is not None
    resp.close()


async def test_body_etag(aiohttp_client):

    async def handler(request):
        return web.Response(body=b'OK')

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    resp_text = await resp.text()
    assert resp_text == 'OK'
    assert resp.headers.get("Etag") is not None
    resp.close()


async def test_json_etag(aiohttp_client):
    last_visit = time.time()
    outdict = {
        'last_visit': last_visit,
    }

    async def handler(request):
        return web.json_response(outdict)

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    assert resp.content_type == 'application/json'
    resp_text = await resp.text()
    assert json.loads(resp_text) == outdict
    assert resp.headers.get("Etag") is not None
    resp.close()


async def test_etag_matched(aiohttp_client):

    async def handler(request):
        return web.Response(body=b'OK')

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    resp_text = await resp.text()
    assert resp_text == 'OK'
    etag = resp.headers.get("Etag")
    assert etag is not None
    resp.close()

    resp = await client.get('/', headers=[('If-None-Match', etag)])
    assert resp.status == 304
    assert resp.headers.get("Etag") == etag
    resp_text = await resp.text()
    assert resp_text == ''
    resp.close()

    resp = await client.get('/')
    assert resp.status == 200
    assert resp.headers.get("Etag") == etag
    resp_text = await resp.text()
    assert resp_text == 'OK'
    resp.close()


async def test_json_etag_matched(aiohttp_client):
    last_visit = time.time()
    outdict = {
        'last_visit': last_visit,
    }

    async def handler(request):
        return web.json_response(outdict)

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    assert resp.content_type == 'application/json'
    resp_text = await resp.text()
    assert json.loads(resp_text) == outdict
    etag = resp.headers.get("Etag")
    assert etag is not None
    resp.close()

    resp = await client.get('/', headers=[('If-None-Match', etag)])
    assert resp.status == 304
    assert resp.content_type == 'application/json'
    assert resp.headers.get("Etag") == etag
    resp_text = await resp.text()
    assert resp_text == ''
    resp.close()

    resp = await client.get('/')
    assert resp.status == 200
    assert resp.headers.get("Etag") == etag
    resp_text = await resp.text()
    assert json.loads(resp_text) == outdict
    resp.close()


async def test_etag_not_matched(aiohttp_client):

    async def handler(request):
        return web.Response(body=b'OK')

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    resp_text = await resp.text()
    assert resp_text == 'OK'
    etag = resp.headers.get("Etag")
    assert etag is not None
    resp.close()

    async def response_updated_handler(request):
        return web.Response(body=b'GOOD')

    client = await aiohttp_client(create_app(response_updated_handler))

    resp = await client.get('/', headers=[('If-None-Match', etag)])
    assert resp.status == 200
    assert resp.headers.get("Etag") != etag
    resp_text = await resp.text()
    assert resp_text == 'GOOD'
    resp.close()

    updated_etag = resp.headers.get("Etag")
    resp = await client.get('/', headers=[('If-None-Match', updated_etag)])
    assert resp.status == 304
    assert resp.headers.get("Etag") == updated_etag
    resp_text = await resp.text()
    assert resp_text == ''
    resp.close()


async def test_etag_wildcard_matched(aiohttp_client):

    async def handler(request):
        return web.Response(body=b'OK')

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/', headers=[('If-None-Match', '*')])
    assert resp.status == 304
    resp_text = await resp.text()
    assert resp_text == ''
    etag = resp.headers.get("Etag")
    assert etag is not None
    resp.close()

    async def response_updated_handler(request):
        return web.Response(body=b'GOOD')

    client = await aiohttp_client(create_app(response_updated_handler))

    resp = await client.get('/', headers=[('If-None-Match', '*')])
    assert resp.status == 304
    resp_text = await resp.text()
    assert resp_text == ''
    assert resp.headers.get("Etag") != etag
    resp.close()


async def test_not_get_method(aiohttp_client):

    async def handler(request):
        return web.Response(body=b'OK')

    for meth in ('POST', 'PUT', 'DELETE', 'HEAD', 'PATCH', 'OPTIONS'):
        client = await aiohttp_client(create_app(handler, method=meth))

        resp = await client.request(meth, '/')
        assert resp.status == 200
        # resp_text = await resp.text()
        # assert resp_text in ('', 'OK')
        assert resp.headers.get("Etag") is None
        resp.close()


async def test_chunked_response(aiohttp_client):

    async def handler(request):
        response = web.StreamResponse()
        await response.prepare(request)
        await response.write(b'OK')
        await response.write(b'GOOD')
        await response.write_eof()
        return response

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    resp_text = await resp.text()
    assert resp_text in ('', 'OKGOOD')
    assert resp.headers.get('Transfer-Encoding') == 'chunked'
    assert resp.headers.get("Etag") is None
    resp.close()


async def test_entity_tags(aiohttp_client):

    async def handler(request):
        return web.Response(body=b'OK')

    client = await aiohttp_client(create_app(handler))

    resp = await client.get('/')
    assert resp.status == 200
    resp_text = await resp.text()
    assert resp_text == 'OK'
    etag = resp.headers.get("Etag")
    assert etag is not None
    resp.close()

    entity_tags_etag = "W/" + etag
    resp = await client.get('/', headers=[('If-None-Match', entity_tags_etag)])
    assert resp.status == 304
    assert resp.headers.get("Etag") == etag
    resp_text = await resp.text()
    assert resp_text == ''
    resp.close()
