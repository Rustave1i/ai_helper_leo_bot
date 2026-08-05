import httpx

from app.config import HTTP_TIMEOUT


class HttpFactory:
    """Фабрика HTTP-клиентов."""

    @staticmethod
    def create_async_client() -> httpx.AsyncClient:

        timeout = httpx.Timeout(
            connect=10.0,
            read=float(HTTP_TIMEOUT),
            write=10.0,
            pool=10.0,
        )

        limits = httpx.Limits(
            max_keepalive_connections=10,
            max_connections=20,
        )

        return httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=True,
            http2=True,
        )