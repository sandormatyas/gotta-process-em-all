# gotta-process-em-all

This repository contains resources for a case study. There is code and notes for pulling, and processing data form the PokéAPI.

## Scope for the tasks

Pokémon that appear in `red`, `blue`, `leafgreen` or `white` are in scope.

The following fields are required:
- id
- name (titlecase)
- height
- weight
- base_experience
- order
- default_front sprite
- bmi (needs to be calculated)


## Pull data about Pokémon from specific games

After looking at the documentation for the API, I concluded that, unfortunately, it is not possible to fetch all Pokémon in a given game with a specific endpoint or query parameter or anything similar. I came up with the following approaches:

**Approach 1:** Fetch all Pokémon by paginating through the Pokémon endpoint, then filter the results using the field `game_indices.[].version.name`. Paginating through all Pokémon is not sufficient though, because the data returned are just names and url references to the actual data of a Pokémon. 

**Approach 2:** Fetch the game data and through relationships the Pokémon they contain. This requires chaining requests for the following resources: game > version_group > generation > pokemon_species > pokemon. Upon fetching and inspecting some of the data I determined that this approach will not work. Unfortunately Pokémon species != Pokémon. The species contain all the available varieties of it, however, it is not guaranteed that every variety appeared in the 4 given games, so another check needs to be performed to make sure the data is correct.

While exploring the endpoints of the Rest API I noticed that a GraphQL API is also available. Since the Rest API had no support for query parameters and filtering data I took a look since this sounded like something that would lend itself well to a GraphQL query.

**Approach 3:** Using the Graph API. With the help of the API explorer I put toghether a query that gives me the list of Pokémon with the desired fields within the scope. This is the most efficient way of obtaining the data from PokéAPI, because it puts the filtering duties on their end, reduces the room for error on my end (given the query is correct) and the size of the returned data is optimal, since I only get the fields I want.

After experimenting with approaches 1 and 3 I was able to fetch 667 Pokémon in the given games.

## Processing the data

There is an issue with the sprites in the Graph API. See https://github.com/PokeAPI/pokeapi/issues/614#issuecomment-1422636938

I decided to flatten the data and store records as json objects.

I dumped all records in to a json file named `pokemon_processed.json`. The data could be sorted into multiple files of course, but I think this depends on the use case. Depending on the purpose or the database they could be saved as independent json files, in batch by games. 

If the data is expected to be updated it should be considered as a factor in separating the records into files. If all the data is dumped into 1 file it represents the "state" of the Pokémon data in scope. This can be versioned and updated or just overwritten as needed. If the data is separated into files additional logic may be required to determine what files need to be updated to avoid unnecessary operations.

## Bonus Requirements
### Pseudonymize Pokémon data

First let's identify the fields that make the data indentifiable. One could argue that if the attributes like weight or height are static, then the combination of the fields could always be used to indenfy a Pokémon. For the sake of this excercise let's put this argument aside and treat Pokémon as they were individuals where their attributes are not traceable.

Fields with identifiable data in my opinion are: id, name and default_front_sprite. The latter because it contains the id.

I chose to apply symmetric encryption (Fernet) on the fields with identifiable data. I implemented a function for encrypting relevant fields and one for decrypting them.

Additionally the fields that idenfy the record (only within the data set) became very long now and they are not friendly for human eyes. This could become an issue if the use for the data is to produce a human readable report or study and records become hard to track.

To work around this I use Faker, a python library for fake data generation to generate human readable pseudonyms for the Pokémon. I store the mappings in a file, but this is not sensitive as it is just a mapping between the pseudonym and the encrypted value.

To see if the output of the decryption function is correct I put in print statements that compare the two lists, and also used `diff` which showed that the processed data matched the decrypted data.

### Continuous updates to investors

TODO