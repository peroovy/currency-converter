from aiohttp.web import Application, run_app
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Callable, Configuration, Factory, List, Singleton
from redis.asyncio.client import Redis

from app.config import BASE_CURRENCY_CODE, AppSettings, RedisSettings
from app.db.repositories import CurrencyRepository
from app.domain.services import Converter
from app.logging import setup_logging
from app.presentation.handlers import ConverterHandlers
from app.presentation.middlewares import process_error
from app.presentation.routes import get_converter_routes


class Container(DeclarativeContainer):
    app_settings = Configuration(pydantic_settings=[AppSettings()])

    redis_settings = Configuration(pydantic_settings=[RedisSettings()])
    redis_session = Singleton(
        Redis,
        host=redis_settings.host,
        port=redis_settings.port,
        password=redis_settings.password,
        decode_responses=True,
    )

    currency_repository = Factory(CurrencyRepository, session=redis_session, base_currency_code=BASE_CURRENCY_CODE)
    converter = Factory(Converter, currency_repository=currency_repository)

    handlers = Factory(ConverterHandlers, converter=converter)

    middlewares = List(Callable(process_error, debug=app_settings.debug))

    routes = Callable(get_converter_routes, handlers=handlers)


async def create_app() -> Application:
    container = Container()

    app = Application(middlewares=container.middlewares())
    app.add_routes(container.routes())

    setup_logging(container.app_settings.debug)

    return app
