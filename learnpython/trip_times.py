import random

'''
Model the amount of time it takes to make a trip by car.

Args:
    segment_list = list of segments of the path.
        Each item in the list is a tuple of (length, speed_limit, number_lights)
        where length = an integer representing a number of miles
        speed_limit = an integer representing the speed limit on that track
        number_lights = the number of traffic lights on that stretch of road.
Returns:
    a float representing minutes it took to finish the trip.
'''
def timeForTrip(segment_list):
    total_time = 0
    for segment in segment_list:
        (length, speed, lights) = segment

        # x += 1 is an abbreviation for x = x + 1
        total_time += float(length)/(float(speed)/60)
        for i in range(lights):
            total_time += random.random()*2

    return total_time

getting_groceries_in_suburbs = [
    (2, 30, 5)]

city_commute = [
    (2, 25, 5),
    (10, 45, 15),
    (1, 10, 0)]

getting_into_the_city = [
    (5, 45, 5),
    (40, 60, 0),
    (5, 20, 15)]

long_trip = [
    (5, 30, 15),
    (400, 60, 0),
    (5, 45, 10)]

all_trips = [
    ("Groceries", getting_groceries_in_suburbs),
    ("Commute", city_commute),
    ("City", getting_into_the_city),
    ("Trip", long_trip)]

for trip_name, path in all_trips:
    print trip_name + " takes " + str(timeForTrip(path)) + " minutes."
