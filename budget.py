import pandas as pd
from numpy import select
import plotly.graph_objects as go
from dash import Dash, dcc, html
import plotly.express as px

# Connect to GoogleSheets (example operations)
sheet_id = '1ylnURhd2nLlszYNLdqptqZoFudwUILnnwThInmMCqkU'
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

# Create Expenses DataFrame
expenses_df = df[df['Payment_Amount'] <= 0].sort_values('Payment_Amount', ascending=True)
expenses_df['Amount'] = abs(df['Payment_Amount'])  # For Sunburst chart

# Group by macro-categories
home_categories = ['ЖКХ',
                   'Дом'
                   ]
food_categories = ['Супермаркеты',
                   'Кофе',
                   'Рестораны'
                   ]
health_categories = ['Аптеки,'
                     'Красота и здоровье',
                     'Медицина',
                     'Мед. услуги',
                     'Аптеки',
                     'Красота и здоровье'
                     ]
transport_categories = ['Транспорт',
                        'Автобусы',
                        'Такси',
                        'Авиабилеты'
                        ]
longtermbyus_categories = ['Техника',
                           'Одежда и обувь'
                           ]
education_categories = ['Книги',
                        'Образование'
                        ]
investments_categories = ['Инвестиции'

                          ]
garbage_categories = ['Алкоголь, табак',
                      'Фастфуд'
                      ]
internet_categories = ['Мобильная связь',
                       'Домашний интернет',
                       'Подписки'

                       ]
presents_categories = ['Подарки',
                       'Цветы',
                       'Семья'
                       ]
onetimebyus_categories = ['Госуслуги',
                          'Юридические услуги',
                          ]
credits_categories = ['Кредитка',
                      'Займы'
                      ]

expenses_df['Group'] = select(
    [
        expenses_df['Category'].isin(home_categories),
        expenses_df['Category'].isin(food_categories),
        expenses_df['Category'].isin(health_categories),
        expenses_df['Category'].isin(transport_categories),
        expenses_df['Category'].isin(longtermbyus_categories),
        expenses_df['Category'].isin(education_categories),
        expenses_df['Category'].isin(investments_categories),
        expenses_df['Category'].isin(garbage_categories),
        expenses_df['Category'].isin(internet_categories),
        expenses_df['Category'].isin(presents_categories),
        expenses_df['Category'].isin(onetimebyus_categories),
        expenses_df['Category'].isin(credits_categories)
    ],
    [
        'Home',
        'Food',
        'Selfcare and Health',
        'Transport',
        'Long-term Buys',
        'Education and Seft-dev',
        'Investments',
        'Garbage',
        'Internet',
        'Presents',
        'One-time Buys',
        'Credits'
    ],
    default='Unknown'
)

# Print df to check
print(expenses_df)

# Create charts
table = go.Figure(data=[go.Table(
    header=dict(
        values=['Category', 'Expenses'],
        fill_color='lavender',
        align='left', font=dict(color='black', size=12)
    ),
    cells=dict(
        values=[expenses_df.Category, expenses_df.Payment_Amount],
        align='left', font=dict(color='black', size=11)
    )
)])

bar = go.Figure(go.Bar(
    name='Expenses',
    x=expenses_df.Payment_Amount,
    y=expenses_df.Category,
    orientation='h')
)

sunburst = px.sunburst(
    expenses_df,
    path=['Group', 'Category'],
    values='Amount'
)

total = go.Figure(go.Indicator(
    mode="number",
    value=sum(expenses_df.Payment_Amount))
)

# Update charts
sunburst.update_layout(margin={'l': 0, 'b': 0, 't': 0, 'r': 0})
table.update_layout(margin={'l': 20, 'b': 0, 't': 0, 'r': 0},
                    height=1000)
bar.update_layout(margin={'l': 20, 'b': 20, 't': 30, 'r': 20},
                  yaxis={'categoryorder': 'total descending'})
total.update_layout(margin={'l': 0, 'b': 0, 't': 0, 'r': 0})

# Create Dash
app = Dash(__name__)
app.layout = html.Div([
    html.H1('Budget Board'),

    html.Div([
        html.H2('Expense Categories'),
        dcc.Graph(
            id='table',
            figure=table
        ),
    ],  style={'width': '25%', 'float': 'left', 'display': 'inline-block'}
    ),

    html.Div([
        html.Div([
            html.H2('Total'),
            dcc.Graph(
                id='total',
                figure=total,
                style={'height': '30px'}
            )
        ], className='wrap'),
        dcc.Graph(
            id='bar',
            figure=bar
        ),
    ],  style={'width': '23%', 'display': 'inline-block'}
    ),

    html.Div([
        html.H2('Groups'),
        dcc.Graph(
            id='sunburst',
            figure=sunburst
        ),
    ], style={'width': '50%', 'float': 'right', 'display': 'inline-block'}
    ),

], style={'min-height': '100vh'})

if __name__ == '__main__':
    app.run_server(debug=True,
                   use_reloader=False
                   )
