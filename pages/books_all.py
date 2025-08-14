import dash
from dash import dcc, html, callback, Output, Input
from shared_data import df_works, df_reviews
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# --- Register Page ---
dash.register_page(__name__, path="/books_all",name='Books', nav=False)

book_options = df_works['original_title'].unique().tolist()
Author_list = 'All'
Genre_list = 'All'
Literary_era = 'All'

#Create table function
def table_generator(df):
    table_header = [
        html.Thead(html.Tr([html.Th(''), html.Th('')]))
    ]

    table_body = [
        html.Tbody([
            html.Tr([
                # Book Image
                html.Td(
                    html.Div(
                        [html.Img(src=row['image_url'], height='60px', className='me-2 rounded'), ],
                        className='d-flex align-items-center'
                    )
                ),
                html.Td(
                    (html.Div([

                        html.P([
                            dcc.Link(
                                html.Span(row['original_title'], className='text-black fw-bold me-2'),
                                href=f"/book_dive/{row['work_id']}", className='text-black fw-bold me-2'
                            ),
                            html.Span(html.I(row['author'], className='small text-info me-2')),
                            html.Span(html.I(row['original_publication_year'], className='text-info'))
                        ], className='mb-0'),
                        html.I(html.P(row['genres'], className='small mb-0 mt-0')),
                    ])
                    )
                )

            ]) for index, row in df.iterrows()
        ])
    ]

    return dbc.Table(table_header + table_body, hover=True, bordered=False, striped=False)


layout = dbc.Container([#Contained Begin
    dbc.Row([#Row 1 Begin
        dbc.Col( #Col 1 Begin
            dbc.Card(
                dbc.CardBody([
                    html.H4(Author_list, id='author',className='card-title text-primary'),
                    html.P("Author(s)", className='card-text'),
                ]), className = 'text-center'
            ), width=4
        ), #Col 1 End
        dbc.Col( # Col2 Begin
            dbc.Card(
                dbc.CardBody([
                    html.H4(Genre_list, id='genre',className='card-title text-primary'),
                    html.P("Genre(s)", className='card-text'),
                ]), className = 'text-center'
            ), width=4
        ), # Col 2 End
        dbc.Col(# Col 3 Begin
            dbc.Card(
                dbc.CardBody([
                    html.H4(Literary_era, id='era',className='card-title text-primary'),
                    html.P("Literary Era(s)", className='card-text'),
                ]), className = 'text-center'
            ), width=4
        ) # Col 3 End
    ], className='mb-4'), # Row 1 End

    html.Hr(), # Horizontal Line

    dbc.Row([ # Row 2 Begin
        dbc.Col( # Col 1 Begin --- Filter SideBar ---
            html.Div([
                html.H4("Filters", className='mb-3'),
                html.Label('Sort by:', className='fw-bold'),
                dcc.Dropdown(
                    id ="sorting-dd",
                    options=[
                        {'label': 'Popularity', 'value': 'popularity'},
                        {'label': 'Reviews', 'value': 'reviews'},
                             ],
                    multi=False,
                    placeholder="Select an option",
                    clearable=True

                ),

            ]),
            width = 3,

        ), #Col 1 End
        dbc.Col(# Col 2 Begin
            dcc.Loading(
                html.Div(
                    id='table-content-area2',
                    children=[],
                )
            ),
            width = 9,
            style={'height': '85vh', 'overflow': 'auto'} #vh = viewport height

        )
    ]) # Row 2 End
])#Container End

@callback(
    Output('table-content-area2', 'children'),
    Output('genre', 'children'),
    Output('author', 'children'),
    Output('era', 'children'),
    Input('shared-filter-store', 'data')
)

def update_table(stored_data):
    print("Data from store:",stored_data)
    author_list="Multi-Authors"
    genre_list="Multi-Genres"
    era_list="Multi-Era"
    if not stored_data or (
            not stored_data.get('genres') and
            not stored_data.get('authors') and
            not stored_data.get('years')
    ):
        return "Go to the Explorer page to select filters", genre_list, author_list, era_list

    filtered_df = df_works.copy()

    if stored_data.get('genres'):
        filter_pattern = '|'.join(stored_data['genres'])
        filtered_df = filtered_df[filtered_df['genres'].str.contains(filter_pattern, case=False, na=False)]

    if stored_data.get('authors'):
        filtered_df = filtered_df[filtered_df['author'].isin(stored_data['authors'])]
        author_list = "|".join(stored_data['authors'])


    if stored_data.get('years'):
        years = stored_data['years']
        filtered_df = filtered_df[
            (filtered_df['original_publication_year'] >= years[0]) &
            (filtered_df['original_publication_year'] <= years[1])
            ]
        era_list= stored_data['era'].capitalize()

    if filtered_df.empty:
        return "No books match the selected filters."

    return table_generator(filtered_df), genre_list,author_list,era_list