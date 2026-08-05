import httpx

from app.config import (
    HTTP_RETRIES,
    HTTP_RETRY_DELAY,
    OPENWEATHER_API_KEY,
)
from app.core.infrastructure import RetryPolicy
from app.exceptions import (
    CityNotFoundError,
    WeatherError,
)
from app.core.models import Weather


class WeatherService:
    """Сервис получения данных о погоде."""

    BASE_URL = (
        "https://api.openweathermap.org/data/2.5/weather"
    )

    GEOCODING_URL = (
        "https://api.openweathermap.org/geo/1.0/direct"
    )

    def __init__(self) -> None:

        self._client = httpx.AsyncClient(
            timeout=10,
        )

        self._retry = RetryPolicy(
            retries=HTTP_RETRIES,
            delay=HTTP_RETRY_DELAY,
        )

    async def find_city(
        self,
        query: str,
    ) -> str:

        async def request():

            response = await self._client.get(
                self.GEOCODING_URL,
                params={
                    "q": query,
                    "limit": 1,
                    "appid": OPENWEATHER_API_KEY,
                },
            )

            response.raise_for_status()

            cities = response.json()

            if not cities:

                raise CityNotFoundError(
                    f"Город '{query}' не найден."
                )

            return cities[0]["name"]

        return await self._retry.execute(
            request,
            retry_on=(
                httpx.TimeoutException,
                httpx.NetworkError,
            ),
        )

    async def get_weather(
        self,
        city: str,
    ) -> Weather:

        city = await self.find_city(
            city
        )

        async def request():

            response = await self._client.get(
                self.BASE_URL,
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "lang": "ru",
                },
            )

            if response.status_code == 404:

                raise CityNotFoundError(
                    f"Город '{city}' не найден."
                )

            response.raise_for_status()

            data = response.json()

            return Weather(
                city=data["name"],
                description=data["weather"][0]["description"].capitalize(),
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                wind_speed=data["wind"]["speed"],
            )

        try:

            return await self._retry.execute(
                request,
                retry_on=(
                    httpx.TimeoutException,
                    httpx.NetworkError,
                ),
            )

        except httpx.TimeoutException as ex:

            raise WeatherError(
                "Сервис погоды не отвечает."
            ) from ex

        except httpx.HTTPError as ex:

            raise WeatherError(
                "Не удалось получить данные о погоде."
            ) from ex

    async def close(
        self,
    ) -> None:

        await self._client.aclose()