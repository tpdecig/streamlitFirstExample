#
# S'exécute de cette façon  : streamlit run realTime_data.py
# ça lance un serveur web sur la machine qui sert une page web qui s'ouvre
# et détecte quand y a un changement dans le code / peut recharger page si nécessaire


import streamlit as st
import numpy as np
import pandas as pd
import time # to simulate real time data
import plotly.express as px # interactive charts


# Clef de VB :
openweathermap_api_key = '95411d1bc270611fdbb5cac8d68ef47b'

import operator as op  # to extract data form json 
import requests  # call APIs on the web


import hvplot.pandas # for interactive plots from dataframes


######################    FETCH DATA FOR A CITY  -> dataframe   #######################
def weather_data(cities, openweathermap_api_key=openweathermap_api_key):
    """
    Get weather data for a list of cities using the openweathermap API
    """
    L = []
    for c in cities: 
        #res = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={c},us&appid={openweathermap_api_key}&units=metric')
        res=requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={c},fr&units=metric&appid={openweathermap_api_key}')
        L.append(res.json())

    df = pd.DataFrame(L)
    df['lon'] = df['coord'].map(op.itemgetter('lon'))
    df['lat'] = df['coord'].map(op.itemgetter('lat'))
    df['Temperature'] = df['main'].map(op.itemgetter('temp'))
    df['Humidity'] = df['main'].map(op.itemgetter('humidity'))
    df['Wind Speed'] = df['wind'].map(op.itemgetter('speed'))
    df = df[['name','lon', 'lat','Temperature','Humidity','Wind Speed']]
    # Adding time information (for plots)
    df['time'] = [pd.Timestamp.now()]
    df = df.set_index('time')
    #df
    return df
########################################################################################




# read static csv from an online place
dataset_url = "https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv"
#age,job,marital,education,default,balance,housing,loan,contact,day,month,duration,campaign,pdays,previous,poutcome,deposit
#159,admin.,married,secondary,no,2343,yes,no,unknown,5,may,1042,1,-1,0,unknown,yes
#56,admin.,married,secondary,no,45,no,no,unknown,5,may,1467,1,-1,0,unknown,yes

st.set_page_config(
    page_title = 'Real-Time Data Science Dashboard',  # important pour le référencement sur Google quand on hébergera l'app
    page_icon = '✅',
    layout = 'wide'
)

# read csv from a URL just at start of the app
@st.cache_data
def get_data() -> pd.DataFrame:
    df1 = pd.read_csv(dataset_url)
    df2 = weather_data(['Montpellier'])
    #df2
    return (df1,df2)

# Gets data a first time
(df,wdf) = get_data()
#wdf

st.title("Real-Time / Live Weather Dashboard")

## Top-level filters
## défini un widget graphique pour choisir un métier parmi ceux listés dans le jeu de données
#job_filter = st.selectbox("Select the Job", pd.unique(df["job"]))
## on filtre le dataframe en fonction de ce qui est choisi dans le widget job_filter
#df = df[df["job"] == job_filter]

# affiche le dataframe filtre
#st.dataframe(df[0:5]) # n'affiche que les 5 premières lignes
# fait maintenant plus bas

# creating a single-element container
placeholder = st.empty()
# Insert a single-element container.
# Inserts a container into your app that can be used to hold a single element. This allows you to, for example, remove elements at any point, 
# or replace several elements at once (using a child multi-element container).
# To insert/replace/clear an element on the returned container, you can use "with" notation or just call methods directly on the returned object. 

temp = 0 # initial fake temperature (for delta in KPI)

# near real-time / live feed simulation
for seconds in range(200):

    #f'ok, I get here every second'
    # Reruns this every second or so

    # Gets (new) weather data
    new_wd = weather_data(['Montpellier'])

    # simulates faster variation
    #new_wd['Temperature'] += 5*(np.random.rand()-0.5)


    # Adds weather information to previous ones
    wdf = pd.concat([wdf,new_wd], ignore_index=False)
    #wdf['time'] = [pd.Timestamp.now()]
    #wdf = wdf.set_index('time')


    # Generates fake new data
    df["age_new"] = df["age"] * np.random.choice(range(1, 5))
    df["balance_new"] = df["balance"] * np.random.choice(range(1, 5))

    # Weather info displayes as KPIs


    previousTemp = temp
    temp = wdf.iloc[-1]['Temperature'] #+ 5*(np.random.rand()-0.5)
    wind = wdf.iloc[-1]['Wind Speed']
    #f'Temp = {temp} Wind = {wind}'

    #time.sleep(5)


    # creating KPIs with fake values
    avg_age = np.mean(df["age_new"])
    count_married = int(
        df[(df["marital"] == "married")]["marital"].count()
        + np.random.choice(range(1, 30))
    )
    balance = np.mean(df["balance_new"])


    with placeholder.container():
	    # la fonction container insère un conteneur multi-elements.
    	#Inserts an invisible container into your app that can be used to hold multiple elements. 
    	#This allows you to, for example, insert multiple elements into your app out of order.
    	# Et comme ils sont dans un st.empty() ca permettra de remplacer tous ces éléments d'un seul coup.

        # create three columns
        kpi1,kpi2 = st.columns(2)

        # fill in those three columns with respective metrics or KPIs
        kpi1.metric(
            label="Wind speed",
            value=wind, #round(avg_age),
            delta=0 #round(avg_age) - 10,
        )
        kpi2.metric(
            label="Temperature (C°)",
            value=f"°C {round(temp,2)} ",
            delta=(temp - previousTemp),
        )

        # PLot of Temperature
        st.markdown("## Temperature evolution")
        st.dataframe(wdf['Temperature'])
        st.line_chart(wdf['Temperature'])
        #wdf['Temperature'].hvplot.line(title='Temperature', backlog=1000)


        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### First Chart")
            fig = px.density_heatmap(
                data_frame=df, y="age_new", x="marital"
            )
            st.write(fig)
            
        with fig_col2:
            st.markdown("### Second Chart")
            fig2 = px.histogram(data_frame=df, x="age_new")
            st.write(fig2)

        # 3D scatter plot grâce à plotly.express :
        threeDplot = px.scatter_3d(df, x='campaign', y='day', z='age',
              color='marital')
        st.write(threeDplot)

        st.markdown("### Detailed Data View")
        st.dataframe(df)
        time.sleep(60)


