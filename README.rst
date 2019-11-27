aiohttp-etag
============

The library provides Etag support for `aiohttp.web`__.

Most of the source code is ported from `Tornado`__.

.. _aiohttp_web: https://aiohttp.readthedocs.io/en/latest/web.html
.. _Tornado: https://www.tornadoweb.org/

__ aiohttp_web_

__ Tornado_

Installation
------------
Install from PyPI::

    pip install aiohttp-etag


Developing
----------

Install requirement and launch tests::

    pip install -r dev-requirements.txt
    pytest tests

Usage
-----

A trivial usage example:

.. code:: python

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
