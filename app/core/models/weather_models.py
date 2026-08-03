from dataclasses import dataclass


@dataclass(slots=True)
class Weather:
    city: str
    temperature: float
    feels_like: float
    description: str
    humidity: int
    wind_speed: float