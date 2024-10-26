import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Hello, Shiny App!')
])

if __name__ == '__main__':
    app.run_server(debug=False)
    