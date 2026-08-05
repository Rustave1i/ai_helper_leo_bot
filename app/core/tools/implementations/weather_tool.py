from app.core.tools.base_tool import BaseTool
from app.core.tools.models import (
    ToolDefinition,
    ToolResult,
)
from app.exceptions import (
    CityNotFoundError,
    WeatherError,
)
from app.services.weather_service import WeatherService


class WeatherTool(BaseTool):
    """Инструмент получения текущей погоды."""

    def __init__(
        self,
        weather_service: WeatherService,
    ) -> None:

        self._weather_service = weather_service

    @property
    def definition(
        self,
    ) -> ToolDefinition:

        return ToolDefinition(
            name="weather",
            description=(
                "Возвращает текущую погоду "
                "в указанном городе."
            ),
            parameters={
                "city": {
                    "type": "string",
                    "description": "Название города",
                },
            },
        )

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:

        city = kwargs.get(
            "city",
            "Москва",
        )

        try:

            weather = await self._weather_service.get_weather(
                city
            )

        except (
            CityNotFoundError,
            WeatherError,
        ) as ex:

            return ToolResult(
                success=False,
                content=str(ex),
            )

        return ToolResult(
            success=True,
            content=(
                f"🌤 {weather.city}\n\n"
                f"🌡 Температура: {weather.temperature:.1f}°C\n"
                f"🤗 Ощущается как: {weather.feels_like:.1f}°C\n"
                f"☁ {weather.description}\n"
                f"💧 Влажность: {weather.humidity}%\n"
                f"💨 Ветер: {weather.wind_speed:.1f} м/с"
            ),
        )