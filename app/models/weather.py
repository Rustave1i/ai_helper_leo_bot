from dataclasses import dataclass


@dataclass(slots=True)
class Weather:
    city: str
    description: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float