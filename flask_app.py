from flask import Flask, render_template, request, jsonify, redirect
from tfidf import TFIDFAnalyzer
import pandas as pd
import string
import re
import os
import ast
import yaml

app = Flask(__name__, static_url_path='/static')


@app.route("/")
def entry_page():
    return render_template('entry.html')

@app.route("/metrics", methods=['POST'])
def compute_metric():
    metric = request.get_json().get('metric')
    model = request.get_json().get('model')
    topic = request.get_json().get('topic')
    df = pd.read_csv(f'data/responses/test/{model}_responses.csv')
    df = df[df['type']== topic]

    df = df.dropna(subset=[f'{metric}_0'])

    score_tuples = [(country, round(score, 3)) for country, score in zip(df['country'], df[f'{metric}_0'])]

    # Sort the list of tuples by the score (second element of each tuple)
    score_tuples_sorted = sorted(score_tuples, key=lambda x: x[1], reverse=True)
    
    countries = [t[0] for t in score_tuples_sorted]
    scores = [t[1] for t in score_tuples_sorted]
    res = {'ranks': [i+1 for i in range(len(score_tuples_sorted))], 'countries': countries, 'scores': scores}
    return jsonify(res)


@app.route("/tfidf", methods=['POST'])
def compute_tfidf():
    threshold = float(request.get_json().get('threshold'))
    model = request.get_json().get('model')
    topic = request.get_json().get('topic')
    # Implement logic to process user input and generate map layers
    analyzer = TFIDFAnalyzer()
    df = pd.read_csv(f'data/responses/test/{model}_responses.csv')
    df = df[df['type']== topic]

	
    response_column_names = {'response_open_ended_version_0': 'r0_text', 'response_open_ended_version_1': 'r1_text', 'response_open_ended_version_2': 'r2_text'}

    res = analyzer.compute_and_underline_tf_idf_words(df, response_column_names , 'country', threshold)
    return jsonify(res)

@app.route("/search", methods=['POST'])
def search_location():
    user_input = request.get_json().get('location')
    model = request.get_json().get('model')
    topic = request.get_json().get('topic')
    # Implement logic to process user input and generate map layers
    layers = generate_layers_for_location(user_input, model, topic)
    return jsonify(layers)

@app.route("/comparison", methods=['POST'])
def compare():
    model1 = request.get_json().get('model1')
    model2 = request.get_json().get('model2')
    topic = request.get_json().get('topic')
    pv = request.get_json().get('pv')
    df1 = pd.read_csv(f'data/responses/test/{model1}_responses.csv')
    df1 = df1[df1['type']== topic]

    classes = ast.literal_eval(df1.iloc[0]['classes'])

    df2 = pd.read_csv(f'data/responses/test/{model2}_responses.csv')
    df2 = df2[df2['type']== topic]

    df1[f'{model1}_response_classification_version_{pv}'] = df1[f'response_classification_version_{pv}']
    df2[f'{model2}_response_classification_version_{pv}'] = df2[f'response_classification_version_{pv}']

    if model1 == model2:
        merged_df = df1
        suffix = ""
    else:
        merged_df = df1.merge(df2, on='country', how='inner')
        suffix = "_x" if model1 != 'Qwen1.5-72B-Chat' else "_y"
    assert len(merged_df) == len(df2)
    result_dict = {}
    for _, row in merged_df.iterrows():
        country_name = row['country'].replace(' ', '_').replace('.','').replace("'", '').replace('-','').lower()
        num1 = row[f'{model1}_response_classification_version_{pv}'] 

        response1 = str(num1)+ '. ' + classes[num1 - 1]
        num2 = row[f'{model2}_response_classification_version_{pv}'] 
        response2 = str(num2)+ '. ' + classes[num2 - 1]

        frac = abs(num1 - num2) / (len(classes) - 1)
        interpolated_color = (255, int(255 * (1 - frac)), int(255 * (1 - frac)))
        color = '#%02x%02x%02x' % interpolated_color

        result_dict[country_name] = {'response_1': response1, 'response_2': response2, 'color': color, 'prompt_classification': row[f'prompt_classification{suffix}'].replace('\n', '<br>'), 'prompt_open_ended': row[f'prompt_open_ended_version_{pv}{suffix}'].replace('\n', '<br>')}

        
        
  
    return jsonify(result_dict)

    

@app.route("/<x>")
def response_page(x):
    if x == "chat_significant,20.html":
        return redirect("/gpt-3.5-turbo_medicine_12months_class.html")
    return render_template(x)


def generate_layers_for_location(location, model, topic):
    df = pd.read_csv(f'data/responses/test/{model}_responses.csv')
    df = df[df['type']== topic]

    with open("planned_prompt_config.yaml") as f:
        prompt_version_config = yaml.safe_load(f)
    colors = prompt_version_config['classification_questions']['color_list']

    popup_len = 3
    response_column_names = {'response_open_ended_version_0': 'r0_text', 'response_open_ended_version_1': 'r1_text', 'response_open_ended_version_2': 'r2_text'}

    res = []

    def add_strong_tags(row, column_name):
        pattern = re.compile(r'\b' + re.escape(location), re.IGNORECASE)
        return pattern.sub(lambda x: f"<strong>{x.group()}</strong>", row[column_name])

    # Apply the custom function to each row and add the dictionary to the 'res' variable
    response_columns = response_column_names.keys()
    for response_column in response_columns:
        df[f'added_strong_{response_column}'] = df.apply(add_strong_tags, axis=1, column_name=response_column)

    for _, row in df.iterrows():
        for response_column in response_columns:
            if row[f'added_strong_{response_column}'] != row[response_column]:
                result_dict = {'country': row['country'].replace(' ', '_').replace('.','').replace("'", '').replace('-','').lower()}
                responses = {}
                for rc in response_columns:
                    responses[response_column_names[rc]] = f"""<span id="{response_column_names[rc]}"> {row[f"added_strong_{rc}"].replace("`", "'")} </span> <br>"""
                result_dict['responses'] = responses
                result_dict['color'] = colors[row['response_classification_version_0'] - 1]
                res.append(result_dict)
                break
    return {'keyword': str(location), 'country_info': res, 'popup_len': popup_len}


if __name__ == "__main__":
    app.run(debug=True)