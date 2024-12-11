# Импортируем библиотеки
from flask import Flask, render_template, jsonify, request
import requests

# API-ключ
apiKey = 'SnUebAQAWnp7j27BG5FUzrGKLJKo7faS'

# Получаем locationKey  
def get_locationKey(city):
    params = {
        "apikey": apiKey,
        "q": city
    }
    data = requests.get('http://dataservice.accuweather.com/locations/v1/cities/search', params=params).json()
    if data:
        return data[0]["Key"]
    else:
        print("Город не найден.")
        return None


# Сохраняем ключевые парметры прогноза погоды
def get_weatherInfo(locationKey):
    params = {
        "apikey": apiKey,
        "details": True,
        "metric": True,
        "languages": "ru-RU"
    }
    data = requests.get(f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{locationKey}', params=params).json()
    weatherInfo = {
        'Temperature': (float(data['DailyForecasts'][0]['Temperature']['Minimum']['Value']) + float(data['DailyForecasts'][0]['Temperature']['Maximum']['Value'])) / 2,
        'Humidity': float(data['DailyForecasts'][0]['Day']['RelativeHumidity']['Average']),
        'Speed': float(data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']),
        'RainProbability': float(data['DailyForecasts'][0]['Day']['RainProbability'])
        }
    return weatherInfo

#def get_weatherInfo(apiKey, locationKey):
#    params = {
#        "apikey": apiKey,
#        "details": True,
#        "metric": True
#    }
#    return requests.get(f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{locationKey}', params=params).json()
#
#print(get_weatherInfo('dM0pZhdzjLlvNdVXIjacwVtOaU0tw7zG', "294021"))



# Оцена погодных услвоий
def weather_assessment(weatherInfo):
    if (weatherInfo['Temperature'] < 0 or weatherInfo['Temperature'] > 35 or weatherInfo['Speed'] > 50 or weatherInfo['Humidity'] > 60 or weatherInfo['Humidity'] < 40 or weatherInfo['RainProbability'] > 70):
        return 'Погода неблагоприятная'
    else:
        return 'Погода благоприятная'

# Веб-интерфейс
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def weather_service():
    if request.method == 'POST':
        start_city = request.form.get('start').strip()
        end_city = request.form.get('end').strip()

        if not start_city or not end_city:
            return render_template('index.html', error="Пожалуйста, введите названия обоих городов.")

        start_locationKey = get_locationKey(start_city)
        end_locationKey = get_locationKey(end_city)

        if not start_locationKey:
            return render_template('index.html', error=f"Упс. Неверно введён город: {start_city}.")
        if not end_locationKey:
            return render_template('index.html', error=f"Упс. Неверно введён город: {end_city}.")

        try:
            start_data = get_weatherInfo(start_locationKey)
            start_assessment = weather_assessment(start_data)
            end_data = get_weatherInfo(end_locationKey)
            end_assessment = weather_assessment(end_data)
        except requests.exceptions.RequestException:
            return render_template('index.html', error="Ошибка подключения к серверу. Попробуйте позже.")

        return render_template(
            'result.html',
            start_city=start_city,
            end_city=end_city,
            start_data=start_data,
            end_data=end_data,
            start_assessment=start_assessment,
            end_assessment=end_assessment
        )
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)