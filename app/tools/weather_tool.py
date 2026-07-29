from app.exceptions import CityNotFoundError, WeatherError
from app.services.weather_service import WeatherService
from app.tools.base_tool import BaseTool
from app.utils.city_extractor import CityExtractor

weather_service = WeatherService()
city_extractor = CityExtractor()


class WeatherTool(BaseTool):

    name = "weather"

    KEYWORDS = (
        "погода",
        "температура",
        "дождь",
        "снег",
        "ветер",
        "прогноз",
    )

    def can_handle(self, message: str) -> bool:
        text = message.lower()
        return any(word in text for word in self.KEYWORDS)

    def execute(self, message: str) -> str:

        city = city_extractor.extract(message)

        if city is None:
            city = "Москва"

        try:
            weather = weather_service.get_weather(city)

        except CityNotFoundError as e:
            return str(e)

        except WeatherError as e:
            return str(e)

        return (
            f"🌤 {weather.city}\n\n"
            f"🌡 Температура: {weather.temperature:.1f}°C\n"
            f"🤗 Ощущается как: {weather.feels_like:.1f}°C\n"
            f"☁ {weather.description}\n"
            f"💧 Влажность: {weather.humidity}%\n"
            f"💨 Ветер: {weather.wind_speed:.1f} м/с"
        )