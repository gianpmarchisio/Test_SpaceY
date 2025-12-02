# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Preparar opciones para el Dropdown (TASK 1 logic)
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
dropdown_options.extend([{'label': site, 'value': site} for site in launch_sites])

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown list for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart (output)
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload] # Valor inicial: rango completo
    ),

    # TASK 4: Scatter chart (output)
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ----------------------------------------------------------------------
# 3. CALLBACKS (TASK 2 & TASK 4)
# ----------------------------------------------------------------------

# TASK 2: Callback function for `site-dropdown` -> `success-pie-chart`
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    
    if entered_site == 'ALL':
        # Muestra el total de lanzamientos exitosos por sitio
        success_by_site = filtered_df[filtered_df['class'] == 1].groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            success_by_site,
            names='Launch Site', 
            values='class',
            title='Total Successful Launches By Site'
        )
        return fig
    else:
        # Muestra el conteo de Success (1) vs Failed (0) para el sitio específico
        specific_site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        site_counts = specific_site_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        
        # Mapeamos 1 y 0 a etiquetas claras para el gráfico
        site_counts['Outcome'] = site_counts['class'].apply(lambda x: 'Success' if x == 1 else 'Failure')

        fig = px.pie(
            site_counts,
            values='count',
            names='Outcome',
            title=f'Success vs. Failure for site {entered_site}',
            color='Outcome',
            color_discrete_map={'Success': 'green', 'Failure': 'red'}
        )
        return fig


# TASK 4: Callback function for `site-dropdown` and `payload-slider` -> `success-payload-scatter-chart`
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    
    # Filtrar el DataFrame por el rango de Payload seleccionado
    df_by_payload = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    if entered_site != 'ALL':
        # Filtrar adicionalmente por sitio de lanzamiento si no es 'ALL'
        df_by_payload = df_by_payload[df_by_payload['Launch Site'] == entered_site]
    
    
    title = f'Correlation Between Payload and Success (Class) | Filtered by Site: {entered_site}'
    
    fig = px.scatter(
        df_by_payload, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category', # Usamos el color para la versión del booster
        title=title
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run()