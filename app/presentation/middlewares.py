from typing import Callable

from aiohttp.abc import Request
from aiohttp.web import middleware
from aiohttp.web_exceptions import HTTPException
from aiohttp.web_response import Response, json_response
from pydantic import ValidationError

from app.errors import APIError
from app.presentation.responses import error_response


def process_error(debug: bool) -> Callable:
    @middleware
    async def middleware_(request: Request, handler: Callable) -> Response:
        try:
            return await handler(request)

        except ValidationError as error:
            return json_response(text=error.json(), status=422)

        except APIError as error:
            return error_response(code=error.__class__.__name__, msg=error.message, status_code=error.status_code)

        except HTTPException as exc:
            return error_response(code=exc.__class__.__name__, msg=str(exc), status_code=exc.status_code)

        except Exception as exc:
            if debug:
                raise exc

            return error_response(code="ServerError", msg="Internal Server Error", status_code=500)

    return middleware_
