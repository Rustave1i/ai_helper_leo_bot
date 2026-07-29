import httpx

from app.config import OPENWEATHER_API_KEY
from app.exceptions import CityNotFoundError, WeatherError
from app.models.weather import Weather


class WeatherService:

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

    def find_city(self, query: str) -> str:
        params = {
                "q": query,
                "limit": 1,
                "appid": OPENWEATHER_API_KEY,
        }
    
        with httpx.Client(timeout=10) as client:
            response = client.get(
                self.GEOCODING_URL,
                params=params,
            )
    
        response.raise_for_status()
    
        cities = response.json()
    
        if not cities:
            raise CityNotFoundError(
                f"Город '{query}' не найден."
            )
    
        return cities[0]["name"]

    def get_weather(self, city: str) -> Weather:

        city = self.find_city(city)

        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "ru",
        }

        try:

            with httpx.Client(timeout=10) as client:
                response = client.get(
                    self.BASE_URL,
                    params=params,
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

        except httpx.TimeoutException as exc:
            raise WeatherError(
                "Сервис погоды не отвечает."
            ) from exc

        except httpx.HTTPError as exc:
            raise WeatherError(
                "Не удалось получить данные о погоде."
            ) from exc