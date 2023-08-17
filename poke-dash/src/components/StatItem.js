import React from "react";
import {
  ListItemAvatar,
  Avatar,
  ListItemText,
  Grid,
  Typography,
  ListItem,
} from "@mui/material";

const StatItem = (props) => {
  const icon = props.icon;
  const statName = props.statName;
  const statValue = props.statValue;

  return (
    <ListItem key={statName}>
      <ListItemAvatar>
        <Avatar>{icon}</Avatar>
      </ListItemAvatar>
      <ListItemText>
        <Grid
          container
          spacing={2}
          direction="row"
          justifyContent="space-between"
        >
          <Grid item xs={6}>
            <Typography>{statName}:</Typography>
          </Grid>
          <Grid item xs={2}>
            <Typography align="right">{statValue}</Typography>
          </Grid>
        </Grid>
      </ListItemText>
    </ListItem>
  );
};

export default StatItem;
