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
from openai import AsyncOpenAI
import asyncio
import numpy as np

client = AsyncOpenAI(api_key="") # Add OpenAI secret key here



async def get_chat_completion(prompt, model_name):
    response = await client.chat.completions.create(
        messages= [{
            "role": "user",
            "content": prompt
        }],
        model=model_name,
        max_tokens=100,
        top_p=0.7,
        temperature=0.7
    )
    return response.choices[0].message.content

async def get_chat_completion_previous_message(curr_prompt, previous_prompt, previous_response, model_name, classes):
    response = await client.chat.completions.create(
        messages= [
            {"role": "user", "content": previous_prompt},
            {"role": "assistant", "content": previous_response},
            {"role": "user", "content": curr_prompt}
        ],
        model=model_name,
        max_tokens=1,
        logprobs=True,
        top_logprobs=20,
        top_p=0.7,
        temperature=0.7,
    )
    res = {}
    res['output'] = response.choices[0].message.content

    classes = [str(i+1) for i in range(len(classes))]

    if res['output'] not in classes:
        res['output'] = classes[-1]

    lp = {}
    for c in classes:
        lp[c] = 0.0
    logprobs = response.choices[0].logprobs.content[0].top_logprobs
    for logp in logprobs:
        if logp.token in classes:
            lp[logp.token] = np.exp(logp.logprob)

    res['log_probs'] = lp
    return res



async def get_open_ended_response(df, model_name, prompt_column, response_column, output_csv):
    prompts = df[prompt_column].to_list()
    num_prompts = len(prompts)
    tasks = []

    batch_size = 100
    curr_index = 0
    completed_responses = []
    

    while (curr_index < num_prompts):
        next_index = min(curr_index + batch_size, num_prompts)
        tasks = []
        for i in range(curr_index, next_index):
            tasks.append(get_chat_completion(prompts[i], model_name))
        curr_responses = await asyncio.gather(*tasks)
        completed_responses += curr_responses
        curr_index = next_index
        print(curr_index)
    #completed_responses = await asyncio.gather(*tasks)
    
    df[response_column] = completed_responses
    df.to_csv(output_csv, index=False)

async def get_classification_response(df, model_name, prompt_column, open_ended_prompt_column, open_ended_response_column, response_column, log_prob_column, output_csv):
    classification_prompt =  df[prompt_column].to_list()
    open_ended_prompt = df[open_ended_prompt_column].to_list()
    open_ended_response = df[open_ended_response_column].to_list()
    classes = df['classes'].to_list()

    num_prompts = len(classification_prompt)
    
    batch_size = 100
    curr_index = 0
    completed_responses = []

    while (curr_index < num_prompts):
        next_index = min(curr_index + batch_size, num_prompts)
        tasks = []
        for i in range(curr_index, next_index):
            tasks.append(get_chat_completion_previous_message(classification_prompt[i], open_ended_prompt[i], open_ended_response[i], model_name,  ast.literal_eval(classes[i])))
        curr_responses = await asyncio.gather(*tasks)
        completed_responses += curr_responses
        curr_index = next_index
        print(curr_index)

    responses = [d['output'] for d in completed_responses]
    logprobs = [d['log_probs'] for d in completed_responses]
    df[response_column] = responses
    df[log_prob_column] = logprobs
    
    df.to_csv(output_csv, index=False)




if __name__ == '__main__':
    model = "gpt-4o"
    #df = pd.read_csv('data/questions/chat_questions.csv')
    df =  pd.read_csv(f'data/responses/test/{model}_responses.csv')
    df_location = f'data/responses/test/{model}_responses.csv'
    
    #asyncio.run(get_open_ended_response(df, model, "prompt_open_ended_version_0", "response_open_ended_version_0", df_location))
    #asyncio.run(get_open_ended_response(df, model, "prompt_open_ended_version_1", "response_open_ended_version_1", df_location))
    #asyncio.run(get_open_ended_response(df, model, "prompt_open_ended_version_2", "response_open_ended_version_2", df_location))
    #pvi = 0
    for pvi in [0, 1, 2]:
        asyncio.run(get_classification_response(df, model, "prompt_classification", f"prompt_open_ended_version_{pvi}", f"response_open_ended_version_{pvi}", f"response_classification_version_{pvi}", f"log_prob_version_{pvi}", df_location))




