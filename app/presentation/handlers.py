from aiohttp.abc import Request
from aiohttp.web_response import Response, json_response

from app.domain.entities import ConversionIn
from app.domain.services import Converter


class ConverterHandlers:
    def __init__(self, converter: Converter):
        self._converter = converter

    async def convert(self, request: Request) -> Response:
        conversion_in = ConversionIn(**request.query)

        conversion_out = await self._converter.convert(conversion_in)

        return json_response(text=conversion_out.json(), status=200)
