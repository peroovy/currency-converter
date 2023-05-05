from aiohttp.web_response import Response, json_response


def success_response() -> Response:
    return json_response(data={"msg": "Success"}, status=200)
