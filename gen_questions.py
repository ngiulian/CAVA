import pandas as pd
import itertools
import yaml
import string

from country_list import COUNTRIES


def gen_questions_dfs(question_config, prompt_version_config, chat_df_name,):
    open_ended_generations = prompt_version_config['open_ended_questions']['prompt_version']

    intro_chat = prompt_version_config['context']['prompt_2']['intro_chat']
    outro_chat = prompt_version_config['context']['prompt_2']['outro_chat']

    chat_open_ended = [[] for _ in range(len(open_ended_generations))]
    chat_classification = []

    types = []
    question_ids = []
    button_names = []
    country_names = []
    classes = []
    wv_ids = []



    for group_id, question_info in question_config.items():
        keywords = question_info['keywords']
        keywords['country'] = COUNTRIES
        for curr_args in itertools.product(*(keywords[key] for key in keywords)):
            replacement_dict = dict(zip(list(keywords.keys()), curr_args))
            question_info['classes']
              
            for i, prompt_version in enumerate(open_ended_generations):
                replacement_dict['prompt_version'] = prompt_version
                chat_question = prompt_version_config['context']['prompt_1']['chat'].format(**replacement_dict) + question_info['chat_template'].format(**replacement_dict)
                chat_open_ended[i].append(chat_question)
            
            options = "Options:\n"
            cs = question_info['classes']
            #if len(cs) >= 10:
            #    replacement_dict['enumeration'] = "letter"
            #    for i, c in enumerate(cs):
            #        options += string.ascii_lowercase[i] + '. ' + c + '\n'
            #else:
            replacement_dict['enumeration'] = "number"
            for i, c in enumerate(cs):
                options += str(i+1) + '. ' + c + '\n'
            chat_classification.append(intro_chat + question_info['classification_template'] + options + outro_chat.format(**replacement_dict))
            types.append(question_info['type_template'].format(**replacement_dict))
            button_names.append(question_info['button_name'].format(**replacement_dict))
            question_ids.append(question_info['question_id'].format(**replacement_dict))
            classes.append(cs)
            country_names.append(replacement_dict['country'])
            wv_ids.append(question_info['wv_id'])
            
    d_chat = {'type': types, 'question_id': question_ids, 'prompt_classification': chat_classification, 'button_name': button_names, 'country': country_names, 'classes': classes, 'wv_id': wv_ids}
    for i in range(len(open_ended_generations)):
        d_chat[f'prompt_open_ended_version_{i}'] = chat_open_ended[i]
    df = pd.DataFrame(d_chat)
    df.to_csv(chat_df_name, index=False)

if __name__ == "__main__":
    with open("planned_question_config.yaml") as f:
        question_config = yaml.safe_load(f)
    with open("planned_prompt_config.yaml") as f:
        prompt_version_config = yaml.safe_load(f)

    gen_questions_dfs(question_config, prompt_version_config, 'data/questions/button_name_chat_questions.csv')