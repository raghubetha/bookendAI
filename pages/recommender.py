
import dash, ast
from dash import dcc, html, callback, Output, Input, State #Clientside_callback, ClientFunction
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from shared_data import df_works, df_reviews, df_users_dummy,df_user_recs # Import your data

# --- Register Page ---

dash.register_page(__name__, name='Your Profile')

# --- Page Layout ---
layout = dbc.Container([
    # "Login" Section
    dbc.Row(
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("User Profile"),
                dbc.CardBody([
                    html.P("Enter your User ID to see your personalized dashboard."),
                    dbc.Input(id='user-id-input', placeholder="Enter User ID...", type='text', className="mb-2"),
                    dbc.Button("Load Profile", id='load-profile-button', color="primary"),
                ])
            ]),
            width=12,
            lg=6,
            className="mx-auto mb-4"  # Center the login box on large screens
        )
    ),

    # This Div will be updated by the callback after "login"
    dcc.Loading(html.Div(id='profile-content-area'))

], fluid=True)

# --- Callback to Update Page Content ---
@callback(
    Output('profile-content-area', 'children'),
    Input('load-profile-button', 'n_clicks'),
    State('user-id-input', 'value'), # Use State to get the value only when the button is clicked
    prevent_initial_call=True
)
def update_profile_page(n_clicks, user_id):
    if not user_id:
        return dbc.Alert("Please enter a User ID.", color="warning")

    # --- Filter data for the selected user ---
    real_id =df_users_dummy[df_users_dummy['dummy_id'] == user_id]['user_id'].values[0]
    user_reviews_df = df_reviews[df_reviews['user_id'] == real_id]
    user_name = df_users_dummy[df_users_dummy['dummy_id'] == user_id]['name'].values[0]

    if user_reviews_df.empty:
        return dbc.Alert(f"No data found for User ID: {user_id}", color="danger")

    # Merge with book data to get details
    user_books_df = pd.merge(user_reviews_df, df_works, on='work_id')

    # --- 1. Calculate KPI Metrics ---
    books_read = user_books_df['work_id'].nunique()
    avg_user_rating = user_books_df['rating'].mean()
    # Placeholder for reading time - you would calculate this from your timedelta column
    avg_reading_time = "15 Days"
    try:
        fav_genre = user_books_df['genres'].str.split(',').explode().str.strip().mode()[0]
    except (KeyError, IndexError):
        fav_genre = "N/A"

    kpi_cards = dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H4(books_read), html.P("Books Read")])), className="text-center"),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4(f"{avg_user_rating:.2f} ★"), html.P("Your Avg. Rating")])),
                className="text-center"),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4(avg_reading_time), html.P("Avg. Reading Time")])),
                className="text-center"),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4(fav_genre), html.P("Favorite Genre")])), className="text-center"),
    ])

    # --- 2. Create Virtual Bookshelf (Recently Read) ---
    user_books_df['date_added']=pd.to_datetime(user_books_df['date_added'], errors='coerce')
    recent_books = user_books_df.sort_values('date_added', ascending=False).head(20)
    bookshelf_cards = [
        dbc.Col(
            dbc.Card([
                dbc.CardImg(src=row['image_url'],
                            top=True,
                            style={'height': '250px', 'objectFit': 'contain'}),
                dbc.CardBody([
                    dcc.Link(html.H6(row['original_title'], className="card-title"),
                            href = f"/book_dive/{row['work_id']}", className = 'text-black fw-bold me-2'
                             ),
                    html.P(f"You rated: {row['rating']} ★", className="small")
                ], className='border-0')
            ], className = 'border-0'),
            width=6, lg=1
        ) for i, row in recent_books.iterrows()
    ]
    bookshelf = dbc.Row(bookshelf_cards, className='flex-nowrap', style={'overflowX': 'auto', 'padding': '15px'})

    book_id_string = df_user_recs[df_user_recs['user_id'] == real_id]['book_id'].iloc[0]
    recshelf_list=ast.literal_eval(book_id_string)
    #print(recshelf_list)
    recshelf_cards = [
        dbc.Col(
            dbc.Card([
                dbc.CardImg(src=df_works[df_works['work_id']==id]['image_url'],
                            top=True,
                            style={'height': '250px', 'objectFit': 'contain'}),
                dbc.CardBody([
                    dcc.Link(html.H6(df_works[df_works['work_id']==id]['original_title'], className="card-title"),
                             href=f"/book_dive/{df_works[df_works['work_id']==id]['work_id']}", className='text-black fw-bold me-2'),
                    #html.P(f"You rated: {row['rating']} ★", className="small")
                ], className='border-0')
            ], className='border-0'),
            width=6, lg=1
        ) for id in recshelf_list
    ]
    recshelf = dbc.Row(recshelf_cards, className='flex-nowrap', style={'overflowX': 'auto', 'padding': '15px'})


    # --- 3. Create Personalized Visualizations ---
    # Rating Habits Bar Chart

    rating_counts = user_books_df['rating'].value_counts().sort_index()
    ratings_fig = px.bar(
        rating_counts,
        title="Your Rating Habits",
        labels={'value': 'Number of Books', 'index': 'Star Rating'},
        color= 'value', color_continuous_scale=['#B0B8C0', '#4A6D8C']
    )
    ratings_fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor='white',
        margin=dict(t=40, l=0, r=0, b=0),
    )


    # Reading Tastes Sunburst
    # Create a simplified genre column for the sunburst
    user_books_df['main_genre'] = user_books_df['genres'].str.split(',').str[0].str.strip()
    tastes_fig = px.sunburst(
        user_books_df.dropna(subset=['main_genre', 'author']),
        path=['main_genre', 'author'],
        title="Your Reading Tastes: Genres & Authors"
    )
    tastes_fig.update_layout(margin=dict(t=40, l=0,r=0, b=0))

    visualizations = dbc.Row([
        dbc.Col(dcc.Graph(figure=ratings_fig), width=12, md=4),
        dbc.Col(dcc.Graph(figure=tastes_fig), width=12, md=4),
    ], className="mt-4")

    # --- 4. (Simulated) Recommendations ---
    # In your real app, these would come from your ML models
    # collab_recs = dbc.Row([

    #])  # Placeholder for collaborative filtering cards
    #content_recs = dbc.Row([...])  # Placeholder for content-based cards'''

    # --- Assemble the Final Layout for the user ---
    return html.Div([
        html.H2(f"Welcome, {user_name}"),
        html.Hr(),
        kpi_cards,
        html.H3("Your Recent Reads", className="mt-4"),
        bookshelf,
        html.Hr(),
        visualizations,
        html.H3("Top Picks For You", className="mt-4"),
        recshelf,

       # html.H3("Because You Read...", className="mt-4"),
        #content_recs,  # Placeholder
    ])