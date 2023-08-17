import {
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Typography,
  List,
} from "@mui/material";
import {
  FitnessCenter,
  Straighten,
  Scale,
  School,
  LowPriority,
} from "@mui/icons-material";
import StatItem from "./StatItem";
import React from "react";

const PokemonInspector = (props) => {
  const pokemon = props.pokemon;

  if (pokemon) {
    const stats = [
      {
        name: "Height (dm)",
        value: pokemon.height,
        icon: <Straighten />,
      },
      {
        name: "Weight (hg)",
        value: pokemon.weight,
        icon: <FitnessCenter />,
      },
      { name: "BMI", value: pokemon.bmi, icon: <Scale /> },
      {
        name: "Base experience",
        value: pokemon.base_experience,
        icon: <School />,
      },
      { name: "Order", value: pokemon.order, icon: <LowPriority /> },
    ];

    return (
      <Card sx={{ height: "100%" }}>
        <CardActionArea>
          <CardMedia
            component="img"
            image={pokemon.default_front_sprite}
            sx={{ width: 200, margin: "auto" }}
            alt={pokemon.name}
          ></CardMedia>
          <CardContent>
            <Typography variant="h2">{pokemon.name}</Typography>
            <Typography variant="h5">
              {pokemon.type.join(", ")}
            </Typography>
            <List dense={false}>
              {stats.map((stat) => {
                return (
                  <StatItem
                    icon={stat.icon}
                    statName={stat.name}
                    statValue={stat.value}
                  ></StatItem>
                );
              })}
            </List>
          </CardContent>
        </CardActionArea>
      </Card>
    );
  } else {
    return (
      <Card sx={{ height: "100%" }}>
        <CardContent>
          <Typography variant="h2">
            Select a Pokémon to inspect it
          </Typography>
        </CardContent>
      </Card>
    );
  }
};

export default PokemonInspector;
