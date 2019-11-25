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


    async def home(request):
        last_visit = time.time()
        text = 'Last visited: {}'.format(last_visit)
        return web.Response(text=text)


    async def resource(request):
        last_visit = time.time()
        return web.json_response({
            'last_visit': last_visit,
        })


    async def make_app():
        app = web.Application()
        aiohttp_etag.setup(app)

        app.router.add_get('/', home)
        app.router.add_get('/resource', resource)
        return app


    web.run_app(make_app())
