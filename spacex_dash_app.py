# Import required libraries
import pandas as pd
import dash
from dash import html, dcc  # Updated import statements
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    # Pie chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # Scatter chart for payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Use all data for the pie chart
        success_counts = spacex_df['class'].value_counts()
        fig = px.pie(
            values=success_counts,
            names=success_counts.index.map({0: 'Failed', 1: 'Successful'}),
            title='Total Launch Success'
        )
    else:
        # Filter data for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts()
        fig = px.pie(
            values=success_counts,
            names=success_counts.index.map({0: 'Failed', 1: 'Successful'}),
            title=f'Success Counts for {selected_site}'
        )
    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def update_scatter_chart(selected_site, selected_payload):
    # Filter the DataFrame based on selected site and payload range
    if selected_site == 'ALL':
        filtered_df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= selected_payload[0]) &
            (spacex_df['Payload Mass (kg)'] <= selected_payload[1])
        ]
    else:
        filtered_df = spacex_df[
            (spacex_df['Launch Site'] == selected_site) &
            (spacex_df['Payload Mass (kg)'] >= selected_payload[0]) &
            (spacex_df['Payload Mass (kg)'] <= selected_payload[1])
        ]

    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Success vs Payload Mass for {selected_site}' if selected_site != 'ALL' else 'Overall Success vs Payload Mass',
        labels={'class': 'Success (1) / Failure (0)'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
