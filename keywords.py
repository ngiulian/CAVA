from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string



def find_keywords(df, t):
    df_curr = df[df['type']== t].reset_index()

    # Sample responses for different countries
    responses_p0 = df_curr['response_top_p_0'].to_list()
    responses_p1 = df_curr['response_top_p_1'].to_list()
    responses = [a +' ' + b for a,b in zip(responses_p0, responses_p1)]#responses_p0 + responses_p1

    question = str(df_curr['question'].to_list()[0])
    question = "".join([c for c in question if c not in string.punctuation])
    question_words = question.split(' ')
    question_words = [w.lower() for w in question_words]

    print(question_words)

    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    all_tokens = [word.lower() for response in responses for word in word_tokenize(response) if word.isalpha() and word.lower() not in stop_words and word.lower() not in question_words]

    # Count word frequencies
    word_freq = Counter(all_tokens)

    # Aggregate and find top keywords
    top_keywords = word_freq.most_common(5)  # Adjust the number as needed

    keyword_dict = {}
    for keyword, _ in top_keywords:
        indices = [i for i, response in enumerate(responses) if keyword in word_tokenize(response.lower())]
        # Get the corresponding 'sovereignt' values for those rows
        sovereign_values = df_curr.iloc[indices]['sovereignt'].to_list()
        keyword_dict[keyword] = set(sovereign_values)

    return keyword_dict