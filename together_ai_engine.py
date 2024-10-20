import together
import pandas as pd
import numpy as np
from openai import AsyncOpenAI
import os
import string
import asyncio
import ast
import re


client = AsyncOpenAI(
    api_key="", # Add Together AI secret key here
    base_url='https://api.together.xyz/v1',
)

async def get_chat_completion(prompt, model_name):
    response = await client.chat.completions.create(
        messages= [{
            "role": "user",
            "content": prompt
        }],
        model=model_name,
        max_tokens=100,
    )
    return response.choices[0].message.content

async def retry_chat_completion(prompt, model_name, timeout=5):
    try:
        return await asyncio.wait_for(get_chat_completion(prompt, model_name), timeout=10)
    except asyncio.TimeoutError:
        return await retry_chat_completion(prompt, model_name, timeout)  # Retry on timeout

async def get_chat_completion_previous_message(curr_prompt, previous_prompt, previous_response, model_name, classes):
    response = await client.chat.completions.create(
        messages= [
            {"role": "user", "content": previous_prompt},
            {"role": "assistant", "content": previous_response},
            {"role": "user", "content": curr_prompt}
        ],
        model=model_name,
        max_tokens=15,
        logprobs=1
    )
    res = {}
    output = response.choices[0].message.content
    
    classes = [str(i+1) for i in range(len(classes))]

    #### code based on : https://github.com/BKHMSI/cultural-trends/blob/main/scripts/utils.py
    patterns = [r"\(\d+\)", r"\d+\)", r"\(\d+", r"\d+"]
    answer = classes[-1]
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, output)
        if match:
            if i == 0:
                answer = int(match.group()[1:-1])
            elif i == 1:
                answer = int(match.group()[:-1])
            elif i == 2:
                answer = int(match.group()[1:])
            else:
                answer = int(match.group())
            if answer <= 0 or answer >= len(classes):
                answer = classes[-1]
            break
    ### code based on: https://github.com/BKHMSI/cultural-trends/blob/main/scripts/utils.py
 
    #lp = {}
    #for c in classes:
    #    lp[c] = 0.0
    #logprobs = response.choices[0].logprobs
    #for logp in logprobs:
    #    if logp.token in classes:
    #        lp[logp.token] = np.exp(logp.logprob)
    #res['output'] = max(lp, key=lp.get)
    res['output'] = answer
    #res['log_probs'] = lp
    return res

async def get_open_ended_response(df, model_name, prompt_column, response_column, output_csv):
    prompts = df[prompt_column].to_list()
    num_prompts = len(prompts)
    
    batch_size = 100
    curr_index = 0
    completed_responses = []
    while (curr_index < num_prompts):
        next_index = min(curr_index + batch_size, num_prompts)
        tasks = []
        for i in range(curr_index, next_index):
            tasks.append(retry_chat_completion(prompts[i], model_name))
        curr_responses = await asyncio.gather(*tasks)
        completed_responses += curr_responses
        curr_index = next_index
        print(curr_index)
    
    df[response_column] = completed_responses
    df.to_csv(output_csv, index=False)


async def get_classification_response(df, model_name, prompt_column, open_ended_prompt_column, open_ended_response_column, response_column, output_csv):
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


    responses = [d['output'] for d in completed_responses]
    df[response_column] = responses    
    df.to_csv(output_csv, index=False)



if __name__ == '__main__':
    model_name = "Qwen/Qwen1.5-72B-Chat"
    model_save_name = "Qwen1.5-72B-Chat"
    #df = pd.read_csv('data/questions/chinese_chat_questions.csv') #Be careful, will overwrite the old df
    df =  pd.read_csv(f'data/responses/test/{model_save_name}_responses.csv')
    df_location = f'data/responses/test/{model_save_name}_responses.csv'
    
    #asyncio.run(get_open_ended_response(df, model_name, "prompt_open_ended_version_0", "response_open_ended_version_0", df_location))
    #asyncio.run(get_open_ended_response(df, model_name, "prompt_open_ended_version_1", "response_open_ended_version_1", df_location))
    #asyncio.run(get_open_ended_response(df, model_name, "prompt_open_ended_version_2", "response_open_ended_version_2", df_location))
    for pvi in [0, 1, 2]:
        asyncio.run(get_classification_response(df, model_name, "prompt_classification", f"prompt_open_ended_version_{pvi}", f"response_open_ended_version_{pvi}", f"response_classification_version_{pvi}", df_location))
