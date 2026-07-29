class WeatherError(Exception):
    """Ошибка получения данных о погоде."""
    pass


class CityNotFoundError(WeatherError):
    """Город не найден."""
    pass