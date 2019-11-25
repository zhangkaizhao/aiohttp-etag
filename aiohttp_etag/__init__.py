import hashlib
import re
from typing import (
    Awaitable,
    Callable,
    Optional,
)

from aiohttp import web

__version__ = '0.0.1'


@web.middleware
async def etag_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.Response]]):
    response = await handler(request)

    if not request.method == 'GET':
        return response

    if response.chunked:
        return response

    set_etag_header(response)

    if should_return_304_with_etag(request, response):
        response.set_status(304)
        response.body = None
        return response

    return response


def setup(app):
    """Setup the library in aiohttp fashion."""
    app.middlewares.append(etag_middleware)


def should_return_304_with_etag(request, response) -> bool:
    """Returns True if the headers indicate that we should return 304."""
    # If client sent If-None-Match, use it, ignore If-Modified-Since
    if request.headers.get("If-None-Match"):
        return check_etag_header(request, response)

    # No need to check the If-Modified-Since with the Last-Modified because
    # aiohttp.web already does that.

    return False


def compute_etag(response) -> Optional[str]:
    """Computes the etag header to be used for this response.

    By default uses a hash of the content written so far.
    """
    if hasattr(response, 'body'):
        # The aiohttp.web.StreamResponse does not have ``body`` attribute.
        body = response.body

        hasher = hashlib.sha1()
        hasher.update(body)

        return '"%s"' % hasher.hexdigest()

    return None


def set_etag_header(response) -> None:
    """Sets the response's Etag header using ``compute_etag()``.

    Note: no header will be set if ``compute_etag()`` returns ``None``.
    """
    etag = compute_etag(response)
    if etag is not None:
        response.headers["Etag"] = etag


def check_etag_header(request, response) -> bool:
    """Checks the ``Etag`` header against requests's ``If-None-Match``.

    Returns ``True`` if the request's Etag matches and a 304 should be
    returned. For example::

        set_etag_header(response)
        if check_etag_header(request, response):
            response.set_status(304)
            response.body = None
            return response

    This method may be called earlier for applications that already call
    `compute_etag` and want to do an early check for ``If-None-Match``
    before completing the request.  The ``Etag`` header should be set
    (perhaps with `set_etag_header`) before calling this method.
    """
    computed_etag = response.headers.get("Etag", "")
    # Find all weak and strong etag values from If-None-Match header
    # because RFC 7232 allows multiple etag values in a single header.
    etags = re.findall(
        r'\*|(?:W/)?"[^"]*"', request.headers.get("If-None-Match", "")
    )
    if not computed_etag or not etags:
        return False

    match = False
    if etags[0] == "*":
        match = True
    else:
        # Use a weak comparison when comparing entity-tags.
        def val(x: str) -> str:
            return x[2:] if x.startswith("W/") else x

        for etag in etags:
            if val(etag) == val(computed_etag):
                match = True
                break
    return match
