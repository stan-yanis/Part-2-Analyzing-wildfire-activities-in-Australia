import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt

# Create app
app = dash.Dash(__name__)
server = app.server
# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Load the wildfire data into pandas dataframe
df =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Historical_Wildfires.csv')

# Extract month and year from the 'Date' column
# Convert the 'Date' column to datetime and create a new 'Month' column with the month names
df['Month'] = pd.to_datetime(df['Date']).dt.month_name()

# Convert the 'Date' column to datetime and create a new 'Year' column with the year value 
df['Year'] = pd.to_datetime(df['Date']).dt.year

# Layout Section of Dash

# Title to the Dashboard
app.layout = html.Div(children=[
    html.H1('Australia Wildfire Dashboard', 
            style={'textAlign': 'center',
                    'color': '#503D36',
                    'font-size': 26}),
    # First inner division to add radio buttons and dropdown for user selection
    html.Div([
        # Select region using radio buttons
        html.Div([
            html.H2('Select Region:', 
                    style={'margin-right': '2em'}),
            #Radio items to select the region
            dcc.RadioItems([{"label":"New South Wales","value": "NSW"},
                            {"label":"Northern Territory","value": "NT"},
                            {"label":"Queensland","value": "QL"},
                            {"label":"South Australia","value": "SA"},
                            {"label":"Tasmania","value": "TA"},
                            {"label":"Victoria","value": "VI"},
                            {"label":"Western Australia","value": "WA"}],"NSW", id='region',inline=True)]), # Default region set to 'NSW'
        #Dropdown to select year
        html.Div([
            html.H2('Select Year:', style={'margin-right': '2em'}),
            dcc.Dropdown(df.Year.unique(), value = 2005,id='year') # Default year set to 2005
        ]),
        # Two empty divisions to hold output graphs
        html.Div([
            html.Div([ ], id='plot1'),
            html.Div([ ], id='plot2')
        ], style={'display': 'flex'}),
    ])
])

# Define a callback function that updates the graphs based on the user's selected region and year
# This is a decorator that tells Dash how to link user inputs (region and year) to outputs (graphs).
@app.callback([Output(component_id='plot1', component_property='children'),
               Output(component_id='plot2', component_property='children')],
               [Input(component_id='region', component_property='value'), # 'value' represents the user-selected region
                Input(component_id='year', component_property='value')]) # 'value' represents the user-selected year
 

def reg_year_display(input_region,input_year):
   # input_region: The selected region value from the radio buttons.
   # input_year: The selected year value from the dropdown.

   # Filter data based on selected region 
   region_data = df[df['Region'] == input_region]

   # Filter data based on selected year
   y_r_data = region_data[region_data['Year']==input_year]

   # Pie Chart: Plot 1 'Monthly Average Estimated Fire Area'
   est_data = y_r_data.groupby('Month')['Estimated_fire_area'].mean().reset_index()

   fig1 = px.pie(est_data,
                  values='Estimated_fire_area', 
                  names='Month', 
                  title="{} : Monthly Average Estimated Fire Area in year {}".format(input_region,input_year))   
   
   # Bar Chart: Plot 2 'Monthly Average Count of Pixels for Presumed Vegetation Fires'
   veg_data = y_r_data.groupby('Month')['Count'].mean().reset_index()
   fig2 = px.bar(veg_data, 
                 x='Month', 
                 y='Count', 
                 title='{} : Average Count of Pixels for Presumed Vegetation Fires in year {}'.format(input_region,input_year)) 
   
   # Return the graphs to be displayed  
   return [dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2) ]

# Run the Dash app
if __name__ == '__main__':
    app.run_server() # starts the local server, which will host the web application and allow users to interact with it.
    