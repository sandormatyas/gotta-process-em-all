
import './App.css';
import {useEffect, useState} from "react"
import { Container, Grid } from "@mui/material"
import { DataGrid } from "@mui/x-data-grid"
import PokemonInspector from './components/PokemonInspector';

const App = () => {
  const [pokemon, setPokemon] = useState([])
  const [selectedPokemon, setSelectedPokemon] = useState(null)

  const handleSelect = (data) => {
    const pokeId = data.row.id
    setSelectedPokemon(pokemon.find((item) => {
      return item.id === pokeId
    }))
  }

  useEffect(()=>{
    fetch("pokemon_processed.json")
    .then((response)=>{
      return response.json()
    })
    .then((data) => {
      setPokemon(data)
    })
  }, [])

  const columns = [
    {field: "id", headerName: "ID"},
    {field: "name", headerName: "Name", minWidth: 100, flex: 1},
    {field: "type", headerName: "Type", minWidth: 100, flex: 1},
    {field: "height", headerName: "Height (dm)"},
    {field: "weight", headerName: "Weight (hg)"},
    {field: "bmi", headerName: "BMI"},
    {field: "base_experience", headerName: "Base Experience", minWidth: 150, flex: 1},
    {field: "order", headerName: "Order"}
  ]

  return (
    <Container className="App" maxWidth="xl">
      <Grid container padding={2} spacing={2}>
        <Grid item xs={8}>
          <DataGrid rows={pokemon}
          columns={columns}
          initialState={{pagination: { paginationModel: { pageSize: 10}}}}
          pageSizeOptions={[5]}
          onRowClick={handleSelect}>
          </DataGrid>
        </Grid>
        <Grid item xs={4}>
          <PokemonInspector pokemon={selectedPokemon}></PokemonInspector>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
