import requests
import json
import re
from imgcat import imgcat
from PIL import Image
from cryptography.fernet import Fernet
from os import getenv
from time import sleep
from faker import Faker
from copy import deepcopy

POKE_REST_API_BASE_URL = "https://pokeapi.co/api/v2/"
POKE_GRAPHQL_BASE_URL = "https://beta.pokeapi.co/graphql/v1beta"
# This is used due to an issue in the GraphQL API https://github.com/PokeAPI/pokeapi/issues/614#issuecomment-1422636938
SPRITE_BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master"
TARGETED_GAMES = ["red", "blue", "leafgreen", "white"]
HEIGHT_MULTIPLIER = 0.1
WEIGHT_MULTIPLIER = 0.1
fake = Faker()
Faker.seed(1234)


def get_all_pokemon_filter_by_game(page_size: int = 100, game_names: list = []) -> list[dict]:
    """This fn fetches all Pokémon details. Filterable by game appearance by providing `game_names`.

    Args:
        page_size (int, optional): Size for pagination. Defaults to 100.
        game_names (list, optional): List of games a Pokémon could appear in. Defaults to [].

    Returns:
        list[dict]: A list of dictionaries where each item is a Pokémon. 
    """
    pokemon_list = []
    url = POKE_REST_API_BASE_URL + f"pokemon/?limit={page_size}"
    while url:
        response = requests.get(url).json()
        for pokemon in response.get("results", []):
            pokemon_details = requests.get(pokemon.get("url")).json()
            game_appearances = [game_index["version"]["name"]
                                for game_index in pokemon_details["game_indices"]]
            if game_names and any(game in game_appearances for game in game_names):
                pokemon_list.append(pokemon_details)
        url = response.get("next")

    return pokemon_list


def get_pokemon_in_scope() -> list[dict]:
    """Returns Pokémon that appear games: 'red', 'blue', 'leafgreen' and 'white'.

    Returns:
        list[dict]: List where each item contains the data of a Pokémon.
    """

    graph_query = """
    query getPokemonFromCertainGames {
        pokemon_v2_pokemon(where: 
            {pokemon_v2_pokemongameindices: 
                {pokemon_v2_version: 
                    {_or: [
                        {name: {_eq: "red"}}, 
                        {name: {_eq: "blue"}}, 
                        {name: {_eq: "leafgreen"}}, 
                        {name: {_eq: "white"}}]
                    }
                }
            }
        ) 
        {
            id
            height
            name
            order
            base_experience
            weight
            pokemon_v2_pokemontypes {
                slot
                pokemon_v2_type {
                    name
                }
            }
            pokemon_v2_pokemonsprites {
                sprites
            }
        }
    }
    """

    payload = {
        "operationName": "getPokemonFromCertainGames",
        "query": graph_query
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(POKE_GRAPHQL_BASE_URL,
                             data=json.dumps(payload),
                             headers=headers)
    response.raise_for_status()

    return response.json()["data"]["pokemon_v2_pokemon"]


def process_pokemon_data(pokemon_data: list) -> list[dict]:
    """Processes the raw records from PokéAPI based on given requirements.

    Args:
        pokemon_data (list): List of Pokémon records.

    Returns:
        list[dict]: Processed Pokémon records in a list.
    """
    processed_pokemon = []
    for pokemon in pokemon_data:
        bmi = round(pokemon["weight"] * WEIGHT_MULTIPLIER /
                    (pokemon["height"] * HEIGHT_MULTIPLIER)**2, 2)
        sprites = json.loads(
            pokemon["pokemon_v2_pokemonsprites"].pop()["sprites"])
        processed = {
            "id": pokemon["id"],
            "name": pokemon["name"].title(),
            "height": pokemon["height"],
            "weight": pokemon["weight"],
            "base_experience": pokemon["base_experience"],
            "order": pokemon["order"],
            "type": [_type["pokemon_v2_type"]["name"] for _type in pokemon["pokemon_v2_pokemontypes"]],
            "bmi": bmi,
            "front_default_sprite": sprites["front_default"].replace("/media", SPRITE_BASE_URL),
        }
        processed_pokemon.append(processed)
    return processed_pokemon


def encrypt_pii(pokemon_data: list[dict]) -> list[dict]:
    """Encrypts fields with PII in processed Pokémon data.

    Args:
        pokemon_data (list[dict]): Processed Pokémon data. Output of `process_pokemon_data()`.

    Returns:
        list[dict]: Data with `id`, `name` and `front_default_sprite` fields encrypted.
    """
    data = deepcopy(pokemon_data)
    key = getenv("FERNET_KEY")
    if not key:
        key = Fernet.generate_key()
        with open(".env", "+a") as envfile:
            envfile.write(f"FERNET_KEY={str(key, encoding='utf-8')}")
    else:
        # If key is in env, needs to be cast to bytes
        key = bytes(key, encoding="utf-8")

    f = Fernet(key)

    for pokemon in data:
        pokemon["id"] = str(
            f.encrypt(bytes(str(pokemon["id"]), encoding="utf-8")), encoding="utf-8")
        pokemon["name"] = str(
            f.encrypt(bytes(pokemon["name"], encoding="utf-8")), encoding="utf-8")
        pokemon["front_default_sprite"] = str(
            f.encrypt(bytes(pokemon["front_default_sprite"], encoding="utf-8")), encoding="utf-8")
    return data


def decrypt_pii(encrypted_data: list[dict], fernet_key: bytes | None = None) -> list[dict]:
    """Reverses the output of `encrypt_pii()`.

    Args:
        encrypted_data (list[dict]): Data output by `encrpyt_pii()`.
        fernet_key (bytes | None, optional): Fernet key used in encryption. Can also be in Environment as `FERNET_KEY`. Defaults to None.

    Raises:
        ValueError: fernet_key is not provided and not in environment.

    Returns:
        list[dict]: Original data before encryption.
    """
    data = deepcopy(encrypted_data)
    if not fernet_key:
        key = getenv("FERNET_KEY")
        if not key:
            raise ValueError("Missing argument `fernet_key`.")
        else:
            key = bytes(key, encoding="utf-8")

    f = Fernet(key)
    human_readable_re_pattern = r"Pocket Monster [0-9]{6}"

    for pokemon in data:
        pokemon["id"] = int(f.decrypt(bytes(pokemon["id"], encoding="utf-8")))
        pokemon_name = pokemon["name"]
        if re.match(human_readable_re_pattern, pokemon_name):
            pokemon_name = get_real_name_by_pseudonym(pokemon["name"])
        pokemon["name"] = str(
            f.decrypt(bytes(pokemon_name, encoding="utf-8")), encoding="utf-8")
        pokemon["front_default_sprite"] = str(f.decrypt(
            bytes(pokemon["front_default_sprite"], encoding="utf-8")), encoding="utf-8")
    return data


def pseudonymise_data(pokemon_data: list) -> list[dict]:
    """Generates pseudonyms for Pokémon and removes other PII fields.

    Args:
        pokemon_data (list): Processed Pokémon data. Encrypted or otherwise.

    Returns:
        list[dict]: Pseudonymised data.
    """
    data = deepcopy(pokemon_data)
    name_lookup = {}
    for idx, pokemon in enumerate(data):
        while True:
            name = fake.numerify(text="Pocket Monster ######")
            if name not in name_lookup:
                break

        if idx < 20:
            display_monster(pokemon, f"{pokemon['name']} > {name}")
            sleep(0.4)

        name_lookup[name] = pokemon["name"]
        pokemon["name"] = name

        del pokemon["id"]
        del pokemon["front_default_sprite"]

    with open("data/pseudonym_name_lookup.json", "w") as file:
        file.write(json.dumps(name_lookup))

    return data


def display_monster(pokemon, display_text):
    resp = requests.get(pokemon["front_default_sprite"], stream=True)
    img = Image.open(resp.raw)
    print(display_text)
    imgcat(img, height=10)


def get_real_name_by_pseudonym(hr_name: str) -> str:
    """Gets the real name of Pokémon.

    Args:
        hr_name (str): The pseudonym on the record.

    Returns:
        str: Real name.
    """
    with open("data/pseudonym_name_lookup.json", "r") as lookup_file:
        name_lookup = json.loads(lookup_file.read())
        return name_lookup.get(hr_name)


if __name__ == "__main__":
    # Inefficient and takes too long (commented out so it will not run)
    # pokemon_1 = get_all_pokemon_filter_by_game(game_names=TARGETED_GAMES)
    # with open("data/pokemon_restapi_raw.json", "w") as file:
    #     file.write(json.dumps(pokemon_1))

    # Efficient, only relevant details
    pokemon_3 = get_pokemon_in_scope()
    with open("data/pokemon_gql_raw.json", "w") as file:
        file.write(json.dumps(pokemon_3, indent=2))

    processed_pokemon = process_pokemon_data(pokemon_3)
    with open("data/pokemon_processed.json", "w") as file:
        file.write(json.dumps(processed_pokemon))

    encrypted_data = encrypt_pii(processed_pokemon)
    with open("data/pokemon_encrypted.json", "w") as file:
        file.write(json.dumps(encrypted_data, indent=2))

    decrypted_data = decrypt_pii(encrypted_data)
    with open("data/pokemon_decrypted.json", "w") as file:
        file.write(json.dumps(decrypted_data, indent=2))
    print(
        f"Data match after decryption: {decrypted_data == processed_pokemon}")

    pseudonym_data = pseudonymise_data(processed_pokemon)
    with open("data/pokemon_pseudonymised.json", "w") as file:
        file.write(json.dumps(pseudonym_data, indent=2))
