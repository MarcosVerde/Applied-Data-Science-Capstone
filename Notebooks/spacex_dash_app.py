# Import required libraries
import pandas as pd
import dash
from dash import html 
from dash import dcc 
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Obtener una lista de sitios de lanzamiento únicos
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                        [{'label': site, 'value': site} for site in launch_sites],
                                    value='ALL',  # Valor predeterminado para mostrar todos los sitios
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: str(i) for i in range(0, 10001, 2000)},  # Etiquetas cada 2000 kg
                                    value=[min_payload, max_payload]  # Valores por defecto del dataset
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Callback function for updating the pie chart based on the dropdown selection
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Agrupar los datos por 'Launch Site' y calcular el número de lanzamientos exitosos
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Success Count']
        
        # Crear el gráfico de pastel con éxito por sitio de lanzamiento
        fig = px.pie(success_counts, 
                     values='Success Count', 
                     names='Launch Site', 
                     title='Success Rate by Launch Site',
                     hole=0.3)
    else:
        # Filtrar los datos por el sitio seleccionado
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Contar éxitos y fallos
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        # Crear el gráfico de pastel para un sitio específico
        fig = px.pie(site_counts, 
                     values='count', 
                     names='class', 
                     title=f'Success vs. Failure for {entered_site}',
                     hole=0.3)

    return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(selected_site, selected_payload_range):
    # Filtrar datos por payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])
    ]
    
    # Si se selecciona "ALL", mostrar todos los sitios
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version",
            title="Payload Mass vs. Success Rate for All Sites"
        )
    else:
        # Filtrar datos por sitio de lanzamiento seleccionado
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        
        fig = px.scatter(
            site_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version",
            title=f"Payload Mass vs. Success Rate for {selected_site}"
        )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
