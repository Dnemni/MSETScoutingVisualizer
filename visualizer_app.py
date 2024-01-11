import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import tbapy
import datetime

st.title("MSET Scouting Data Visualizer")

#Blue Alliance API Parsing
tba = tbapy.TBA('kDUcdEfvMKYdouPPg0d9HudlOZ19GLwBBOH3CZuXMjMf7XITviY1eJrSs1jkrOYX')

def getinfo(t, yearlist, curyear):
  team = tba.team(t)
  years = tba.team_years(t)
  years = set(years).intersection(set(yearlist))
  for y in years:
    print(y)
    events = tba.team_events(t, y)
    awards = tba.team_awards(t, y)
    matches = tba.team_matches(t, year=y)
    print('team was active during %s years.' % years)
    print('In %d, team was in %d events: %s.' % (y, len(events), ', '.join(event.event_code for event in events)))
    print('In %d, team won %d awards, award list: %s.' % (y, len(awards), ",".join('%s (%s)' % (award.name, award.event_key) for award in awards)))
    #print('In %d, team match results are: %s.' % (y, ",".join(matches)))
    print()

def getscoreinfo(t, y, events):
  d = {}
  for event in events:
    matches = tba.team_matches(team=t, year=y)
    score = []
    for alliance in matches:
        blue_score = alliance['alliances']['blue']['score']
        blue_teams = alliance['alliances']['blue']['team_keys']
        red_score = alliance['alliances']['red']['score']
        red_teams = alliance['alliances']['red']['team_keys']
        eventChosen = alliance['event_key']

        teamcode = "frc"+str(t)
        if eventChosen == (str(y) + event):
          if teamcode in blue_teams:
            score.append(blue_score)
          else:
            score.append(red_score)
    d[event] = score
  return d

def getTeamEvents(team, yr):
    return tba.team_events("frc"+str(team), yr)

def getTeamYears(team):
    return tba.team_years("frc"+str(team))

evscr = getscoreinfo(649,2022,["casf","casj", "tur"])
data = {}
for key, scores in evscr.items():
  q1 = np.percentile(scores, 25)
  median = np.percentile(scores, 50)
  q3 = np.percentile(scores, 75)
  minimum = np.min(scores)
  maximum = np.max(scores)
  data.update({key:[q1, median, q3, minimum, maximum]})

#App and Chart Formation
while True:
    tm = st.text_input("Team Number", "649", key = "teamname", placeholder = "649")
    st.write("You selected:", tm)

    tmyrs = getTeamYears(tm)
    st.write("Type", type(tmyrs))
    st.write("Tmyrs", tmyrs)
    tmy = st.selectbox("Which year do you want to check", tmyrs, key = "teamyrs")
    st.write("You selected:", tmy)

    
    tyevents = getTeamEvents(tm, tmy)
    evnt = st.multiselect("Which events do you want to compare", tyevents, [], key = "teamevent")
    st.write("You selected:", evnt)

    tm1 = tm
    tmy1 =tmy

num_points = st.slider("Number of points in spiral", 1, 10000, 1100)
num_turns = st.slider("Number of turns in spiral", 1, 300, 31)

indices = np.linspace(0, 1, num_points)
theta = 2 * np.pi * num_turns * indices
radius = indices

x = radius * np.cos(theta)
y = radius * np.sin(theta)

df = pd.DataFrame({
    "x": x,
    "y": y,
    "idx": indices,
    "rand": np.random.randn(num_points),
})

st.altair_chart(alt.Chart(df, height=700, width=700)
    .mark_point(filled=True)
    .encode(
        x=alt.X("x", axis=None),
        y=alt.Y("y", axis=None),
        color=alt.Color("idx", legend=None, scale=alt.Scale()),
        size=alt.Size("rand", legend=None, scale=alt.Scale(range=[1, 150])),
    ))
