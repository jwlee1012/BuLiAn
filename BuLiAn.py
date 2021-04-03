#####################################################################################
#####################################################################################
#####################################################################################
######## author = Tim Denzler
######## insitution = N/A
######## website = https://www.linkedin.com/in/tim-denzler/
######## version = 1.0
######## status = WIP
######## description = tba
######## layout inspired by https://share.streamlit.io/tylerjrichards/streamlit_goodreads_app/books.py
#####################################################################################
#####################################################################################
#####################################################################################

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import time
from matplotlib import pyplot as plt
from  matplotlib.ticker import FuncFormatter
import seaborn as sns


st.set_page_config(layout="wide")

### Data Import ###

df_database = pd.read_csv("./data/data_BuLi_13_20_cleaned.csv")
label_attr_dict = {"Goals":"goals","Halftime Goals":"ht_goals","Shots on Goal":"shots_on_goal","Distance Covered (in km)":"distance","Passes":"total_passes", "Successful Passes":"success_passes", "Failed Passes":"failed_passes", "Pass Success Ratio":"pass_ratio", "Ball Possession":"possession", "Tackle Success Ratio":"tackle_ratio", "Fouls Committed":"fouls", "Fouls Received":"got_fouled", "Offsides":"offside", "Corners":"corners"}
label_attr_dict_teams = {"Goals Scored":"goals","Goals Received":"goals_received","Halftime Goals Scored":"ht_goals","Halftime Goals Received":"halftime_goals_received","Shots on opposing Goal":"shots_on_goal","Shots on own Goal":"shots_on_goal_received","Distance Covered (in km)":"distance","Passes":"total_passes", "Successful Passes":"success_passes", "Failed Passes":"failed_passes", "Pass Success Ratio":"pass_ratio", "Ball Possession":"possession", "Tackle Success Ratio":"tackle_ratio", "Fouls Committed":"fouls", "Fouls Received":"got_fouled", "Offsides":"offside", "Corners":"corners"}
color_dict = {'1. FC Köln': '#fc4744', '1. FC Nürnberg':'#b50300', '1. FC Union Berlin':'#edd134', '1. FSV Mainz 05':'#fa2323', 'Bayer 04 Leverkusen':'#cf0c0c', 'Bayern München':'#e62222', 'Bor. Mönchengladbach':'#1f9900', 'Borussia Dortmund':'#fff830', 'Eintracht Braunschweig':'#dbca12', 'Eintracht Frankfurt':'#d10606', 'FC Augsburg':'#007512', 'FC Ingolstadt 04':'#8c0303', 'FC Schalke 04':'#1c2afc', 'Fortuna Düsseldorf':'#eb3838', 'Hamburger SV':'#061fc2', 'Hannover 96':'#127a18', 'Hertha BSC':'#005ac2', 'RB Leipzig':'#0707a8', 'SC Freiburg':'#d1332e', 'SC Paderborn 07':'#0546b5', 'SV Darmstadt 98':'#265ade', 'TSG Hoffenheim':'#2b82d9', 'VfB Stuttgart':'#f57171', 'VfL Wolfsburg':'#38d433', 'Werder Bremen':'#10a30b'}
### Helper Methods ###

def get_unique_seasons(df_data):
    #returns season in the form "13-14"
    unique_seasons = np.unique(df_data.season).tolist()
    return unique_seasons

def get_unique_seasons_modified(df_data):
    #returns unique season list in the form "Season 13/14" for labels
    unique_seasons = get_unique_seasons(df_data)
    seasons_modified = []
    for season in unique_seasons:
        seasons_modified.append("Season "+season.replace("-","/"))
    return seasons_modified

def get_unique_matchdays(df_data):
    #returns minimum and maximum
    return np.unique(df_data.matchday).tolist()

def get_unique_teams(df_data):
    unique_teams = np.unique(df_data.team).tolist()
    return unique_teams

def filter_season(df_data):
    df_filtered_season = pd.DataFrame()
    seasons = get_unique_seasons(df_data) #season list "13-14"
    start_raw = start_season.replace("/","-").replace("Season ","") #get raw start season "13-14"
    end_raw = end_season.replace("/","-").replace("Season ","") #get raw end season "19-20"
    start_index = seasons.index(start_raw)
    end_index = seasons.index(end_raw)+1
    seasons_selected = seasons[start_index:end_index]
    df_filtered_season = df_data[df_data['season'].isin(seasons_selected)]
    return df_filtered_season

def filter_matchday(df_data):
    df_filtered_matchday = pd.DataFrame()
    matchdays_list = list(range(selected_matchdays[0], selected_matchdays[1]+1))
    df_filtered_matchday = df_data[df_data['matchday'].isin(matchdays_list)]
    return df_filtered_matchday

def filter_teams(df_data):
    df_filtered_team = pd.DataFrame()
    if all_teams_selected == 'Select teams manually (choose below)':
        df_filtered_team = df_data[df_data['team'].isin(selected_teams)]
        return df_filtered_team
    return df_data

def stack_home_away_dataframe(df_data):
    df_data["game_id"] = df_data.index + 1
    column_names = ['distance','total_passes','success_passes','failed_passes','pass_ratio','possession','tackle_ratio','fouls','got_fouled','offside','corners']
    h_column_names = ['game_id','season','matchday','h_team','h_goals','a_goals','h_ht_goals','a_ht_goals','h_shots_on_goal','a_shots_on_goal']
    a_column_names = ['game_id','season','matchday','a_team','a_goals','h_goals','a_ht_goals','h_ht_goals','a_shots_on_goal','h_shots_on_goal']
    column_names_new = ['game_id','season','matchday','location','team','goals','goals_received','ht_goals','ht_goals_received','shots_on_goal','shots_on_goal_received','distance','total_passes','success_passes','failed_passes','pass_ratio','possession','tackle_ratio','fouls','got_fouled','offside','corners']
    for column in column_names: 
        h_column_names.append("h_" + column)
        a_column_names.append("a_" + column)
    df_home = df_data.filter(h_column_names)
    df_away = df_data.filter(a_column_names)
    df_home.insert(3,'location','h')
    df_away.insert(3,'location','a')
    df_home.columns = column_names_new
    df_away.columns = column_names_new
    df_total = df_home.append(df_away, ignore_index=True).sort_values(['game_id','season', 'matchday'], ascending=[True,True, True])
    return df_total

def group_measure_by_attribute(aspect,attribute,measure):
    df_data = df_data_filtered_team
    df_return = pd.DataFrame()
    if(measure == "Absolute"):
        if(attribute == "pass_ratio" or attribute == "tackle_ratio" or attribute == "possession"):
            measure = "Mean"
        else:
            df_return = df_data.groupby([aspect]).sum()            
    
    if(measure == "Mean"):
        df_return = df_data.groupby([aspect]).mean()*2
        
    if(measure == "Median"):
        df_return = df_data.groupby([aspect]).median()
    
    if(measure == "Minimum"):
        df_return = df_data.groupby([aspect]).min()
    
    if(measure == "Maximum"):
        df_return = df_data.groupby([aspect]).max()
    
    df_return["aspect"] = df_return.index
    if aspect == "team":
        df_return = df_return.sort_values(by=[attribute], ascending = False)
    return df_return
    
########################
### ANALYSIS METHODS ###
########################
#per game?
#differences?
#distribution, most common
#home team # away team # all team
# most common result
# farben teams

def plot_x_per_season(attr,measure):
    rc = {'figure.figsize':(8,4.5),
          'axes.facecolor':'#0e1117',
          'axes.edgecolor': '#0e1117',
          'axes.labelcolor': 'white',
          'figure.facecolor': '#0e1117',
          'patch.edgecolor': '#0e1117',
          'text.color': 'white',
          'xtick.color': 'white',
          'ytick.color': 'white',
          'grid.color': 'grey',
          'font.size' : 12,
          'axes.labelsize': 12,
          'xtick.labelsize': 12,
          'ytick.labelsize': 12}
    plt.rcParams.update(rc)
    fig, ax = plt.subplots()
    ### Goals
    attribute = label_attr_dict[attr]
    df_plot = pd.DataFrame()
    df_plot = group_measure_by_attribute("season",attribute,measure)
    ax = sns.barplot(x="aspect", y=attribute, data=df_plot, color = "#b80606")
    y_str = measure + " " + attr + " " + "per Game"
    if measure == "Absolute":
        y_str = measure + " " + attr
    if measure == "Minimum" or measure == "Maximum":
        y_str = measure + " " + attr + "in a Game"
        
    ax.set(xlabel = "Season", ylabel = y_str)
    if measure == "Mean" or attribute in ["distance","pass_ratio","possession","tackle_ratio"]:
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.2f'), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 15),
                   textcoords = 'offset points')
    else:
        for p in ax.patches:
            ax.annotate(format(str(int(p.get_height()))), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 15),
                   textcoords = 'offset points')
    st.pyplot(fig)

def plot_x_per_matchday(attr,measure):
    rc = {'figure.figsize':(8,4.5),
          'axes.facecolor':'#0e1117',
          'axes.edgecolor': '#0e1117',
          'axes.labelcolor': 'white',
          'figure.facecolor': '#0e1117',
          'patch.edgecolor': '#0e1117',
          'text.color': 'white',
          'xtick.color': 'white',
          'ytick.color': 'white',
          'grid.color': 'grey',
          'font.size' : 8,
          'axes.labelsize': 12,
          'xtick.labelsize': 8,
          'ytick.labelsize': 12}
    plt.rcParams.update(rc)
    fig, ax = plt.subplots()
    ### Goals
    attribute = label_attr_dict[attr]
    df_plot = pd.DataFrame()
    df_plot = group_measure_by_attribute("matchday",attribute,measure)
    ax = sns.barplot(x="aspect", y=attribute, data=df_plot.reset_index(), color = "#b80606")
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)+1))
    y_str = measure + " " + attr + " " + "per Game"
    if measure == "Absolute":
        y_str = measure + " " + attr
    if measure == "Minimum" or measure == "Maximum":
        y_str = measure + " " + attr + "in a Game"
        
    ax.set(xlabel = "Matchday", ylabel = y_str)
    if measure == "Mean" or attribute in ["distance","pass_ratio","possession","tackle_ratio"]:
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.2f'), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    else:
        for p in ax.patches:
            ax.annotate(format(str(int(p.get_height()))), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    st.pyplot(fig)

def plot_x_per_team(attr,measure): #total #against, #conceived
    rc = {'figure.figsize':(8,4.5),
          'axes.facecolor':'#0e1117',
          'axes.edgecolor': '#0e1117',
          'axes.labelcolor': 'white',
          'figure.facecolor': '#0e1117',
          'patch.edgecolor': '#0e1117',
          'text.color': 'white',
          'xtick.color': 'white',
          'ytick.color': 'white',
          'grid.color': 'grey',
          'font.size' : 8,
          'axes.labelsize': 12,
          'xtick.labelsize': 8,
          'ytick.labelsize': 12}
    
    plt.rcParams.update(rc)
    fig, ax = plt.subplots()
    ### Goals
    attribute = label_attr_dict_teams[attr]
    df_plot = pd.DataFrame()
    df_plot = group_measure_by_attribute("team",attribute,measure)
    if specific_team_colors:
        ax = sns.barplot(x="aspect", y=attribute, data=df_plot.reset_index(), palette = color_dict)
    else:
        ax = sns.barplot(x="aspect", y=attribute, data=df_plot.reset_index(), color = "#b80606")
    y_str = measure + " " + attr + " " + "per Game"
    if measure == "Absolute":
        y_str = measure + " " + attr
    if measure == "Minimum" or measure == "Maximum":
        y_str = measure + " " + attr + "in a Game"
    ax.set(xlabel = "Team", ylabel = y_str)
    plt.xticks(rotation=66,horizontalalignment="right")
    if measure == "Mean" or attribute in ["distance","pass_ratio","possession","tackle_ratio"]:
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.2f'), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    else:
        for p in ax.patches:
            ax.annotate(format(str(int(p.get_height()))), 
                  (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center',
                   va = 'center', 
                   xytext = (0, 18),
                   rotation = 90,
                   textcoords = 'offset points')
    st.pyplot(fig)

####################
### INTRODUCTION ###
####################

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns((.1, 2, .2, 1, .1))
row0_1.title('Analyzing Bundesliga Data')
row0_2.subheader('Streamlit App by [Tim Denzler](https://www.linkedin.com/in/tim-denzler/)')
row1_spacer1, row1_1, row1_spacer2 = st.beta_columns((.1, 3.2, .1))
with row1_1:
    st.markdown("Hello there! Have you ever spent your weekend watching the German Bundesliga and had your friends complain about how 'players definitely used to run more' and how your club 'just won more tackles last season' ? However, you did not want to start an argument because you did not have any stats at hand? Well this simple application containing Bundesliga data from seasons 2013/2014 to season 2019/2020 allows you to discover just that! If you're on a mobile device, I would recommend switching over to landscape for viewing ease.")
    st.markdown("**First select the data range you want to analyze:** 👇")

#################
### SELECTION ###
#################
df_stacked = stack_home_away_dataframe(df_database)

row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3  = st.beta_columns((.2, 3.2, .4, 3.2, .2))

### SEASON RANGE ###
unique_seasons = get_unique_seasons_modified(df_database)
with row2_1: 
    start_season, end_season = st.select_slider('Select the season range you want to include', unique_seasons, value = ["Season 13/14","Season 19/20"]
    )
df_data_filtered_season = filter_season(df_stacked)        


### MATCHDAY RANGE ###
unique_matchdays = get_unique_matchdays(df_data_filtered_season) #min and max matchday
with row2_2: #matchday range
    selected_matchdays = st.select_slider('Select the matchday range you want to include', unique_matchdays, value=[min(unique_matchdays),max(unique_matchdays)])

df_data_filtered_matchday = filter_matchday(df_data_filtered_season)        

### TEAM SELECTION ###
unique_teams = get_unique_teams(df_data_filtered_matchday)
row3_spacer1, row3_1, row3_spacer2 = st.beta_columns((.1, 3.2, .1))
with row3_1:
    all_teams_selected = st.selectbox('Do you want to focus on more more specific teams? If the answer is yes, please check the box below and then select the specfic team(s) in the new field.', ['Include all available teams','Select teams manually (choose below)'])
    if all_teams_selected == 'Select teams manually (choose below)':
        selected_teams = st.multiselect("Select and deselect the teams you would like to include in the analysis? You can clear the current selection by clicking the corresponding button on the right", unique_teams, default = unique_teams)

    df_data_filtered_team = filter_teams(df_data_filtered_matchday)        
    st.text('')
    see_data = st.beta_expander('Want to see the currently selected raw data first? Click here 👉')
    with see_data:
        st.dataframe(data=df_data_filtered_team.reset_index(drop=True))
st.text('')

#st.dataframe(data=df_stacked.reset_index(drop=True))
#st.dataframe(data=df_data_filtered)

################
### ANALYSIS ###
################

types = ["Absolute","Mean","Median","Maximum","Minimum"]

row4_spacer1, row4_1, row4_spacer2, row4_2, row4_spacer3  = st.beta_columns((.2, 3.2, .4, 3.2, .2))
with row4_1:
    ### X per Season ###
    st.subheader('Analysis per Season')
    plot_x_per_season_selected = st.selectbox ("Which aspect do you want to analyze for each season?", list(label_attr_dict.keys()))
    plot_x_per_season_type = st.selectbox ("Which measure do you want to analyze for each season?", types)
    if all_teams_selected != 'Select teams manually (choose below)' or selected_teams:
        plot_x_per_season(plot_x_per_season_selected,plot_x_per_season_type)
    else:
        st.warning('Please select at least one team')
        

with row4_2:
    ### X per Matchday ###
    st.subheader('Analysis per Matchday')
    plot_x_per_matchday_selected = st.selectbox ("Which aspect do you want to analyze for each matchday?", list(label_attr_dict.keys()))
    plot_x_per_matchday_type = st.selectbox ("Which measure do you want to analyze for each matchday?", types)
    if all_teams_selected != 'Select teams manually (choose below)' or selected_teams:
        plot_x_per_matchday(plot_x_per_matchday_selected, plot_x_per_matchday_type)
    else:
        st.warning('Please select at least one team')
    
row5_spacer1, row5_1, row5_spacer2, row5_2, row5_spacer3  = st.beta_columns((.2, 3.2, .4, 3.2, .2))
with row5_1:
    ### X per Team ###
    st.subheader('Analysis per Team')
    plot_x_per_team_selected = st.selectbox ("Which aspect do you want to analyze for each team?", list(label_attr_dict_teams.keys()))
    plot_x_per_team_type = st.selectbox ("Which measure do you want to analyze for each team?", types)
    specific_team_colors = st.checkbox("Use team specific color scheme")
    if all_teams_selected != 'Select teams manually (choose below)' or selected_teams:
        plot_x_per_team(plot_x_per_team_selected, plot_x_per_team_type)
    else:
        st.warning('Please select at least one team')