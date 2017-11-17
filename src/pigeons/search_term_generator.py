"""Generates funny terms to search for, like "nice pigeon"."""
from random import choice

NOUNS = (
    "pigeon",
    "pigeons",
    "domestic pigeon",
    "homing pigeon",
    "feral pigeon",
)

ADJECTIVES = (
    "",
    "nice",
    "pretty",
    "lovely",
    "elegant",
    "real",
    "flying",
    "eating",
)

def generate_pigeon_search_term():
    """Returns a random pigeon search term"""
    pigeon_term = "{} {}".format(choice(ADJECTIVES), choice(NOUNS)).strip()
    return pigeon_term

if __name__ == "__main__":
    print(generate_pigeon_search_term())
