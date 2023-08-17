import "./App.css";
import { Fragment, useEffect, useState } from "react";
import { Container, Grid, Typography } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import {
  Pie,
  PieChart,
  Cell,
  Tooltip,
  BarChart,
  CartesianGrid,
  YAxis,
  XAxis,
  Legend,
  Bar,
} from "recharts";
import PokemonInspector from "./components/PokemonInspector";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];
const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
  index,
}) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor={x > cx ? "start" : "end"}
      dominantBaseline="central"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

const App = () => {
  const [pokemon, setPokemon] = useState([]);
  const [selectedPokemon, setSelectedPokemon] = useState(null);
  const [bmiBreakdown, setBmiBreakdown] = useState([]);
  const [pokemonByHeight, setPokemonByHeight] = useState([]);

  const handleSelect = (data) => {
    const pokeId = data.row.id;
    setSelectedPokemon(
      pokemon.find((item) => {
        return item.id === pokeId;
      })
    );
  };

  useEffect(() => {
    fetch("pokemon_processed.json")
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        setPokemon(data);
        return data;
      })
      .then((data) => {
        setBmiBreakdown([
          {
            name: "Underweight",
            value: data.filter((item) => {
              return item.bmi < 18.5;
            }).length,
          },
          {
            name: "Healthy weight",
            value: data.filter((item) => {
              return item.bmi >= 18.5 && item.bmi < 25;
            }).length,
          },
          {
            name: "Overweight",
            value: data.filter((item) => {
              return item.bmi >= 25 && item.bmi < 30;
            }).length,
          },
          {
            name: "Obese",
            value: data.filter((item) => {
              return item.bmi >= 30;
            }).length,
          },
        ]);
        return data;
      })
      .then((data) => {
        const dataCopy = [...data];
        setPokemonByHeight(
          dataCopy.sort((a, b) => {
            return b.height - a.height;
          })
        );
      });
  }, []);

  const columns = [
    { field: "id", headerName: "ID" },
    { field: "name", headerName: "Name", minWidth: 100, flex: 1 },
    { field: "type", headerName: "Type", minWidth: 100, flex: 1 },
    { field: "height", headerName: "Height (dm)" },
    { field: "weight", headerName: "Weight (hg)" },
    { field: "bmi", headerName: "BMI" },
    {
      field: "base_experience",
      headerName: "Base Experience",
      minWidth: 150,
      flex: 1,
    },
    { field: "order", headerName: "Order" },
  ];

  return (
    <Container className="App" maxWidth="xl">
      <Grid container padding={2} spacing={2}>
        <Grid item xs={8}>
          <DataGrid
            rows={pokemon}
            columns={columns}
            initialState={{
              pagination: { paginationModel: { pageSize: 10 } },
            }}
            pageSizeOptions={[10]}
            onRowClick={handleSelect}
          ></DataGrid>
        </Grid>
        <Grid item xs={4}>
          <PokemonInspector
            pokemon={selectedPokemon}
          ></PokemonInspector>
        </Grid>
        <Grid
          container
          item
          xs={6}
          direction="column"
          alignItems="center"
          justifyContent="center"
        >
          <Grid item>
            <Typography variant="h2">
              BMI breakdown of Pokémon
            </Typography>
          </Grid>
          <Grid item>
            <PieChart width={560} height={560}>
              <Tooltip active={true}></Tooltip>
              <Pie
                data={bmiBreakdown}
                innerRadius={50}
                label={renderCustomizedLabel}
                labelLine={false}
              >
                {bmiBreakdown.map((bmi, idx) => {
                  return (
                    <Fragment key={bmi.name}>
                      <Cell fill={COLORS[idx]}></Cell>
                    </Fragment>
                  );
                })}
              </Pie>
            </PieChart>
          </Grid>
        </Grid>
        <Grid
          container
          item
          xs={6}
          direction="column"
          alignItems="center"
          justifyContent="center"
        >
          <Grid item>
            <Typography variant="h2">
              Top 15 Pokémon by height
            </Typography>
          </Grid>
          <Grid item>
            <BarChart
              width={780}
              height={560}
              data={pokemonByHeight.slice(0, 15)}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="height" fill="#8884d8" />
            </BarChart>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
};

export default App;
