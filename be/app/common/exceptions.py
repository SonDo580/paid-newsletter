from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Optional, Any
from loguru import logger

from app.schemas.error import ErrResBody


def _get_content(msg: str, detail: Optional[Any] = None) -> dict:
    return ErrResBody(message=msg, detail=detail).model_dump(exclude_none=True)


async def _validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    detail = exc.errors()
    err_msgs: list[str] = []
    for err in detail:
        location = ".".join(str(x) for x in err["loc"])
        msg = err["msg"]
        err_msgs.append(f"[{location}] {msg}")
    combined_msg = "; ".join(err_msgs)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=_get_content(msg=combined_msg, detail=detail),
    )


async def _http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_get_content(msg=exc.detail),
    )


async def _generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_get_content(msg="Internal Server Error"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _generic_exception_handler)
