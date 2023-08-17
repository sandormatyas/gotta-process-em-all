import { Card, CardActionArea, CardContent, CardMedia, Typography, List, ListItem, ListItemAvatar, Avatar, ListItemText, Grid } from '@mui/material'
import {FitnessCenter} from "@mui/icons-material"
import React from 'react'

const PokemonInspector = (props) => {
  const pokemon = props.pokemon
  
  if (pokemon) {
    const stats = {
      "Height": pokemon.height,
      "Weight": pokemon.weight,
      "BMI": pokemon.bmi,
      "Base experience": pokemon.base_experience,
      "Order": pokemon.order
    }

    return (
      <Card sx={{height: "100%"}}>
        <CardActionArea>
          <CardMedia
          component="img"
          image={pokemon.default_front_sprite}
          sx={{width: 200, margin:"auto"}}
          alt={pokemon.name}>
          </CardMedia>
          <CardContent>
            <Typography variant='h2'>
              {pokemon.name}
            </Typography>
            <Typography variant='h5'>
              {pokemon.type.join(", ")}
            </Typography>
            <List dense={false}>
            {Object.keys(stats).map((statName)=>{
              return (<ListItem key={statName}>
                <ListItemAvatar>
                  <Avatar>
                    <FitnessCenter></FitnessCenter>
                  </Avatar>
                </ListItemAvatar>
                <ListItemText>
                  <Grid container spacing={2} direction="row" justifyContent="space-between">
                    <Grid item xs={6}>
                      <Typography>{statName}:</Typography>
                    </Grid>
                    <Grid item xs={2}>
                      <Typography align="right">{stats[statName]}</Typography>
                    </Grid>
                  </Grid>
                </ListItemText>
                </ListItem>)
            })}
            </List>
          </CardContent>
        </CardActionArea>
      </Card>
    )
  } else {
    return (
      <Card>
        <CardContent>
          <Typography variant='h2'>
            Select a Pokémon to inspect it
          </Typography>
        </CardContent>
      </Card>
    )
  }
}

export default PokemonInspector