from app.services import weather_service

weather = weather_service.get_weather("Москва")

print(weather)