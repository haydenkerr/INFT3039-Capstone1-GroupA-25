import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import requests

# If pulling from FastAPI endpoint
response = requests.get('http://192.168.1.17:8001/results')
data = response.json()
df = pd.DataFrame(data)

# For this demo, we’ll use a local CSV
# df = pd.read_csv('sample_results.csv')

app = dash.Dash(__name__)

fig = px.bar(df, x='teacher', y='average_score', color='competency')

app.layout = html.Div([
    html.H1('Admin/Teacher Dashboard', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='teacher-filter',
        options=[{'label': t, 'value': t} for t in df['teacher'].unique()],
        value=df['teacher'].unique()[0],
        clearable=False
    ),
    dcc.Graph(id='score-graph', figure=fig)
])

@app.callback(
    dash.dependencies.Output('score-graph', 'figure'),
    [dash.dependencies.Input('teacher-filter', 'value')]
)
def update_graph(selected_teacher):
    filtered_df = df[df['teacher'] == selected_teacher]
    fig = px.bar(filtered_df, x='competency', y='average_score', color='competency')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
