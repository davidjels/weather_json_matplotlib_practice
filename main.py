# imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json

# Dictionary of cities and coordinates. Note: While there is an OpenWeather API endpoint for calling by city name,
# the free API only supports coordinates so only 3 cities have been chosen and their coordinates looked up.
locations = {
    'london': (51.5230, 0.0803),
    'birmingham': (53.483959, -2.244644),
    'manchester': (52.489471, -1.898575)
}

def get_user_input():
    '''
    :return: city (str): User's input choice from a list of available cities
    '''

    # always prompt the user for input if input isn't valid. Allow the user to run simple test by typing 'test'
    while True:
        user_input_string = input(
            f'Please type the name of the city you want to see the weather forecast for. Options: {[name for name in locations.keys()]}. \n Type "test" to run test data.')
        user_input_string = user_input_string.lower()

        if user_input_string in locations.keys() or user_input_string == "test":
            break
        print('\nOops!! Please choose a valid city from the provided options only!\n\n')

    return user_input_string

def get_fallback_data():
    print('There was an issue getting the data from the external source. Falling back to preloaded sample data...')
    sample_file = open('sample_data.json', )
    json_data = json.load(sample_file)
    return json_data

def get_data(user_input):
    ''' Calls the OpenWeather API for the city chosen by looking up that city's coordinates and getting the forecast for those coordinates.
    :param city (str): User's input choice of the city they want the forecast for.
    :return temp_dict (dictionary): A dictionary of  UNIX timestamps (keys) and temperatures in celsius (values)
        '''
    # parameters for the API Call
    api_key = '336b9d17037213d702842ea2dc6ae933'
    base_url = 'https://api.openweathermap.org/data/2.5/onecall'

    # Lookup the coordinates for the city chosen (note there is an endpoint for calling by city name but the free API only supports coordinates.)
    city_chosen = locations[user_input]
    lat = city_chosen[0]
    long = city_chosen[1]

    url_to_call = f'{base_url}?lat={lat}&lon={long}&exclude=current,daily,alerts,minutely&appid={api_key}'

    # Get response and convert to json
    try:
        response = requests.get(url_to_call)
    except:
        #If issue with API response (e.g. no internet) fallback to preloaded sample data
        json_data = get_fallback_data()
    else:
        #Validate the API response and fallback to preloaded sample data if necessary
        if response.status_code != 200:
            json_data = get_fallback_data()
        else:
            json_data = response.json()

    return json_data

def prep_data_dict(api_data):
    '''
    #Build up a dictionary of hours (datetimes) and temperatures at that hour over the next 48 hours.
    # Note: Hours are UNIX timestamps.
    :param api_data: A HTTP response from the OpenWeather API
    :return: A dictionary if timestamps and corresponding temperatures.
    '''
    temperature_dict = {}
    for hour in api_data['hourly']:
        timestamp = hour['dt']
        temperature = hour['temp'] - 273.15  # Convert Kelvin to Celsius
        temperature_dict[timestamp] = temperature

    return (temperature_dict)


def plot_results(temp_dict, city):
    '''
    :param temp_dict: A dictionory containing hourly measures in unix timestamp and the corresponding temperature values in celsius
    :param city: User's input choice from a list of available cities
    :return: A plot of the upcoming temperature values in the next 48 hours and their mean, min and max values.
    '''

    print('Generating plot...')

    # Convert dict to pandas series
    pandSeries = pd.Series(temp_dict).rename('Temperature')
    # Convert unix time to human readable time
    pandSeries.index = pd.to_datetime(pandSeries.index, unit='s')
    # Reformat datetimes to eb more user friendly
    pandSeries.index = pandSeries.index.strftime('%d-%b - %I %p')
    # Calculate the data min,max and mean
    avg = pandSeries.mean()
    minimum = pandSeries.min()
    maximum = pandSeries.max()

    # plotting
    plt.figure(figsize=(20, 8))
    plt.xticks(rotation=90)
    sns.lineplot(data=pandSeries, label='Temp')

    # plotting the statistics lines
    plt.axhline(minimum, color='g', label='Min Temp')
    plt.axhline(avg, color='orange', label='Average Temp')
    plt.axhline(maximum, color='r', label='Max Temp ')

    # general formatting
    plt.title(f'Forecasted temperature values for {city.title()} in the next 48 Hours')
    plt.xlabel('Time and Day')
    plt.ylabel('Temperature in Celsius')
    plt.legend()
    plt.tight_layout()
    print('Showing plot...')
    return plt.show()


if __name__ == '__main__':
    # Ask user for input
    user_input = get_user_input()

    if user_input == 'test':
        #Runs the program and plots a chart for a set of datetimes & temperatures with a known pattern
        #Plot created should be a flat/horizontal 20 celsius apart from the first and last datetimes at 10 celsius
        #To see if data is getting plotted as expected
        print('getting test data')
        test_file = open('test_data_1.json', )
        json_data = json.load(test_file)
    else:
        # Collect data
        json_data = get_data(user_input)

    # Prep data for plotting
    data_dict = prep_data_dict(json_data)
    # Display Results
    plot_results(data_dict, user_input)