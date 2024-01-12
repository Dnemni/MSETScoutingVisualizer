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
        matches = tba.team_matches(team="frc"+str(t), year=y)
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
    e = []
    evs = tba.team_events("frc"+str(team), yr)
    for evnts in evs:
        e.append(evnts.event_code)
    return e


def getTeamYears(team):
    return tba.team_years("frc"+str(team))

def getTeamData(team, year, events):
    evscr = getscoreinfo(team, year, events)
    data = {}
    for key, scores in evscr.items():
        q1 = np.percentile(scores, 25)
        median = np.percentile(scores, 50)
        q3 = np.percentile(scores, 75)
        minimum = np.min(scores)
        maximum = np.max(scores)
        data.update({key:[q1, median, q3, minimum, maximum]})
    return data

#Input
tm = st.text_input("Team Number", "649", key = "teamname", placeholder = "649")

tmyrs = getTeamYears(tm)
tmy = st.selectbox("Which year do you want to check", tmyrs, key = "teamyrs")


tyevents = getTeamEvents(tm, tmy)
evnt = st.multiselect("Which events do you want to compare", tyevents, [], key = "teamevent")

#Charts
tmscrs = getTeamData(tm, tmy, evnt)
evscr = getscoreinfo(tm, tmy, evnt)
print(getscoreinfo("649", 2022, ["casf", "casj", "tur"]))

st.write(evscr)
data = alt.Data(values=evscr)
scrdata = [[]]
for key, scores in evscr.items():
    scrdata.append(scores)

"""
option = {
    "title": [
        {"text": "Team " + str(tm) + " Scoring Boxplots", "left": "center"},
        {
            "text": "upper: Q3 + 1.5 * IQR \nlower: Q1 - 1.5 * IQR",
            "borderColor": "#999",
            "borderWidth": 1,
            "textStyle": {"fontWeight": "normal", "fontSize": 14, "lineHeight": 20},
            "left": "10%",
            "top": "90%",
        },
    ],
    "dataset": [
        {
            "source": scrdata
        },
        {
            "transform": {
                "type": "boxplot",
                "config": {"itemNameFormatter": "expr {value}"},
            }
        },
        {"fromDatasetIndex": 1, "fromTransformResult": 1},
    ],
    "tooltip": {"trigger": "item", "axisPointer": {"type": "shadow"}},
    "grid": {"left": "10%", "right": "10%", "bottom": "15%"},
    "xAxis": {
        "type": "category",
        "boundaryGap": True,
        "nameGap": 30,
        "splitArea": {"show": False},
        "splitLine": {"show": False},
    },
    "yAxis": {
        "type": "value",
        "name": "points scored",
        "splitArea": {"show": True},
    },
    "series": [
        {"name": "boxplot", "type": "boxplot", "datasetIndex": 1},
        {"name": "outlier", "type": "scatter", "datasetIndex": 2},
    ],
}
st_echarts(option, height="500px")

"""

d = pd.DataFrame({"Event": "casf", "Points Scored": [1,2,3,4,5]})
#alt.Data(values=[{"Event": "casf", "Points Scored": [1,2,3,4,5]}])


boxplot = alt.Chart(d).mark_boxplot(extent="min-max").encode(
    alt.X("Event:N"),
    alt.Y("Points Scored:Q").scale(zero=False),
    alt.Color("Origin:N").legend(None),
    ).properties(
        width=400,
        height=300
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
# Display the boxplot
st.altair_chart(boxplot, use_container_width=True)
st.write(data)
