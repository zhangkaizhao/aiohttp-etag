import asyncio
import time

import aiohttp_etag
from aiohttp import web


async def plain(request):
    text = 'Hello aiohttp!'
    return web.Response(text=text)


async def resource(request):
    text = 'Hello aiohttp!'
    return web.json_response({
        'message': text,
    })


async def dynamic_plain(request):
    last_visit = time.time()
    text = 'Last visited: {}'.format(last_visit)
    return web.Response(text=text)


async def dynamic_resource(request):
    last_visit = time.time()
    return web.json_response({
        'last_visit': last_visit,
    })


async def chunked(request):
    response = web.StreamResponse()
    response.content_type = 'text/plain'
    await response.prepare(request)
    await response.write(b'OK')
    await asyncio.sleep(2)
    await response.write(b'GOOD')
    await response.write_eof()
    return response


async def make_app():
    app = web.Application()
    aiohttp_etag.setup(app)

    app.router.add_get('/', plain)
    app.router.add_get('/resource', resource)
    app.router.add_get('/dynamic', dynamic_plain)
    app.router.add_get('/dynamic/resource', dynamic_resource)
    app.router.add_get('/chunked', chunked)
    return app


web.run_app(make_app())
