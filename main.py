import requests
import json

POKE_REST_API_BASE_URL = "https://pokeapi.co/api/v2/"
POKE_GRAPHQL_BASE_URL = "https://beta.pokeapi.co/graphql/v1beta"
# This is used due to an issue in the GraphQL API https://github.com/PokeAPI/pokeapi/issues/614#issuecomment-1422636938
SPRITE_BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master"
TARGETED_GAMES = ["red", "blue", "leafgreen", "white"]
HEIGHT_MULTIPLIER = 0.1
WEIGHT_MULTIPLIER = 0.1


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
            "name": pokemon["name"],
            "height": pokemon["height"],
            "weight": pokemon["weight"],
            "base_experience": pokemon["base_experience"],
            "order": pokemon["order"],
            "type": [_type["pokemon_v2_type"]["name"] for _type in pokemon["pokemon_v2_pokemontypes"]],
            "bmi": bmi,
            "default_front_sprite": sprites["front_default"].replace("/media", SPRITE_BASE_URL),
        }
        processed_pokemon.append(processed)
    return processed_pokemon


if __name__ == "__main__":
    # Inefficient and takes too long (commented out so it will not run)
    # pokemon_1 = get_all_pokemon_filter_by_game(game_names=TARGETED_GAMES)
    # with open("pokemon_restapi_raw.json", "w") as file:
    #     file.write(json.dumps(pokemon_1, indent=2))

    # Efficient, only relevant details
    pokemon_3 = get_pokemon_in_scope()
    with open("pokemon_gql_raw.json", "w") as file:
        file.write(json.dumps(pokemon_3, indent=2))

    processed_pokemon = process_pokemon_data(pokemon_3)
    with open("pokemon_gql_processed.json", "w") as file:
        file.write(json.dumps(processed_pokemon, indent=2))
