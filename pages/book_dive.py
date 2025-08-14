import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import ast, io, base64
from wordcloud import WordCloud, STOPWORDS
from urllib.parse import parse_qs, urlparse
from shared_data import df_works, df_reviews, similar_books_df, df_AI_review_summary, df_users_dummy  # Assumes df_works is in your shared_data.py

# --- Register Page ---
dash.register_page(__name__, path_template="/book_dive/<work_id>", name="Book Deep Dive", nav=False)

# --- word cloud function ---
def create_wordcloud(data_df, column_name):
    """Generates a word cloud image from a DataFrame column and returns it as a base64 string."""
    # Combine all text into a single string
    text = ' '.join(str(review) for review in data_df['review_text'].dropna())

    my_stopwords = set(STOPWORDS)
    my_stopwords.update(['book','read','story','character'])
    if not text:
        return None # Return None if there's no text to process

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords= my_stopwords, # You can add a set of stopwords here
        colormap='inferno',

    ).generate(text)

    # Convert the word cloud image to a base64 string
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

# --- Page Layout ---
layout = dbc.Container([
    # This component reads the URL
    dcc.Location(id='book-dive-url', refresh=False),

    # Back button to return to the main explorer
    dcc.Link(
        dbc.Button("← Back to Explorer", color="secondary", className="mb-4"),
        href="/"
    ),

    # Main content area will be populated by the callback
    html.Div(id='book-detail-content-area')

], fluid=True)


# --- Callback to Update Page Content ---
@callback(
    Output('book-detail-content-area', 'children'),
    Input('book-dive-url', 'pathname')  # Triggered by URL change
)
def update_book_details(pathname):
    # Extract the work_id from the URL, e.g., "/book_dive/123" -> "123"
    try:
        selected_work_id = int(pathname.split('/')[-1])
    except (ValueError, IndexError):
        return html.H4("Invalid book ID in URL.")

    # Find the selected book's data
    if selected_work_id not in df_works['work_id'].values:
        return html.H4("Book ID not found in dataset.")

    book_data = df_works[df_works['work_id'] == selected_work_id].iloc[0]


    # --- Prepare Data for Charts ---
    # Rating Distribution Data
    rating_cols = ['5_star_ratings', '4_star_ratings', '3_star_ratings', '2_star_ratings', '1_star_ratings']
    rating_values = list(book_data[rating_cols].values)
    rating_labels = ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star']
    ratings_fig = px.bar(
        x=rating_values, y=rating_labels, orientation='h',
        labels={'x': 'Number of Ratings', 'y': ''},
        color = rating_values, color_continuous_scale=['#B0B8C0', '#4A6D8C']#, '#4A6D8C']
    )
    ratings_fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor='white',
    )


    reading_time = pd.to_timedelta(df_reviews[df_reviews['work_id']==selected_work_id]['Avg_Reading_Time'].iloc[0])

    # --- Sentiment Data ---
    # --- Filter reviews for the selected book ---
    # The sentiment column contains dictionaries like {'neg': 0.1, 'neu': 0.625, ...}
    reviews_for_book = df_reviews[df_reviews['work_id'] == selected_work_id]

    # ---  Prepare Sentiment Data ---
    sentiment_fig = {}  # Default to an empty figure
    if not reviews_for_book.empty:
        # 1. Expand the dictionary column into a new DataFrame
        sentiment_dicts = reviews_for_book['sentiment'].apply(ast.literal_eval)
        sentiment_scores_df = sentiment_dicts.apply(pd.Series)

        # 2. Calculate the average score for each sentiment category
        avg_sentiment = sentiment_scores_df[['pos', 'neu', 'neg']].mean()

        # 3. Prepare data for the pie chart
        sentiment_data_for_chart = pd.DataFrame({
            'sentiment': ['Positive', 'Neutral', 'Negative'], #
            'score': [avg_sentiment['pos'], avg_sentiment['neu'], avg_sentiment['neg']]
        })

        # 4. Create the pie (donut) chart
        sentiment_fig = px.pie(
            sentiment_data_for_chart,
            names='sentiment',
            values='score',
            #title='Average Review Sentiment',
            hole=0.4,
            color='sentiment',
            color_discrete_sequence=['#7492AA','rgb(179,177,169)','#F2D0A7']#{''#7492AA','rgb(180,170,180)','#F2D0A7'}
        )
        sentiment_fig.update_traces(textinfo='percent+label')
        sentiment_fig.update_layout(showlegend=False)

    # --- Prepare Similar Books ---
    # Assumes 'similar_books' is a list of work_ids stored as a string
    try:
        # Safely evaluate the list
        similar_book_string = similar_books_df[similar_books_df['work_id'] == selected_work_id]['similar_books'].to_list()[0]
        similar_book_ids = ast.literal_eval(similar_book_string)
        similar_books = df_works[df_works['work_id'].isin(similar_book_ids)].head(5)
        similar_books_cards = [
            dbc.Col(
                dbc.Card([
                    dbc.CardImg(src=row['image_url'], top=True, style={'height': '250px', 'objectFit': 'contain'}),
                    dbc.CardBody(
                        dcc.Link(
                            html.Span(row['original_title'], className='text-black fw-bold me-2'),
                            href=f"/book_dive/{row['work_id']}", className='text-black fw-bold me-2'
                        ),
                    )
                ],  style={'height':'300px', 'width':'200px'},className='border-0'),
                width=6, lg=2
            ) for index, row in similar_books.iterrows()
        ]
    except (SyntaxError, NameError):
        similar_books_cards = dbc.Col(html.P("No similar books available."))

    # --- Generate Word Cloud ---
    wordcloud_img_src = create_wordcloud(reviews_for_book, 'review_text')

    # --- Generate Review Table ---
    df_reviews_book = df_reviews[df_reviews['work_id'] == selected_work_id].copy()
    df_reviews_book['date_added'] = pd.to_datetime(df_reviews_book['date_added'], errors='coerce')
    df_reviews_book=df_reviews_book.sort_values(by=['date_added'], ascending=False).reset_index(drop=True).head(20)
    df_reviews_book['rating'] = df_reviews_book['rating'].fillna(0).astype(int)

    table_body=[
                html.Tbody([
                    #List comprehension generates rows (html.Tr)
                    html.Tr([
                        #First column: Reviewer and Review Text
                        html.Td(
                            html.Div([
                                     html.P([html.I(className='fas fa-star small', style={'color':'#FFD700', 'marginRight':'2px'}) for _ in range(row['rating'])],className='mb-0'),
                                     html.I(
                                         f"Reviewed by {df_users_dummy[df_users_dummy['user_id']==row['user_id']]['name'].iloc[0]} on  {row['date_added'].strftime('%b %d, %Y')}",
                                         className="text-info small mt-0",
                                         ),

                                    html.P(row['review_text'], className = 'small mb-0')
                            ])

                        ),


                    ]) for index, row in df_reviews_book.iterrows()

                ])
    ]

    review_table = dbc.Table(table_body, striped=False, bordered = False, hover = True, className="mt-3")





    # --- Assemble the Final Layout ---
    return html.Div([
        # Header Section
        dbc.Card(dbc.CardBody(dbc.Row([
                                            dbc.Col(dbc.Card([dbc.CardImg(src=book_data['image_url'], style={'height':'350px', 'width':'220px' }, className="img-fluid rounded border-0")], className='border-0'), width=12, lg=2, className="ps-lg-4"),
                                            dbc.Col([
                                                             html.H1(book_data['original_title']),
                                                             html.H4(f"by {book_data['author']}", className="text-muted"),
                                                             html.Hr(),
                                                             dbc.Row([
                                                                dbc.Col(html.Div([html.H5("Avg. Rating"), html.P(f"{book_data['avg_rating']:.2f} ★")])),
                                                                dbc.Col(html.Div([html.H5("Total Ratings"), html.P(f"{book_data['ratings_count']:,}")])),
                                                                dbc.Col(html.Div([html.H5("Published"), html.P(int(book_data['original_publication_year']))])),
                                                                dbc.Col(html.Div([html.H5("Pages"), html.P(int(book_data['num_pages']))])),
                                                                dbc.Col(html.Div([html.H5("Average Reading Time"), html.P(f"{reading_time.days} days, {int(reading_time.seconds/3600)} hours")])),
                                                            ]),
                                                            html.Hr(),
                                                            html.P(book_data['description'])
                                            ], width=12, lg=10, className="ps-lg-4")
        ], align="center")), className="mb-4 border-0"),

        # Charts Section
        dbc.Card(dbc.CardBody(dbc.Row([
                                        dbc.Col(html.Div(id='grqph1',
                                                         children=[
                                                                    html.H4('Rating Distribution', className='mb-0'),
                                                                    dcc.Graph(figure=ratings_fig, className='mt-0'),
                                                        ]
                                                ),width=12, md=4, className='mb-4 border-0'
                                        ),
                                        dbc.Col(html.Div(id='content2',
                                                           children=[

                                                               html.H4('AI Summary of Reviews:', className='mb-2'),
                                                               html.I(df_AI_review_summary[df_AI_review_summary['work_id']==selected_work_id]['review_text_summary'], className='text-primary fw-bold',  style={'fontWeight':'bold'}),
                                                               html.Hr(),
                                                               html.H5 ('Recent Reviews'),
                                                               html.Div(id='table1',
                                                                        children=[review_table],
                                                                        className='p-0', style={'height': '20vh', 'overflow': 'auto'}
                                                               ),


                                                           ]), width=12, md=4, className='mb-4 border-0',

                                        ),
                                        dbc.Col(
                                            html.Div(id='graph2',
                                                     children=[
                                                         html.H4('Average Reviewers Sentiment', className='mb-2'),
                                                         dcc.Graph(figure=sentiment_fig,
                                                                   className='fluid rounded border-0')
                                                     ]), width=12, md=4, className='mb-4 border-0'


                                        )


        ])), className='border-0'),

        # Similar Books Section
        html.H4("You Might Also Like..."),
        html.Hr(),
        dbc.Row(similar_books_cards),

    ])
