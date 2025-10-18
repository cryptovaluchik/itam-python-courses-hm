# pip install loguru requests
import time
from typing import Awaitable, Callable
from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel
from loguru import logger

from utils.edit_link import insert_https_protocol
from services.link_service import LinkService
from utils.check_url import is_valid_link

logger.add("logs/app.log", rotation="1 hour", level="DEBUG")

def create_app() -> FastAPI:
    app = FastAPI()
    short_link_service = LinkService()

    class PutLink(BaseModel):
        link: str

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Логирует все HTTPException, включая сам запрос и тело запроса.
        """
        try:
            # Получаем тело запроса
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8') if body_bytes else "<пустое тело>"
        except Exception as e:
            body_str = f"<не удалось прочитать тело: {e}>"

        logger.error(
            "🚨 HTTPException {status} | {detail}\n"
            "→ Метод: {method}\n"
            "→ Путь: {url}\n"
            "→ Заголовки: {headers}\n"
            "→ Тело запроса: {body}",
            status=exc.status_code,
            detail=exc.detail,
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            body=body_str
        )

        return Response(
            content=f"Ошибка {exc.status_code}: {exc.detail}",
            status_code=exc.status_code,
            media_type="text/plain"
        )


    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Мидлварь принимаем на вход request (сам запрос), call_next - функция, что возвращает ответ
        #  с ответом мы можем проводить множество операций, например, добавлять хедеры, логировать запросы и тд

        
        start = time.time()
        
        response = await call_next(request)

        # elapsed_ms = round((time.time() - t0) * 1000, 2)
        elapsed_ms = (time.time() - start) * 1000
        response.headers["X-Latency"] = f"{elapsed_ms:.2f}"
        logger.debug("{} {} done in {}ms", request.method, request.scope["route"].path, elapsed_ms)
        
        return response

    def _service_link_to_real(short_link: str) -> str:
        return f"http://localhost:8000/{short_link}"

    @app.post("/link")
    def create_link(put_link_request: PutLink) -> PutLink:
        modified_link = insert_https_protocol(put_link_request.link)
        if is_valid_link(link=modified_link):
            short_link = short_link_service.create_link(modified_link)
            return PutLink(link=_service_link_to_real(short_link))

        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Link invalid:(")

    @app.get("/{link}")
    def get_link(link: str) -> Response:
        real_link = short_link_service.get_real_link(link)

        if real_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found:(")

        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY, headers={"Location": real_link})

    return app
