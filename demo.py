import requests
import json
import random

url = "http://localhost:8080/"


FOOD_COUNT = 20
LOCATION_COUNT = 15

foods = json.load(open("config/random-foods.json", "r"))
random.shuffle(foods)
locations = json.load(open("config/random-addresses.json", "r"))
random.shuffle(locations)

auth = {
    "username": "test_username1",
    "password": "test_password1",
    "email": "test_email1"
}


def initialize() -> None:

    DEFAULT_USER = {
        "username": "username",
        "password": "password",
        "email": "email"
    }
    requests.post(url + "add_user", params=DEFAULT_USER)
    for i in range(1, 11):
        auth = {
            "username": f"test_username{i}",
            "password": f"test_password{i}",
            "email": f"test_email{i}"
        }
        requests.post(url + "add_user", params=auth)
    print("Added users")

    # WRITE TEST CASES
    DEFAULT_LOCATION = {
        "address": "6560 Braddock Rd, Alexandria, VA 22312",
        "latitude": 38.817261,
        "longitude": -77.167343
    }
    requests.post(url + "add_location", params=DEFAULT_LOCATION | auth)

    for location in locations[:LOCATION_COUNT]:
        requests.post(url + "add_location", params=location | auth)
    print("Added locations")

    for food in foods[:FOOD_COUNT]:
        requests.post(url + "add_food",
                      params={"description": food, "location": 1} | auth)
    print("Added foods")


def update_random_location() -> None:

    food_id = random.randint(1, FOOD_COUNT + 1)

    _food = requests.get(url + f"get_food/{food_id}", params=auth).json()


    # fork food into 3 - 8 new locations
    num_of_locations = random.randint(3, 5)

    # sample n random locations
    locations = random.sample(range(1, LOCATION_COUNT + 1), num_of_locations)

    # add new foods to current location so I can update them
    for _ in range(num_of_locations - 1):
        requests.post(url + "add_food", params=_food | auth)

    _foods = requests.get(url + "get_foods", params=auth).json()["foods"]

    foods = [food_id] + [food["id"] for food in _foods[-(num_of_locations - 1):]]

    for food, location in zip(foods, locations):
        requests.post(url + f"update_food_location/{food}", params={"location": location} | auth)
    
    print(f"Forked food {food_id} into {num_of_locations} different locations")


def save_history() -> None:
    history = requests.get(url + "get_history", params=auth).json()["history"]

    for entry in history:
        entry["food"] = requests.get(
            url + "get_food/" + str(entry["food"]), params=auth).json()
        entry["source"] = requests.get(
            url + "get_location/" + str(entry["source"]), params=auth).json()
        entry["destination"] = requests.get(
            url + "get_location/" + str(entry["destination"]), params=auth).json()

    with open("history.json", "w") as f:
        json.dump(history, f)


def main() -> None:
    initialize()

    for _ in range(20):
        update_random_location()

    save_history()


if __name__ == "__main__":
    main()
