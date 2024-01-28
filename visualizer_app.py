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


def getscoreinfoNew(t, y, events):
    d = {}
    for event in events:
        matches = tba.team_matches(team="frc"+str(t), year=y)
        playoffs = tba.event_predictions(str(y) + event)["match_predictions"]["playoff"]
        quals = tba.event_predictions(str(y) + event)["match_predictions"]["qual"]
        scorePrd = [[],[]]
        for alliance in matches:
            blue_score = alliance['alliances']['blue']['score']
            blue_teams = alliance['alliances']['blue']['team_keys']
            red_score = alliance['alliances']['red']['score']
            red_teams = alliance['alliances']['red']['team_keys']
            eventChosen = alliance['event_key']

            teamcode = "frc"+str(t)
            if eventChosen == (str(y) + event):
                if teamcode in blue_teams:
                    scorePrd[0].append(blue_score)
                    for keys in playoffs:
                        if(keys == alliance['key']):
                            scorePrd[1].append(playoffs[keys]["blue"]["score"])
                    for keys in quals:
                        if(keys == alliance['key']):
                            scorePrd[1].append(quals[keys]["blue"]["score"])
                else:
                    scorePrd[0].append(red_score)
                    for keys in playoffs:
                        if(keys == alliance['key']):
                            scorePrd[1].append(playoffs[keys]["red"]["score"])
                    for keys in quals:
                        if(keys == alliance['key']):
                            scorePrd[1].append(quals[keys]["red"]["score"])
        d[event] = scorePrd
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
    def bar(self):
        st.sidebar.header("----------")
    
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

def basicTeamBoxPlot(tmevscr):
    #Charts
    df = pd.DataFrame([(event, score) for event, scores in tmevscr.items() for score in scores], columns=['Event', 'Points Scored'])

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
    
    
def individualTeamScatterPlot(scores_data):
    
    for event, scores in scores_data.items():
        st.write("Event: ", event)
        min_length = min(len(scores[0]), len(scores[1]))
    
        # Prepare data for scatter plot
        data = pd.DataFrame({
          'Match': range(1, min_length + 1),
          'Actual Score': scores[0][:min_length],
          'Predicted Score': scores[1][:min_length]
        })
        
        # Create scatter plot
        #data = pd.DataFrame({'Match': range(1, len(scores) + 1), 'Points Scored': scores})

        scatter_plot_1 = alt.Chart(data).mark_circle(size=60).encode(
            alt.X("Match:N", axis=alt.Axis(labels=True, ticks=True, domain=True, grid=True, domainColor="white", gridColor="white", labelColor="black", tickColor="white", titleColor="black")),
            alt.Y("Actual Score:Q", axis=alt.Axis(labels=True, ticks=True, domain=True, grid=True, domainColor="white", gridColor="white", labelColor="black", tickColor="white", titleColor="black")).scale(zero=False),
            color = alt.value("blue")
            #alt.Color("variable:N", legend=alt.Legend(title="Score Type")),
            ).properties(
                width=200,
                height=300
            )#.configure_legend(
             #   orient='right'
            #)
        
        scatter_plot_2 = alt.Chart(data).mark_circle(size=60).encode(
            alt.X("Match:N", axis=alt.Axis(labels=True, ticks=True, domain=True, grid=True, domainColor="white", gridColor="white", labelColor="black", tickColor="white", titleColor="black")),
            alt.Y("Predicted Score:Q", axis=alt.Axis(labels=True, ticks=True, domain=True, grid=True, domainColor="white", gridColor="white", labelColor="black", tickColor="white", titleColor="black")).scale(zero=False),
            color = alt.value("orange")
            #alt.Color("variable:N", legend=alt.Legend(title="Score Type")),
            ).properties(
                width=200,
                height=300
            )
            #.configure_legend(
            #    orient='right'
            #)

        # Combine scatter plot and line of best fit
        #line_of_fit = scatter_plot.transform_regression('Match','Points Scored').mark_line()
        
        combined_chart = scatter_plot_2 + scatter_plot_1

        # Display the chart
        st.altair_chart(combined_chart, use_container_width=True)
        #st.altair_chart(scatter_plot_2, use_container_width=True)



tba = tbapy.TBA('kDUcdEfvMKYdouPPg0d9HudlOZ19GLwBBOH3CZuXMjMf7XITviY1eJrSs1jkrOYX')

# Add teams dynamically
teams_info = []
sblist = []
sb0 = SideBarSetup()
tm0 = sb0.tmnumIN(0)
tmy0 = sb0.tmyrIN(0, tm0)
evnt0 = sb0.tmyrevIN(0, tm0, tmy0)
teams_info.append((tm0, tmy0, evnt0))
sblist.append(sb0)
x = 1

if 'buttonClick' not in st.session_state:
    st.session_state.buttonClick = 0

#buttonClick = 0
if st.button("Add Team", type="primary", key=f"add_team_{x}"):
    st.session_state.buttonClick += 1

tab1, tab2, tab3 = st.tabs(["Plots", "Awards", "Blank (pictures?)"])

for i in range (st.session_state.buttonClick):
    globals()["sb" + str(x)] = SideBarSetup()
    globals()["sb" + str(x)].bar()
    globals()["tm" + str(x)] = globals()["sb" + str(x)].tmnumIN(x)
    globals()["tmy" + str(x)] = globals()["sb" + str(x)].tmyrIN(x, globals()["tm" + str(x)])
    globals()["evnt" + str(x)] = globals()["sb" + str(x)].tmyrevIN(x, globals()["tm" + str(x)], globals()["tmy" + str(x)])
    teams_info.append((globals()["tm" + str(x)], globals()["tmy" + str(x)], globals()["evnt" + str(x)]))
    sblist.append(globals()["sb" + str(x)])
    x += 1

with tab1:
    st.header("Score Visualization")
    
    # Display charts for each team
    for idx, (tm, tmy, evnt) in enumerate(teams_info):
        evscr = getscoreinfo(tm, tmy, evnt)
        nevscr = getscoreinfoNew(tm, tmy, evnt)
        
        st.write("Team " + str(tm) + " Event Scores Boxplot")
        basicTeamBoxPlot(evscr)
        
        st.write("Team " + str(tm) + " Predicted vs Actual Scores Scatterplot")
        individualTeamScatterPlot(nevscr)

with tab2:
    st.header("Awards & Stats")
    awards = tba.team_awards(int(tm), int(tmy))
    if len(awards) == 0:
        st.write('In %d, team won no awards.' % (tmy))
    elif len(awards) == 1:
        st.write('In %d, team won %d award, award list: %s.' % (tmy, len(awards), ", ".join('%s (%s)' % (award.name, award.event_key) for award in awards)))
    else:
        st.write('In %d, team won %d awards, award list: %s.' % (tmy, len(awards), ", ".join('%s (%s)' % (award.name, award.event_key) for award in awards)))