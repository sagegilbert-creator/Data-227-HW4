import streamlit as st
import pandas as pd
import altair as alt
import HW3

st.set_page_config(page_title="HW4 - Sage Gilbert", layout="wide")
alt.data_transformers.disable_max_rows()

season = st.radio("Season", ["Both", "2023-24", "2024-25"], horizontal=True)
metric = st.radio("Metric", ["All", "Goals", "Shots", "ShotsOnTarget", "Corners"], horizontal=True)

team_season = HW3.team_season.copy()
attackingdf = HW3.attackingdf.copy()
wide = HW3.wide.copy()

if season != "Both":
    team_season = team_season[team_season["Season"] == season]
    attackingdf = attackingdf[attackingdf["Season"] == season]
    wide = wide[wide["Season"] == season]

if metric != "All":
    attackingdf = attackingdf[attackingdf["Metric"] == metric]

team_click = alt.selection_point(fields=["Team"], empty="all")

points_chart = (
    alt.Chart(team_season)
    .mark_bar()
    .encode(
        y=alt.Y("Team:N", sort="-x"),
        x=alt.X("Points:Q"),
        color=alt.condition(team_click, alt.value("steelblue"), alt.value("lightgray")),
        tooltip=["Team:N", "Season:N", "Points:Q"]
    )
)

wins_chart = (
    alt.Chart(team_season)
    .mark_bar()
    .encode(
        y=alt.Y("Team:N", sort="-x"),
        x=alt.X("Wins:Q"),
        color=alt.condition(team_click, alt.value("orange"), alt.value("lightgray")),
        tooltip=["Team:N", "Season:N", "Wins:Q"]
    )
)

q1 = (points_chart & wins_chart).add_params(team_click)

q2 = (
    alt.Chart(attackingdf)
    .mark_line(point=True)
    .encode(
        x=alt.X("Matchweek:Q"),
        y=alt.Y("mean(Value):Q", title="Average attacking stat"),
        color="Metric:N",
        tooltip=["Season:N", "Team:N", "Metric:N", "Matchweek:Q", "Value:Q"]
    ).add_params(team_click)
    .transform_filter(team_click)
    .properties(width=700, height=320)
)

q3 = (
    alt.Chart(wide)
    .mark_circle(size=120)
    .encode(
        x=alt.X("AwayPoints:Q", title="Away Points"),
        y=alt.Y("HomePoints:Q", title="Home Points"),
        color=alt.condition(team_click, alt.value("teal"), alt.value("lightgray")),
        tooltip=["Season:N", "Team:N", "HomePoints:Q", "AwayPoints:Q"]
    )
    .add_params(team_click)
    .transform_filter(team_click)
    .properties(width=450, height=450)
)

st.title("Home Advantage in the Premier League - Sage Gilbert")

st.caption("Use the Season/Metric controls above. Click a team in the bar charts to filter the plots.")

st.markdown("""Typically, home advantage is treated like a the best thing any team can have in any sport. For Premier League soccer, it means the benefit of crowd energy, familiar field conditions, comfort of home, and reduced travel. It is often thought that all of these factors place the home team at an advantage to win any given game. 
Using match data from the 2023–24 and 2024–25 Premier League seasons, this story aims to asks:
how much does home advantage still matter, and which teams seem least dependent on it?""")

st.markdown("""
This chart displays a baseline of team quality. Points and wins reflect basic results and are valid measures of a team's competence, but they don't necessarily explain how each team got the wins. """)

st.header("Overview of Team Performances")
st.altair_chart(q1, use_container_width=True)

st.markdown("""
This chart aims to answer what the first one couldn't: the indicators that lead to a team's overall performance. Use the radio buttons to filter this chart by shots, shots on target, and corners to see whether a team's attacking profile stays consistent or spikes randomly.
""")

st.header("Attacking Patterns")
st.altair_chart(q2, use_container_width=True)

st.markdown("""And, finally, this scatter plot directly displays the relationship between Home Points and Away Points of a team in a given season. Teams with more points at home than away reflect the classic idea of a home advantage. Teams with nearly equal points at home and away tend to be less dependent on venues. And teams that have more points away than at home are the most interesting because they disrupt the norm of a home advantage.""")

st.header("Home vs Away")
st.altair_chart(q3, use_container_width=True)

st.header("Conclusion")
st.markdown(""" Home advantage still appears true for many clubs, but I think it’s not as uniform and reliable as perhaps previously thought. Some teams appear venue-dependent, while most teams seem to be able to earn points regardless of location. """)