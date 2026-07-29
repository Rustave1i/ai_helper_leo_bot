from app.utils.city_extractor import CityExtractor

extractor = CityExtractor()

tests = [
    "Какая погода в Москве?",
    "Погода в Сочи",
    "Что сейчас в Санкт-Петербурге?",
    "Температура в Ростове-на-Дону",
    "Погода",
]

for text in tests:
    print(f"{text} -> {extractor.extract(text)}")