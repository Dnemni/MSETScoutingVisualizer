import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import tbapy
import datetime

st.set_page_config(
    page_title="MSET Scouting Data Visualizer",
    page_icon=":chart:",  # You can use any emoji as an icon
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("MSET Scouting Data Visualizer")

# Set theme
theme = {
    "backgroundColor": "#afc9f7",
    "secondaryBackgroundColor": "#8f98ea",
    "textColor": "#000000",
}

st.markdown(
    """
    <style>
        body {
            background-color: %(backgroundColor)s;
        }
        .secondaryBackgroundColor {
            background-color: %(secondaryBackgroundColor)s;
        }
        .markdown-text-container {
            color: %(textColor)s;
        }
    </style>
    """ % theme,
    unsafe_allow_html=True,
)

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
        try:
            q1 = np.percentile(scores, 25)
            median = np.percentile(scores, 50)
            q3 = np.percentile(scores, 75)
            minimum = np.min(scores)
            maximum = np.max(scores)
            data.update({key:[q1, median, q3, minimum, maximum]})
        except:
            st.error("No data. Try a different year.")
            st.stop()
    return data

def checkTeamValidity(team):
    allteams = np.load("teamnumbers.npy")
    if team in allteams:
        return True
    return False

#Input
st.sidebar.title("Select Team")

class SideBarSetup:
    def tmnumIN(self, a):
        with st.sidebar:
            t = st.text_input("Team Number", "649", key = "teamname " + str(a), placeholder = "649")
        return t

    def tmyrIN(self, b, t):
        with st.sidebar:
            tmyrs = getTeamYears(t)
            tmy = st.selectbox("Which year do you want to check", tmyrs, key = "teamyrs " + str(b))
        return tmy

    def tmyrevIN(self, c, t, y):
        with st.sidebar:
            tyevents = getTeamEvents(t, y)
            evnt = st.multiselect("Which events do you want to compare", tyevents, [], key = "teamevent " + str(c))
        return evnt


#with st.sidebar:
    """tm = st.text_input("Team Number", "649", key = "teamname", placeholder = "649")

    tmyrs = getTeamYears(tm)
    tmy = st.selectbox("Which year do you want to check", tmyrs, key = "teamyrs")


    tyevents = getTeamEvents(tm, tmy)
    evnt = st.multiselect("Which events do you want to compare", tyevents, [], key = "teamevent")
    
    
    sb1 = SideBarSetup()
    tm = sb1.tmnumIN()
    tmy = sb1.tmyrIN()
    evnt = sb1.tmyrevIN()
    if st.sidebar.button("Add Team", type="primary"):
        sb2 = SideBarSetup()
        tm = sb2.tmnumIN()
        tmy = sb2.tmyrIN()
        evnt = sb2.tmyrevIN()
    """
st.header("Score Visualization")
"""
# Add teams dynamically
sb1 = SideBarSetup()
tm1 = sb1.tmnumIN("649")
tmy1 = sb1.tmyrIN()
evnt1 = sb1.tmyrevIN(0)
teams_info.append((tm1, tmy1, evnt1))
teams_info = []
x = 1
while st.sidebar.button(f"Add Team {x}", type="primary", key=f"add_team_{x}"):
    sb = SideBarSetup()
    tm = sb.tmnumIN(x)
    tmy = sb.tmyrIN(x)
    evnt = sb.tmyrevIN(x)
    teams_info.append((tm, tmy, evnt))
    x += 1

# Display information for each team
for idx, (tm, tmy, evnt) in enumerate(teams_info):
    st.sidebar.header(f"Team {idx + 1} Information")
    st.sidebar.text(f"Team Number: {tm}")
    st.sidebar.text(f"Year: {tmy}")
    st.sidebar.text(f"Events: {', '.join(evnt)}")
"""
x = 1
teams_info = []
sbslist = []
for i in range(x):
    sb = SideBarSetup()
    tm = sb.tmnumIN(x)
    tmy = sb.tmyrIN(x, tm)
    evnt = sb.tmyrevIN(x, tm, tmy)
    teams_info.append((tm, tmy, evnt))
    if st.sidebar.button("Add Team", type="primary"):
        x += 1
    sbslist.append(sb)

# Display information for each team
for idx, (tm, tmy, evnt) in enumerate(teams_info):
    st.sidebar.header(f"Team {idx + 1} Information")
    st.sidebar.text(f"Team Number: {tm}")
    st.sidebar.text(f"Year: {tmy}")
    st.sidebar.text(f"Events: {', '.join(evnt)}")

#Charts
tmscrs = getTeamData(tm, tmy, evnt)
evscr = getscoreinfo(tm, tmy, evnt)

df = pd.DataFrame([(event, score) for event, scores in evscr.items() for score in scores], columns=['Event', 'Points Scored'])

boxplot = alt.Chart(df).mark_boxplot(extent="min-max", size = 50).encode(
    alt.X("Event:N", axis=alt.Axis(labels=True, ticks=True, domain=True, grid=True, domainColor="white", gridColor="white", labelColor="black", tickColor="white", titleColor="black")),
    alt.Y("Points Scored:Q", axis=alt.Axis(labels=True, ticks=True, domain=True, grid=True, domainColor="white", gridColor="white", labelColor="black", tickColor="white", titleColor="black")).scale(zero=False),
    alt.Color("Event:N").legend(None),
    ).properties(
        width=400,
        height=300
    ).configure_title(
        fontSize=16,
        anchor='start'
    )
# Display the boxplot
st.altair_chart(boxplot, use_container_width=True)

st.header("Awards & Stats")
awards = tba.team_awards(int(tm), int(tmy))
if len(awards) == 0:
    st.write('In %d, team won no awards.' % (tmy))
elif len(awards) == 1:
    st.write('In %d, team won %d award, award list: %s.' % (tmy, len(awards), ", ".join('%s (%s)' % (award.name, award.event_key) for award in awards)))
else:
    st.write('In %d, team won %d awards, award list: %s.' % (tmy, len(awards), ", ".join('%s (%s)' % (award.name, award.event_key) for award in awards)))