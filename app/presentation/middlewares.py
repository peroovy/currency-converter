from typing import Callable

from aiohttp.abc import Request
from aiohttp.web import middleware
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_response import Response, json_response
from pydantic import ValidationError

from app.errors import APIError


@middleware
async def process_error(request: Request, handler: Callable) -> Response:
    try:
        return await handler(request)

    except ValidationError as error:
        return json_response(text=error.json(), status=422)

    except APIError as error:
        return json_response(data=error.dict(), status=error.status_code)

    except HTTPNotFound:
        return json_response(data={"msg": "Not found resource"}, status=404)

    except Exception:
        return json_response(data={"msg": "Internal Server Error"}, status=500)
