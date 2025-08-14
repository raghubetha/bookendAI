import uuid
import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from shared_data import df_works, df_reviews # Loading the dataframe from shared_data.py directly.



# --- Register Page ---
# This tells Dash that this is a page in your app
# The path is the URL, and the name is the text that will appear in the navigation

dash.register_page(__name__, path='/', name='Explorer')

# --- Calculate Key Metrics ---
total_books = df_works['work_id'].nunique()
total_reviews = df_works['reviews_count'].sum()
overall_ratings =df_works['avg_rating'].mean()
total_users = df_reviews['user_id'].nunique()

# --- Prepare Filter Options ---
genres_list = df_works['genres'].unique().tolist()
genre_options = sorted(set([genre.strip().capitalize() for lst in genres_list for genre in lst.split(',')]))
author_options=sorted(df_works['author'].unique())
min_year = int(df_works['original_publication_year'].min())
max_year = int(df_works['original_publication_year'].max())

# --- Function to Generate Book Tables ---
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





# --- Initiate and Estimate Variables for Popularity Score ---

C=df_works['avg_rating'].mean()
m=df_works['reviews_count'].quantile(0.9) # set minimum reviews threshold at 90th Percentile

min_review_gems = 50


# --- Generate Tabbed Tables ---

table_tabs = dbc.Tabs( #Iinitiate with empty tables they will be updated by the callback during the page load
    [
        dbc.Tab(children=[], label='Most Reviewed', className='tab'),
        dbc.Tab(children=[], label='Most Popular', className='tab'),
        dbc.Tab(children=[], label='Hidden Gems', className='tab'),
    ]
)

# --- Initiate Treemap Figure for Genres with Blank Figure ---
genre_treemap_fig = go.Figure()

# --- Publications Trends ---

#trends_df = df_works.groupby('original_publication_year').agg(book_count=('work_id', 'count'), mean_rating=('avg_rating', 'mean')).reset_index()
#publication_trends = px.bar(trends_df, x='original_publication_year', y='book_count')

# --- Page Layout ---
layout = dbc.Container([
    #First Row to add title for the page
    dbc.Row(
        [
        dbc.Col(html.H1 ("📚 Book Explorer Dashboard", className ='text-center mb-4'), width=12)
    ]
    ),

    # Second Row for the summary cards - it has four columns, one for each card
    dbc.Row(
        [
            dbc.Col(
                      dbc.Card(
                                dbc.CardBody(
                            [
                                html.H4(f'{total_books:,}',id='card-books',  className='card-title text-primary'),
                                html.P("Total Books", className='card-text'),
                            ]
                                            ),
                            className = 'text-center'
                            ), width=3


                    ),

            dbc.Col(
                    dbc.Card(
                                dbc.CardBody(
                            [
                                html.H4(f'{total_reviews:,}', id='card-reviews', className="card-title text-success", ),
                                html.P("Total Reviews", className="card-text"),
                            ]
                                            ),
                            className="text-center",
                            ),width = 3
                    ),
            dbc.Col(
                    dbc.Card(
                                dbc.CardBody(
                            [
                                html.H4(f'{overall_ratings:.2f} ★',id='card-rating', className="card-title text-warning", ),
                                html.P("Overall Avg. Rating", className="card-text"),
                            ]
                                            ),
                            className="text-center",
                            ), width=3
                    ),
            dbc.Col(
                    dbc.Card(
                                dbc.CardBody(
                            [
                                html.H4(f'{total_users:,}', id='card-users',className="card-title text-info", ),
                                html.P("Total Users", className="card-text"),
                            ]
                                            ),
                            className="text-center",
                            ), width = 3
                    )


    ], className='mb-4'
    ),
    html.Hr(), # Horizontal Line

    #Third Row for filters and Graphs
    dbc.Row([
        # --- Filter Sidebar (Left Column) ---
        dbc.Col(# first column
            html.Div([
                html.H4 ("Filters", className='mb-3'),
                html.Label("Select Genre:", className='fw-bold'),
                dcc.Dropdown(
                    id='genre-dropdown',
                    options=[{'label':genre, 'value': genre} for genre in genre_options],
                    multi=True, # allow multiple selections
                    placeholder="Select Genre (s):"
                ),
                html.Br(),
                html.Label("Select Author:", className='fw-bold'),
                dcc.Dropdown(
                    id='author-dropdown',
                    options=[{'label': author, 'value':author} for author in author_options],
                    multi=True,
                    placeholder="Select Author (s):"
                ),

                html.Br(),
                html.Label("Select a Literary Era:", className="fw-bold mt-3"), # mt-3 adds a little space above

                dcc.Dropdown(
                    id='era-dropdown',
                    options = [
                        {'label': 'Prior to 19th Century', 'value': 'pre-1800s'},
                        {'label': '19th Century', 'value': '1800s'},
                        {'label': 'Modern (1900-1945)', 'value': 'modern'},
                        {'label': 'Contemporary (1946-1999)', 'value': 'contemporary'},
                        {'label': '21st Century', 'value': '2000s'},
                    ],
                    multi=False,
                    placeholder="Select Literary Era (s):",
                    clearable = True
                ),
                html.Br(),
                html.Label("Publication Year:", className='fw-bold'),
                dcc.RangeSlider(
                    id='year-slider',
                    min=min_year,
                    max=max_year,
                    step=1,
                    value=[min_year, max_year], #Default value is the full range
                    marks={year:str(year) for year in range(min_year, max_year+1, 5)},
                    tooltip={'placement':'bottom', 'always_visible': True},
                ),

            ]),
            width = 3,
            className='big-light p-4 rounded'
        ),

        # --- Most Reviewed Books List ---
        dbc.Col( #second column
            dcc.Loading(
                dbc.Card([
                    dbc.CardBody(
                            html.Div(
                                    id='table-content-area',
                                    children=[
                                     table_tabs,
                                             ]
                            ), className='p-0'
                   ),
                    dbc.CardFooter(
                                dcc.Link(
                                    "Click here for Complete List ",
                                    href="/books_all",
                                    className='small'
                                ),
                                className='text-end bg-transparent border-0'
                    )
                ], className='border-0')
            ), width =5,
            style={'height': '85vh', 'overflow': 'auto'} #vh = viewport height
        ),

        dbc.Col(# 3rd column
            dcc.Loading(
                html.Div(
                    id = 'graph-content-area',
                    children=[#html.H4('Book Distribution by Genre'),
                            dcc.Graph(id='genre_treemap',figure=genre_treemap_fig),

                          ]
                 )
            ), width = 4

        ),

    ]),

])


# --- Callbacks ---
# A callback links inputs (like dropdowns) to outputs (like graphs)

@callback(
        Output('table-content-area', 'children'),
        Output('genre_treemap', 'figure'),
        Output('card-books', 'children'),
        Output('card-reviews', 'children'),
        Output('card-rating', 'children'),
        Output('card-users', 'children'),
        Input('author-dropdown', 'value'),
        Input('genre-dropdown', 'value'),
        Input('year-slider', 'value')
    )
def update_dashboard(selected_authors, selected_genres, selected_years):
    # Filter the DataFrame based on the dropdown selection

    filtered_df = df_works.copy()
    if selected_genres:
        filter_pattern = '|'.join(selected_genres)
        filtered_df = filtered_df[filtered_df['genres'].str.contains(filter_pattern, case=False,na=False)]
    if selected_authors:
        filtered_df = filtered_df[filtered_df['author'].isin(selected_authors)].copy()
    if selected_years:
        filtered_df = filtered_df[
            (filtered_df['original_publication_year'] >= selected_years[0]) &
            (filtered_df['original_publication_year'] <= selected_years[1])

            ]
    if filtered_df.empty:
        return html.Div(['No books match the selected filters.'], className='mb-4')


    # Calculate Tables based on the filtered_df
    top_reviewed_books = filtered_df.nlargest(5, 'reviews_count')

    v = filtered_df['reviews_count']
    R = filtered_df['avg_rating']
    filtered_df['popularity_score'] = (v/(v+m))*R + (m/(m+v))*C
    top_popular_books = filtered_df.sort_values(by=['popularity_score'], ascending=False).head(5)

    max_review_gems = filtered_df['reviews_count'].quantile(0.5)
    gems_df = filtered_df[(filtered_df['reviews_count'] >= min_review_gems) & (filtered_df['reviews_count'] <= max_review_gems)]
    top_gems_df = gems_df.sort_values(by=['avg_rating', 'reviews_count'], ascending=[False, True]).head(5)

    most_reviewed_table = table_generator(top_reviewed_books)
    most_popular_table = table_generator(top_popular_books)
    hidden_gems_table = table_generator(top_gems_df)

    table_tabs = dbc.Tabs(
        [
            dbc.Tab(most_reviewed_table,label='Most Reviewed', className='tab'),
            dbc.Tab(most_popular_table, label='Most Popular', className='tab'),
            dbc.Tab(hidden_gems_table,label='Hidden Gems', className='tab'),
        ]
    , key = str(uuid.uuid4())
    )

    # Replot the Treemap based on filtered_df
    list_genres = filtered_df['genres'].tolist()
    unpack_genres = pd.DataFrame([genre.strip().capitalize() for lst in list_genres for genre in lst.split(',')])
    genre_counts = unpack_genres.value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']
    genre_treemap_fig = px.treemap(
        genre_counts,
        path=['genre'],  # creates a root node
        values='count',
        title=' Genre Distribution of Books',
        color_discrete_sequence=px.colors.qualitative.Pastel  # set a color scheme
    )
    genre_treemap_fig.update_layout(margin=dict(t=50, r=25, b=25, l=25))

    #Update cards based on filtered_df
    books = filtered_df['work_id'].nunique()
    reviews = filtered_df['reviews_count'].sum()
    rating = filtered_df['avg_rating'].mean()
    users = df_reviews[df_reviews['work_id'].isin(filtered_df['work_id'].unique().tolist())]['user_id'].nunique()

    card_books_text = f'{books:,}'
    card_reviews_text = f'{reviews:,}'
    card_rating_text = f'{rating:.2f} ★'
    card_users_text = f'{users:,}'

    return table_tabs, genre_treemap_fig, card_books_text, card_reviews_text, card_rating_text, card_users_text


# --- Callback for Era Dropdown ---
@callback(
Output('year-slider', 'min'),
    Output('year-slider', 'max'),
    Output('year-slider', 'value'),
    Input('era-dropdown', 'value'),  # Input is now the dropdown's value
)
def update_slider_from_dropdown(selected_era):
    min_year_data = df_works['original_publication_year'].min()
    max_year_data = df_works['original_publication_year'].max()

    if not selected_era:
        # If cleared, return the full range for all properties
        return min_year_data, max_year_data, [min_year_data, max_year_data]

    # Define the new min and max based on selection
    if selected_era == 'pre-1800s':
        new_min, new_max = min_year_data, 1799
    elif selected_era == '1800s':
        new_min, new_max = 1800, 1899
    elif selected_era == 'modern':
        new_min, new_max = 1900, 1945
    elif selected_era == 'contemporary':
        new_min, new_max = 1946, 1999
    elif selected_era == '2000s':
        new_min, new_max = 2000, max_year_data
    else:
        new_min, new_max = min_year_data, max_year_data

    # The function must now return 3 values for the 3 Outputs
    # (min, max, value)
    return new_min, new_max, [new_min, new_max]

@callback(
    Output('shared-filter-store', 'data'),
    Input('genre-dropdown', 'value'),
    Input('author-dropdown', 'value'),
    Input('year-slider', 'value'),
    Input('era-dropdown', 'value'),

)
def store_filter_values(genres, authors, years, era):
    min_year_val = df_works['original_publication_year'].min()
    max_year_val = df_works['original_publication_year'].max()
    if years[0] == min_year_val and years[1] == max_year_val:
        years = None

    return {
        'genres': genres,
        'authors': authors,
        'years': years,
        'era': era
    }
