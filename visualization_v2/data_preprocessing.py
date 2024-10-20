import pandas as pd
import os



def preprocess_dfs():
    chat_questions_df = pd.read_csv('completed_test_chat_sentiment.csv')
    completion_questions_df = pd.read_csv('completed_completion_chat_sentiment.csv')

    chat_questions_df['sovereignt'] = ''
    completion_questions_df['sovereignt'] = ''


    chat_questions_df['response_top_p_1'] = chat_questions_df['response_top_p_1'].astype(str)
    chat_questions_df['response_top_p_0'] = chat_questions_df['response_top_p_0'].astype(str)
    completion_questions_df['response_top_p_1'] = completion_questions_df['response_top_p_1'].astype(str)
    completion_questions_df['response_top_p_0'] = completion_questions_df['response_top_p_0'].astype(str)

    country_list = ['China', 'India', 'United States of America', 'Norway', 'Saudi Arabia', 'South Africa']


    for country in country_list:
        # Check if 'country' is in the 'question' column for each DataFrame
        chat_questions_df.loc[chat_questions_df['question'].str.contains(country), 'sovereignt'] = country
        completion_questions_df.loc[completion_questions_df['question'].str.contains(country), 'sovereignt'] = country
    return chat_questions_df, completion_questions_df