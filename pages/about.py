
import dash
from dash import html
import dash_bootstrap_components as dbc

# --- Register Page ---
dash.register_page(__name__, name='About')


# --- Reusable Card Component for Skills ---
def skill_card(title, description):
    """Creates a styled card for a technical skill or model."""
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title text-primary"),
            html.P(description, className="card-text", style = {'white-space':'pre-wrap'} )
        ]),
        className="mb-3 border-0",
    )


# --- Page Layout ---
layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("About Bookend AI", className="text-center my-4"),
            width=12
        )
    ),

    # --- Mission Statement ---
    dbc.Row(
        dbc.Col(
            html.P(
                "Bookend AI is a dynamic dashboard designed to help readers discover their next favorite book. "
                "Leveraging over a million book reviews from Goodreads, this tool goes beyond simple genre matching "
                "to provide deep, data-driven insights and personalized recommendations.",
                className="lead text-center mb-5"
            ),
            width=10,
            className="mx-auto"
        )
    ),

    # --- Technical Deep Dive ---
    dbc.Row([
        html.H2("Technical Deep Dive", className="my-3"),


        # --- Data Processing Column ---
        dbc.Col([
            skill_card(
                "Data Processing & Feature Engineering",
                "The initial dataset of over one million reviews was cleaned and processed using Pandas. "
                "Key features like 'reading_time' were engineered by calculating the timedelta between review start and end dates. "
                "Popularity metrics such as a 'weighted rating' score were created to balance average ratings with the number of reviews, providing a more accurate measure of a book's true popularity."

            )
        ], width=12, md=4),

        # --- Recommendation Engine Column ---
        dbc.Col([
            skill_card(
                "Recommendation Engines",
                "Bookend AI provides recommendations using two powerful, independent models:\n"
                "\t1) Content-based filtering: It uses TF-IDF vectorization and cosine similarity to analyze book descriptions and genres, finding titles that are textually and thematically similar.\n "
                "\t2) Collaborative filtering: This model uses Singular Value Decomposition (SVD) to learn latent user and book features from users' personal rating history and patterns of other readers to provide truly personalized recommendations. \n"
                "This dual approach allows users to discover new books either by exploring titles similar to a known favorite or by receiving personalized suggestions based on their own reading profile."
            )
        ], width=12, md=4),

        # --- NLP Column ---
        dbc.Col([
            skill_card(
                "Natural Language Processing (NLP)",
                "To extract deeper insights from review text, this project uses two NLP techniques. \n "
                "\t 1) Sentiment analysis is performed using VADER to classify reviews as positive, neutral, or negative. \n"
                "\t 2) Abstractive summarization is implemented using a pre-trained Transformer model (BART) from the Hugging Face ecosystem, providing human-like summaries of reader consensus.\n"
            ),
        ], width=12, md=4, className='border-0'),
    ]),

    html.Hr(className="my-5"),

    # --- How to Use Section ---
    dbc.Row([
        dbc.Col([
            html.H2("How to Use This Dashboard", className="mb-3 my-3"),
            html.Ul([
                html.Li(html.P([html.Strong("Explorer Page: "),
                                "Get a high-level overview of the dataset. Filter by genre, author, or publication year to see dynamic updates on the most reviewed, most popular, and hidden gem books. Clicking on any book will take you to Book Deep Dive Page. This page provides a detailed report on that book, including rating breakdowns, review sentiment analysis, and similar book recommendations."])),
                html.Li(html.P([html.Strong("Your Profile Page: "),
                                "Enter a user ID to see a personalized dashboard, which includes your reading stats, a virtual bookshelf, and recommendations tailored to your reading history. (Note: User IDs are in the format User_xxxxx, for example: User_00001 or User_12345)."])),
            ])
        ], width=12, lg=12, className="mx-auto")

    ])

], className="mb-5")