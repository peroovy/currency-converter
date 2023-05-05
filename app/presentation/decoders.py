from json import JSONDecodeError

from aiohttp.abc import Request


async def get_json_body(request: Request) -> dict | list | None:
    try:
        return await request.json()
    except JSONDecodeError:
        return None
