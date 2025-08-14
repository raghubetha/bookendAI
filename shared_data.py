
import pandas as pd

#Load the dataframes here

df_works = pd.read_parquet('https://storage.googleapis.com/goodread_data/works_cleaned.parquet')
df_reviews = pd.read_parquet('https://storage.googleapis.com/goodread_data/reviews_cleaned_sentiment.parquet')
similar_books_df = pd.read_parquet('https://storage.googleapis.com/goodread_data/similar_books_df.parquet')
df_AI_review_summary=pd.read_parquet('https://storage.googleapis.com/goodread_data/AItxtSummary.parquet')
df_users_dummy = pd.read_parquet('https://storage.googleapis.com/goodread_data/fake_users.parquet')
df_user_recs = pd.read_parquet('https://storage.googleapis.com/goodread_data/user_recs_collab.parquet')