from aiohttp.web_response import Response, json_response


def success_response() -> Response:
    return json_response(data={"msg": "Success"}, status=200)


def error_response(code: str, msg: str, status_code: int) -> Response:
    return json_response(data={"error": {"code": code, "msg": msg}}, status=status_code)
