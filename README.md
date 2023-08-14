# gotta-process-em-all

This repository contains code and notes for pulling, and processing data form the PokéAPI.

## Scope for the tasks

Pokémon that appear in `red`, `blue`, `leafgreen` or `white` are in scope.

The following data is required:
- id
- name
- height
- weight
- base_experience
- order


## Pull data about Pokémon from specific games


After looking at the documentation for the API, I concluded that, unfortunately, it is not possible to fetch all Pokémon in a given game with a specific endpoint or query parameter or anything similar. I came up with the following approaches:

**Approach 1:** Fetch all Pokémon by paginating through the Pokémon endpoint, then filter the results using the field `game_indices.[].version.name`. Paginating through all Pokémon is not sufficient though, because the data returned are just names and url references to the actual data of a Pokémon. 

**Approach 2:** Fetch the game data and through relationships the Pokémon they contain. This requires chaining requests for the following resources: game > version_group > generation > pokemon_species > pokemon. Upon fetching and inspecting some of the data I determined that this approach will not work. Unfortunately Pokémon species != Pokémon. The species contain all the available varieties of it, however, it is not guaranteed that every variety appeared in the 4 given games, so another check needs to be performed to make sure the data is correct.

While exploring the endpoints of the Rest API I noticed that a GraphQL API is also available. Since the Rest API had no support for query parameters and filtering data I took a look since this sounded like something that would lend itself well to a GraphQL query.

**Approach 3:** Using the Graph API. With the help of the API explorer I put toghether a query that gives me the list of Pokémon with the desired fields within the scope. This is the most efficient way of obtaining the data from PokéAPI, because it puts the filtering duties on their end, reduces the room for error on my end (given the query is correct) and the size of the returned data is optimal, since I only get the fields I want.

After experimenting with approaches 1 and 3 I was able to fetch 667 Pokémon in the given games.

## Processing the data

There is an issue with the sprites in the Graph API. See https://github.com/PokeAPI/pokeapi/issues/614#issuecomment-1422636938