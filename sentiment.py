from transformers import pipeline
import pandas as pd
import numpy as np

class SentimentAnalyzer:
    def __init__(self, sentiment_pipe):
        self.sentiment_pipe = sentiment_pipe
    
    def hex_color_gen(self, label_score_tuples):
        res = []
        for label, score in label_score_tuples:
            if label == 'negative':
                score = -1 * score
            elif label == 'neutral':
                score = 0.0
            
            red = (255, 0, 0)
            yellow = (255, 255, 0)
            green = (0, 255, 0)

            # Interpolate between the colors based on the score
            if score <= -1:
                color = '#%02x%02x%02x' % red
            elif score <= 0:
                # Interpolate between red and yellow for negative scores
                ratio = score + 1
                interpolated_color = tuple(int((1 - ratio) * red[i] + ratio * yellow[i]) for i in range(3))
                color = '#%02x%02x%02x' % interpolated_color
            else:
                # Interpolate between yellow and green for positive scores
                ratio = score 
                interpolated_color = tuple(int((1 - ratio) * yellow[i] + ratio * green[i]) for i in range(3))
                color = '#%02x%02x%02x' % interpolated_color
            res.append(color)
        return res
    
    def add_sentiment_to_response_df(self, df, response_column, sentiment_columns):
        texts = df[response_column].to_list()
        model_output = self.sentiment_pipe(texts)
        labels = [d['label']  for d in model_output]
        scores = [d['score'] for d in model_output]
        df[sentiment_columns['label']] = labels
        df[sentiment_columns['score']] = scores
        df[sentiment_columns['color']] = self.hex_color_gen(list(zip(labels,scores)))


if __name__ == '__main__':
    model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    sentiment_pipe = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)
    SA = SentimentAnalyzer(sentiment_pipe)
    model_name = "Qwen1.5-72B-Chat"
    df = pd.read_csv(f'data/responses/test/{model_name}_responses.csv')
    for prompt_verion in [0, 1, 2]:
        sentiment_columns = {'label': f'sentiment_label_verion_{prompt_verion}', 'score': f'sentiment_score_verion_{prompt_verion}', 'color': f'sentiment_color_verion_{prompt_verion}'}
        SA.add_sentiment_to_response_df(df, f'response_open_ended_version_{prompt_verion}', sentiment_columns)
        print(f"finishd {prompt_verion}")
    df.to_csv(f'data/responses/test/{model_name}_responses.csv', index=False)


