import json


def load_players():

    with open("data/players.json", "r") as file:
        players = json.load(file)

    return players