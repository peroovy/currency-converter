from aiohttp.web import get
from aiohttp.web_routedef import RouteDef

from app.presentation.handlers import ConverterHandlers


def get_converter_routes(handlers: ConverterHandlers) -> list[RouteDef]:
    return [get("/convert", handlers.convert)]
