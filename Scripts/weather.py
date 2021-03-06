#!/usr/bin/python2.7

import re
import os
import json
import yaml
import forecastio
import datetime

def readConfiguration():
    # open the configuration file in read mode
    config_file = open('config.yml', 'r')
    # now load the yaml
    config = yaml.load(config_file)
    config_file.close()
    return config


def readAPI():
    # open the API file in read mode
    API_file = open('API', 'r')
    API = API_file.readline().rstrip()
    API_file.close()
    return API

def readWeather(config, API):
    # connect to forecast.io
    forecast = forecastio.load_forecast(API, config['weather']['latitude'], config['weather']['longitude'], units=config['weather']['units'])

    # get the current weather
    current = forecast.currently()
    # get the details fo the current weather
    data = dict()
    data['temperature'] = int(current.temperature)
    data['summary'] = current.summary
    data['icon'] = current.icon
    data['feel'] = int(current.apparentTemperature)
    data['wind'] = current.windSpeed
    data['humidity'] = current.humidity
    data['update_at'] = current.time

    # now lets get the daily forecast
    daily = forecast.daily()
    data['forecast_summery'] = daily.summary.encode('utf-8')
    # get day by day data
    day_index = 1 # with 1 being today
    for day in daily.data:
        data[str(day_index) + '_' + 'minTemp'] = day.temperatureMin
        data[str(day_index) + '_' + 'minTempAt'] = datetime.datetime.fromtimestamp(int(day.temperatureMinTime)).strftime('%H:%M')
        data[str(day_index) + '_' + 'maxTemp'] = day.temperatureMax
        data[str(day_index) + '_' + 'maxTempAt'] = datetime.datetime.fromtimestamp(int(day.temperatureMaxTime)).strftime('%H:%M')
        data[str(day_index) + '_' + 'icon'] = day.icon
        data[str(day_index) + '_' + 'summary'] = day.summary
        day_index = day_index + 1

    # get the units
    units = config['weather']['units']
    # put the unit specific details
    if units == 'si':
        data['temp_unit'] = 'C'
        data['speed_unit'] = 'm/s'
    elif units == 'ca':
        data['temp_unit'] = 'C'
        data['speed_unit'] = 'km/h'
    else:
        data['temp_unit'] = 'F'
        data['speed_unit'] = 'mph'

    return data


def writeWeather(data):
    # open the file for writing
    weather_file = open('/tmp/starter-conky/weather.tmp', 'w')
    # write the weather
    for key in data:
        weather_file.write(key + ':' + str(data[key]) + '\n')
    # close the file
    weather_file.close()


# read the configuration
config = readConfiguration()
API    = readAPI()

# read the weatther
data = readWeather(config, API)

# change the status
data['status'] = 'FILLED'

# write the weather
writeWeather(data)
