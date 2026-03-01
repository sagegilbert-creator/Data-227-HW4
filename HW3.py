#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np 
import pandas as pd 
import altair as alt
from vega_datasets import data


# To start, I choose to answer questions 1, 2, and 3 provided in the dataset. 

# In[2]:


yr2324 = pd.read_csv("data/PL-season-2324.csv")
yr2425 = pd.read_csv("data/PL-season-2425.csv")

yr2324["Season"] = "2023-24"
yr2425["Season"] = "2024-25"

#merging the datasets so that it's easier to analyze team-centric data instead of per match data
dfboth = pd.concat([yr2324, yr2425], ignore_index=True)

home = dfboth[[
    "Date", "Season", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "HS", "HST", "HC"]].copy()

home.columns = [
    "Date", "Season", "Team", "Opponent",
    "Goals", "OppGoals", "Shots", "ShotsOnTarget", "Corners"]

home["HomeAway"] = "Home"

away = dfboth[[
    "Date", "Season", "AwayTeam", "HomeTeam",
    "FTAG", "FTHG", "AS", "AST", "AC"]].copy()

away.columns = [
    "Date", "Season", "Team", "Opponent",
    "Goals", "OppGoals", "Shots", "ShotsOnTarget", "Corners"]

away["HomeAway"] = "Away"

df = pd.concat([home, away], ignore_index=True)

df["Points"] = 0

df.loc[df["Goals"] > df["OppGoals"], "Points"] = 3
df.loc[df["Goals"] == df["OppGoals"], "Points"] = 1
df.head(2)

df["Win"] = (df["Goals"] > df["OppGoals"]).astype(int)

team_season = (df.groupby(["Season", "Team"], as_index=False)
      .agg(Points=("Points", "sum"), Wins=("Win", "sum")))

seasons = "Both", "2023-24", "2024-25"

season_param = alt.param(
    name="SeasonView",
    value="Both",
    bind=alt.binding_radio(
        options= seasons,
        name="Season: "))

team_click = alt.selection_point(fields=["Team"], empty="all")

points_chart = (
    alt.Chart(team_season).mark_bar()
    .encode(y= "Team:N",x="Points:Q",
        column="Season:N",
        color=alt.condition(team_click, alt.value("steelblue"), alt.value("lightgray")),
        tooltip=["Team", "Season", "Points"]).add_params(season_param)
    .transform_filter((season_param == "Both") | (alt.datum.Season == season_param)))

wins_chart = (alt.Chart(team_season).mark_bar()
    .encode(
        y="Team:N",x="Wins:Q",
        column="Season:N",
        color=alt.condition(team_click, alt.value("orange"), alt.value("lightgray")),
        tooltip=["Team", "Season", "Wins"]).add_params(season_param)
              .transform_filter((season_param == "Both") | (alt.datum.Season == season_param)))

q1 = (points_chart & wins_chart).add_params(team_click)


#alt.data_transformers.disable_max_rows()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df = df.sort_values(["Season", "Team", "Date"])
df["Matchweek"] = df.groupby(["Season", "Team"]).cumcount() + 1

attackingstats = ["Goals", "Shots", "ShotsOnTarget", "Corners"]

metric = alt.param(
    name="MetricView",
    value="Goals",
    bind=alt.binding_radio(
        options=["All"] + attackingstats,   
        name="Metric: "))

team_week = (
    df.groupby(["Season", "Team", "Matchweek"], as_index=False)[attackingstats]
      .mean()
)

attackingdf = team_week.melt(
    id_vars=["Season", "Team", "Matchweek"],
    value_vars=attackingstats,
    var_name="Metric",
    value_name="Value"
)

q2 = alt.Chart(attackingdf).mark_line(point = True).encode(
    x="Matchweek:Q",
    y=alt.Y("mean(Value):Q", title="Average attacking stat"),
    color="Metric:N",
    tooltip=[
        "Season:N",
        "Team:N",
        "Metric:N", "Matchweek:Q"]).add_params(season_param, metric, team_click).transform_filter(
    team_click).transform_filter(
    (season_param == "Both") | (alt.datum.Season == season_param)
).transform_filter((metric == "All") | (alt.datum.Metric == metric)).properties(
    title="Attacking performance per team across matchweeks",
    width=520,
    height=320)


dashboard = (q1 & q2).add_params(season_param, metric, team_click)

wide = (df.groupby(["Season", "Team", "HomeAway"], as_index=False)["Points"]
      .sum().pivot_table(index=["Season", "Team"], columns="HomeAway", values="Points", aggfunc="sum")
      .reset_index())

wide = wide.rename(columns={"Home": "HomePoints", "Away": "AwayPoints"})
wide = wide.fillna(0)

q3 = (
    alt.Chart(wide)
    .mark_circle(size=120)
    .encode(
        x=alt.X("AwayPoints:Q", title="Away Points"),
        y=alt.Y("HomePoints:Q", title="Home Points"),
        tooltip=["Season:N", "Team:N", "HomePoints:Q", "AwayPoints:Q"])
    .add_params(season_param, team_click)
    .transform_filter((season_param == "Both") | (alt.datum.Season == season_param)).transform_filter(team_click)
    .properties(width=400, height=400, title="Q3: Home advantage (Home vs Away points)"))

dashboard2 = (q1 & q2 & q3).add_params(season_param, team_click, metric)



