from aiohttp.abc import Request
from aiohttp.web_response import Response, json_response

from app.domain.entities import ConversionIn, UpdatingIn, UpdatingOptions
from app.domain.services import Converter
from app.presentation.decoders import get_json_body
from app.presentation.responses import success_response


class ConverterHandlers:
    def __init__(self, converter: Converter):
        self._converter = converter

    async def convert(self, request: Request) -> Response:
        conversion_in = ConversionIn(**request.query)

        conversion_out = await self._converter.convert(conversion_in)

        return json_response(text=conversion_out.json(), status=200)

    async def update(self, request: Request) -> Response:
        params = UpdatingOptions(**request.query)
        body = UpdatingIn(currencies=await get_json_body(request))

        await self._converter.update(body, params)

        return success_response()
