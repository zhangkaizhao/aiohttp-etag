import time
from pathlib import Path

import aiohttp_etag
import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_jinja2 import template

APP_PATH = Path(__file__).parent


def setup_jinja(app):
    templates_path = str(APP_PATH / 'templates')
    jinja2_loader = jinja2.FileSystemLoader(templates_path)
    aiohttp_jinja2.setup(app, loader=jinja2_loader)


@template('hello.html')
async def hello(request):
    text = 'Hello aiohttp!'
    return {'message': text}


@template('last_visit.html')
async def last_visit(request):
    text = 'Hello aiohttp!'
    last_visit = time.time()
    return {
        'message': text,
        'last_visit': last_visit,
    }


async def make_app():
    app = web.Application()
    setup_jinja(app)
    aiohttp_etag.setup(app)

    app.router.add_get('/', hello, name='hello')
    app.router.add_get('/last_visit', last_visit, name='last_visit')
    return app


web.run_app(make_app())
