import pandas as pd
from numpy import select
import plotly.graph_objects as go
from dash import Dash, dcc, html
import plotly.express as px

# Connect to GoogleSheets
sheet_id = ${{ secrets.GOOGLE_SHEET_ID }}
sheet_name = 'operations'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'

# Create df from csv
df = pd.read_csv(url, on_bad_lines='skip')

# Convert data
df['Payment_Amount'] = df['Payment_Amount'].str.replace(',', '.').astype('float').round()
df['Operation_Date'] = df['Operation_Date'].astype('datetime64')

# Filer data
date_from = '2023-02-01 00:00:00'
filtered_categories = ('Переводы', 'Вне бюджета')

df = df[df['Status'] != 'FAILED']  # Filter failed operations
df = df[df['Operation_Date'] >= date_from]
df = df[~df['Category'].isin(filtered_categories)]

# Create aggregated table
df = df.groupby(['Category']).agg({
    'Payment_Amount': 'sum'}).reset_index()

# Create Cost DataFrame
cost_df = df[df['Payment_Amount'] <= 0].sort_values('Payment_Amount', ascending=True)
cost_df['Amount'] = abs(df['Payment_Amount'])  # For Sunburst chart

# Grope by macro-categories
home_categories = ['ЖКХ',
                   'Дом'
                   ]
food_categories = ['Супермаркеты',
                   'Фастфуд',
                   'Кофе',
                   'Рестораны'
                   ]
health_categories = ['Аптеки,'
                     'Красота и здоровье',
                     'Медицина',
                     'Мед. услуги'

                     ]
transport_categories = ['Транспорт',
                        'Автобусы',
                        'Такси',
                        'Авиабилеты'
                        ]

cost_df['Group'] = select(
    [
        cost_df['Category'].isin(home_categories),
        cost_df['Category'].isin(food_categories),
        cost_df['Category'].isin(health_categories),
        cost_df['Category'].isin(transport_categories)
    ],
    [
        'Home',
        'Food',
        'Health',
        'Transport'
    ],
    default='Unknown'
)

# Print df to check
print(cost_df)

# Create charts
table = go.Figure(data=[go.Table(
    header=dict(
        values=['Category', 'Cost'],
        fill_color='lavender',
        align='left', font=dict(color='black', size=12)
    ),
    cells=dict(
        values=[cost_df.Category, cost_df.Payment_Amount],
        align='left', font=dict(color='black', size=11)
    )
)])

bar = go.Figure(data=go.Bar(
    name='Cost',
    x=cost_df.Payment_Amount,
    y=cost_df.Category,
    orientation='h')
)

sunburst = px.sunburst(
    cost_df,
    path=['Group', 'Category'],
    values='Amount')

# Update charts
sunburst.update_layout(margin={'l': 0, 'b': 0, 't': 0, 'r': 0})
table.update_layout(margin={'l': 20, 'b': 0, 't': 0, 'r': 0})
bar.update_layout(margin={'l': 20, 'b': 20, 't': 30, 'r': 20},
                  barmode='stack',
                  yaxis={'categoryorder': 'total descending'})

# Create Dash
app = Dash(__name__)
app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([

        html.Div([
            html.H1(children='Cost Category'),
            dcc.Graph(
                id='graph1',
                figure=table
            ),
        ], style={'width': '25%', 'float': 'left', 'display': 'inline-block'}),

        html.Div([
            html.H1(children='"'),
            dcc.Graph(
                id='graph2',
                figure=bar
            ),
        ], style={'width': '25%', 'display': 'inline-block'}),

        html.Div([
            html.H1(children='Groups'),
            dcc.Graph(
                id='graph3',
                figure=sunburst
            ),
        ], style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True,
                   use_reloader=False
                   )