import json
import openai
import pandas as pd
import re
import backoff
import os
import ast
from datetime import datetime
from sentiment import SentimentAnalyzer
from transformers import pipeline
from evaluation import ClassExtractor

OPENAI_SECRET_KEY = "" # Add OpenAI secret key here
openai.api_key = OPENAI_SECRET_KEY


class OpenAIEngine():
  def __init__(self, 
               model_name, 
               top_p       = None, 
               num_tokens  = None,
               temperature = None,
               num_samples = None, # n
               logprobs    = None,
               echo        = None,
               presence_penalty  = None,
               frequency_penalty = None,
               best_of     = None
               ):
    self.model_name = model_name
    self.top_p = top_p
    self.num_tokens = num_tokens
    self.temperature = temperature
    self.num_samples = num_samples
    self.logprobs = logprobs
    self.echo = echo
    self.presence_penalty = presence_penalty
    self.frequency_penalty = frequency_penalty
    self.best_of = best_of

  @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
  def generate(self,prompt,max_tokens,top_p,log_probs):
      """Generates text given the provided prompt text.

      This only works for the OpenAI models which support the legacy `Completion`
      API.
      """
      response = openai.Completion.create(
          model             = self.model_name,
          prompt            = prompt,
          max_tokens        = max_tokens,
          top_p             = top_p,
          logprobs          = log_probs
      )
      
      return response
    
  @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
  def chat_generate(self,
                    previous_messages,
                    top_p=1.0,
                    max_tokens=32,
                    num_samples=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.0):
    response = openai.ChatCompletion.create(
      model=self.model_name,
      messages=previous_messages,
      temperature=1.0,
      max_tokens=max_tokens,
      top_p=top_p,
      frequency_penalty=frequency_penalty,
      presence_penalty=presence_penalty,
      n=num_samples,
      logprobs=True,
      top_logprobs=20,
    )
    return response
  
def get_response(engine, prompt, is_completion, max_tokens):
    if is_completion:
        reg_response = engine.generate(prompt=prompt, max_tokens=max_tokens, top_p=0, log_probs=6)
    else:
        reg_response = engine.chat_generate(
            previous_messages=[{
                "role": "user",
                "content": prompt
                }],
            max_tokens=max_tokens,
            top_p=0
        )
    return reg_response
  
def build_responses(engine, questions_df, responses_dir, output_csv, is_completion):
    for idx, row in questions_df.iterrows():
        if (idx % 100 == 0):
            print(idx)
        question_id = row['question_id']
  
        prompts = row['question']

        prompts = ast.literal_eval(prompts)
        responses = []
        for i, prompt in enumerate(prompts):
            reg_response = get_response(engine, prompt, is_completion)
            responses.append(reg_response['choices'][0]['message']['content'])
        
            with open(f'{responses_dir}/q_{question_id}_{i}.json', "w") as outfile:
                json_object = json.dumps(reg_response.to_dict(), indent=4)
                outfile.write(json_object)
        questions_df.loc[idx, 'responses'] = responses
    

 
    todays_date = datetime.today().strftime('%Y-%m-%d')
    questions_df['date_asked'] = todays_date

    model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)
    sa = SentimentAnalyzer(sentiment_task)
    sa.add_sentiment_to_response_df(questions_df, 'response_top_p_0', 'response_top_p_1')

    ce = ClassExtractor()
    ce.add_classes(questions_df, 'response_top_p_0', 'response_top_p_1')
    

    questions_df.to_csv(output_csv, index=False)



if __name__ =='__main__':
    completion_engine = OpenAIEngine('davinci-002')
    completion_questions = pd.read_csv('./data/questions/completion_questions.csv')
    #responses_dir = './data/sample_responses/completion'
    #output_csv = './data/responses/completion_responses.csv'
    
    #build_responses(completion_engine, completion_questions, responses_dir, output_csv, True)

    chat_engine = OpenAIEngine('gpt-3.5-turbo')
    chat_questions = pd.read_csv('./data/questions/chat_questions.csv')

    reg_response = get_response(chat_engine, chat_questions.loc[810, 'prompt_classification'], False, 1)
    #reg_response = get_response(completion_engine, completion_questions.loc[810, 'prompt_classification'], True, 1)

    #responses_dir = './data/sample_responses/chat'
    #output_csv = './data/responses/chat_responses.csv'
    #reg_response = get_response(completion_engine, "Question: Which of the following is most related to birds? Options: 1. Bugs\n2. Penguins\n3. Primates\n4. Robins\n5. Dogs\n6. Cats\nThe number of the best option is ", True, 1)
    #reg_response = get_response(chat_engine, "Question: Which of the following is most related to birds? Options: 1. Bugs\n2. Lizards\n3. Primates\n4. Robins\n5. Dogs\n6. Cats\nRespond with only the number of the option and nothing else.", False, 1)
    #print(reg_response['choices'][0]['text'])
    print(reg_response['choices'][0]['message']['content'])
    print(reg_response)
    #build_responses(chat_engine, chat_questions, responses_dir, output_csv, False)
  