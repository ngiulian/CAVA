from sklearn.feature_extraction.text import TfidfVectorizer
from stopwords import stopwords_list
import re


class TFIDFAnalyzer:
    def __init__(self):
        self.model = TfidfVectorizer()
        self.stopwords = set(stopwords_list)

    def compute_tfidf_words(self, country_list, corpus, threshold):
        # country_list[i] is reponse for corpus[i]
        res = self.model.fit_transform(corpus).toarray()
        vocab = self.model.get_feature_names_out()
        assert len(res) == len(country_list)

        country_to_words = dict()
        for country, results in zip(country_list, res):
            vocab_results = dict(zip(vocab, results))
            final_words = [w for w, score in vocab_results.items() if w not in self.stopwords and w not in country.lower() and score >= threshold]
            country_to_words[country] = final_words
        return country_to_words
    
    def underline_tfidf_words(self, df, response_column, country_column, country_to_words):

        def add_u_tags(row, column_name):
            word_list = country_to_words[row[country_column]]
            original_text = row[column_name]
            for word in word_list:
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                original_text = pattern.sub(lambda x: f"<u>{x.group()}</u>", original_text)
            return original_text
        
        df[f'added_u_{response_column}'] = df.apply(add_u_tags, axis=1, column_name=response_column)



    def compute_and_underline_tf_idf_words(self, df, response_columns_name, country_column, threshold):
        country_list = df[country_column].to_list()
        response_columns = list(response_columns_name.keys())
        df['group_responses'] = df[response_columns].apply(lambda x: ' '.join(x), axis=1)
        corpus = df['group_responses'].to_list()
        country_to_words = self.compute_tfidf_words(country_list, corpus, threshold)

        for response_column in response_columns:
            self.underline_tfidf_words(df, response_column, country_column, country_to_words)

        res = []
        for _, row in df.iterrows():
            curr_country = row[country_column].replace(' ', '_').replace('.','').replace("'", '').replace('-','').lower()
            new_response = {'country': row[country_column], 'layer_id': curr_country}
            new_response['selected_words'] = country_to_words[row[country_column]]
            updated_responses = {}
            for response_column in response_columns:
                updated_responses[response_columns_name[response_column]] = f"""<span id="{response_columns_name[response_column]}">{row[f'added_u_{response_column}'].replace("`", "'")}</span> <br>"""
            new_response['responses'] = updated_responses
            res.append(new_response)
        return sorted(res, key=lambda x: x['country'])
    
    
            
            









