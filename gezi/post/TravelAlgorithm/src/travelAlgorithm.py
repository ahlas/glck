from sys import argv

import numpy as np
from math import sqrt

from .io_helper import read_tsp, normalize
from .neuron import generate_network, get_neighborhood, get_route
from .distance import select_closest, euclidean_distance, route_distance
from .plot import plot_network, plot_route

import geocoder

#Rota Bulma fonksiyonu
def findRoute():

    myloc = geocoder.ip('me')
    print("My Location =",myloc.latlng)

    dosya = open("deneme.txt", "w")
    dosya.write("Merhaba Millet :)")
    dosya.close()

    problem = read_tsp("sehirBilgileri.tsp")

    locationFlag = False

    cityAndRoute = som(problem, 30,locationFlag)
    route = cityAndRoute[0]
    cityS = cityAndRoute[1]

    #Sıralanmis City List'i
    for a in range(len(cityS)):
        print("Cities=", a, " ", cityS.iloc[a]['city'])

    problem = problem.reindex(route)

    distance = route_distance(problem)

    print('Route found of length {}'.format(distance))

    return cityS


def som(problem, iterations, locationFlag, learning_rate=0.8):
    """Solve the TSP using a Self-Organizing Map."""
    while not locationFlag:
        # Obtain the normalized set of cities (w/ coord in [0,1])
        cities = problem.copy()

        print(cities)
        shortestCityIndex = findShortestCity(cities)

        cities[['x', 'y']] = normalize(cities[['x', 'y']])

        # The population size is 8 times the number of cities
        n = cities.shape[0] * 8

        # Generate an adequate network of neurons:
        network = generate_network(n)
        print('Network of {} neurons created. Starting the iterations:'.format(n))

        for i in range(iterations):
            if not i % 100:
                print('\t> Iteration {}/{}'.format(i, iterations), end="\r")
            # Choose a random city
            city = cities.sample(1)[['x', 'y']].values
            winner_idx = select_closest(network, city)
            # Generate a filter that applies changes to the winner's gaussian
            gaussian = get_neighborhood(winner_idx, n//10, network.shape[0])
            # Update the network's weights (closer to the city)
            network += gaussian[:,np.newaxis] * learning_rate * (city - network)
            # Decay the variables
            learning_rate = learning_rate * 0.99997
            n = n * 0.9997

            # Check for plotting interval

            # Check if any parameter has completely decayed.
            if n < 1:
                print('Radius has completely decayed, finishing execution',
                      'at {} iterations'.format(i))
                break
            if learning_rate < 0.001:
                print('Learning rate has completely decayed, finishing execution',
                      'at {} iterations'.format(i))
                break
        else:
            print('Completed {} iterations.'.format(iterations))

     #   plot_network(cities, network, name='diagrams/final.png')

        route = get_route(cities, network)

        cities.sort_values(by=['winner'],inplace =True)

        print("Shortest=", shortestCityIndex)
        ourLocationIndex = route.tolist()

        print("Len = ", len(ourLocationIndex))

        if (ourLocationIndex[0] == 0 and ourLocationIndex[1] == shortestCityIndex):
            break

     #   plot_route(cities, route, 'diagrams/route.png')

    return [route,cities]

def findShortestCity(cities):
    index = 999
    length = 9999
    arraySize = cities['x'].size

    for i in range(1,arraySize):
        temp = sqrt(abs(cities.iloc[0]['x'] - cities.iloc[i]['x'])**2 + (abs(cities.iloc[0]['y'] - cities.iloc[i]['y']))**2)
        if temp < length:
            print("Temp=", temp, " ==== Length=", length, " City=", cities.iloc[i]['city'], "  İ=", i)
            length = temp
            index = i

    return index