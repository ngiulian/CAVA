import json
import ast

def gen_dropdown_html_entry(df):
    type_button_names_df = df.drop_duplicates(subset=['type', 'button_name'])

    types = type_button_names_df['type'].to_list()
    button_names = type_button_names_df['button_name'].to_list()

    dropdown_html = """
    <h2>CAVA: Cultural Alignment Visual Analyzer</h2>
        <label for="dropdown_model">Choose a Model:</label>
        <select name="dropdown_model" id="dropdown_model">
            <option disabled selected value> -- select an option -- </option>
            {}
        </select>

        <label for="dropdown_topic">Select a Topic:</label>
        <select id="dropdown_topic">
            <option disabled selected value> -- select an option -- </option>
            {}
        </select>

        <input type="button" id="goBtn" value="GO!">
        <input type="button" id="modeBtn" value="Comparison Mode" style="float: right;">
    """
    # Generate the options for the model dropdown
    model_options = "\n".join([f'<option value="{model}">{model}</option>' for model in ['gpt-3.5-turbo', 'gpt-4o', 'gpt-4-turbo', 'Llama-2-70b-chat-hf', 'Llama-3-70b-chat-hf', 'Mixtral-8x22B-Instruct-v0.1', 'Qwen1.5-72B-Chat']])

    # Generate the options for the topic dropdown
    topic_options = "\n".join([f'<option value="{val}">{name}</option>' for val, name in zip(types, button_names)])

    # Insert the generated options into the dropdown HTML
    dropdown_html = dropdown_html.format(model_options, topic_options)

    return dropdown_html


def gen_dropdown_html_comparison(df):
    type_button_names_df = df.drop_duplicates(subset=['type', 'button_name'])

    types = type_button_names_df['type'].to_list()
    button_names = type_button_names_df['button_name'].to_list()

    dropdown_html = """
    <h2>CAVA: Cultural Alignment Visual Analyzer</h2>
        <label for="dropdown_model_1">Choose Model 1:</label>
        <select name="dropdown_model_1" id="dropdown_model_1">
            <option disabled selected value> -- select an option -- </option>
            {}
        </select>

        <label for="dropdown_model_2">Choose Model 2:</label>
        <select name="dropdown_model_2" id="dropdown_model_2">
            <option disabled selected value> -- select an option -- </option>
            {}
        </select>

        <label for="dropdown_topic">Select a Topic:</label>
        <select id="dropdown_topic">
            <option disabled selected value> -- select an option -- </option>
            {}
        </select>

        <label for="dropdown_prompt_version">Select a Prompt Version:</label>
        <select id="dropdown_prompt_version">
            <option disabled selected value> -- </option>
            <option value="0">0</option>
            <option value="1">1</option>
            <option value="2">2</option>
        </select>

        <input type="button" id="goBtn" value="GO!" onclick="requestToBuildMap()">
        <input type="button" id="modeBtn" value="Standard Mode" style="float: right;">
    """
    # Generate the options for the model dropdown
    model_options = "\n".join([f'<option value="{model}">{model}</option>' for model in ['gpt-3.5-turbo', 'gpt-4o', 'gpt-4-turbo', 'Llama-2-70b-chat-hf', 'Llama-3-70b-chat-hf', 'Mixtral-8x22B-Instruct-v0.1', 'Qwen1.5-72B-Chat']])

    # Generate the options for the topic dropdown
    topic_options = "\n".join([f'<option value="{val}">{name}</option>' for val, name in zip(types, button_names)])



    # Insert the generated options into the dropdown HTML
    dropdown_html = dropdown_html.format(model_options, model_options, topic_options)

    return dropdown_html


def gen_dropdown_html(df, df_name, t):
    type_button_names_df = df.drop_duplicates(subset=['type', 'button_name'])

    types = type_button_names_df['type'].to_list()
    button_names = type_button_names_df['button_name'].to_list()

    dropdown_html = """
    <h2>CAVA: Cultural Alignment Visual Analyzer</h2>
        <label for="dropdown_model">Choose a Model:</label>
        <select name="dropdown_model" id="dropdown_model">
            {}
        </select>

        <label for="dropdown_topic">Select a Topic:</label>
        <select id="dropdown_topic">
            {}
        </select>

        <input type="button" id="goBtn" value="GO!">
        <input type="button" id="modeBtn" value="Comparison Mode" style="float: right;">

        <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
        
        
    """

    # Generate the options for the model dropdown
    model_options = []
    for model in ['gpt-3.5-turbo', 'gpt-4o', 'gpt-4-turbo', 'Llama-2-70b-chat-hf', 'Llama-3-70b-chat-hf', 'Mixtral-8x22B-Instruct-v0.1', 'Qwen1.5-72B-Chat']:
        if model == df_name:
            model_options.append(f'<option value="{model}" selected>{model}</option>')
        else:
            model_options.append(f'<option value="{model}">{model}</option>')
    model_options = "\n".join(model_options)

    options = []
    for val, name in zip(types, button_names):
        if val == t:
            options.append(f'<option value="{val}" selected>{name}</option>')
        else:
            options.append(f'<option value="{val}">{name}</option>')

    # Generate the options for the topic dropdown
    topic_options = "\n".join(options)

    # Insert the generated options into the dropdown HTML
    dropdown_html = dropdown_html.format(model_options, topic_options)

    return dropdown_html

def gen_layer_dict_html(layer_dict, popup_dict):
    return f"""
    <script> 
        var layerDict = {json.dumps({key: layer.get_name() for key, layer in layer_dict.items()})}; 
        var popupDict = {json.dumps(popup_dict)};
    </script>
"""


def gen_legend_html(colors, classes, title):
    html = '<div id="classificationLegend" style="display: block; position: absolute; bottom: 30px; right: 0px; z-index: 9999; font-size: 12px; background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 10px;">'
    html += f'<p style="text-align: center; margin-bottom: 2px;"><b>{title}</b></p>'
    
    for color, class_name in zip(colors, classes):
        html += f'<span><div style="display: inline-block; height: 10px; width: 10px; background-color: {color};"></div>'
        html += f'<p style="display: inline;"> {class_name}</p></span><br>'
    
    html += '</div>'

    sentiment_colors = ['red', 'orange', 'yellow', 'LightGreen', 'green']
    sentiment_classes = ['Negative', 'Slightly Negative', 'Neutral', 'Slightly Positive', 'Positive']
    sentiment_title = "Response Polarity"


    html += '<div id="sentimentLegend" style="display: none; position: absolute; bottom: 30px; right: 0px; z-index: 9999; font-size: 12px; background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 10px;">'
    html += f'<p style="text-align: center; margin-bottom: 2px;"><b>{sentiment_title}</b></p>'

    for sentiment_color, sentiment_class in zip(sentiment_colors, sentiment_classes):
        html += f'<span><div style="display: inline-block; height: 10px; width: 10px; background-color: {sentiment_color};"></div>'
        html += f'<p style="display: inline;"> {sentiment_class}</p></span><br>'
    html += '</div>'

    evaluation_colors = ['#FF0000', '#BF0000', '#7F0000', '#3F0000', '#000000'][::-1]
    evaluation_title = "Alignment Score"
    evaluation_classes = ['0.00 (Poor)', '0.25', '0.50', '0.75', '1.0 (Good)'][::-1]

    html += '<div id="evaluationLegend" style="display: none; position: absolute; bottom: 30px; right: 0px; z-index: 9999; font-size: 12px; background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 10px;">'
    html += f'<p style="text-align: center; margin-bottom: 2px;"><b>{evaluation_title}</b></p>'

    for eval_color, eval_class in zip(evaluation_colors, evaluation_classes):
        html += f'<span><div style="display: inline-block; height: 10px; width: 10px; background-color: {eval_color};"></div>'
        html += f'<p style="display: inline;"> {eval_class}</p></span><br>'
    html += '</div>'





    
    return html

def country_to_layer_id(country):
    return country.replace(' ', '_').replace('.','').replace("'", '').replace('-','').lower()


def gen_polarity_classes_tab(summary_statistics):
    highest_score_countries = summary_statistics['highest_score_countries']
    lowest_score_countries = summary_statistics['lowest_score_countries']
    highest_score = [f'<li><a href="#" style="text-decoration: underline;" onclick="openPopupForCountry(\'{country_to_layer_id(country)}\')">{country}</a></li>' for country in highest_score_countries]
    lowest_score = [f'<li><a href="#" style="text-decoration: underline;" onclick="openPopupForCountry(\'{country_to_layer_id(country)}\')">{country}</a></li>' for country in lowest_score_countries]


    highest_score =  "\n".join(highest_score)
    lowest_score = "\n".join(lowest_score)

    polarity_html = """
        <h4>Highest Average Polarity Scores</h4>
            <ol>
                {}
            </ol>
            <h4>Lowest Average Polarity Scores</h4>
            <ol>
                {}
            </ol>
        """.format(highest_score, lowest_score)

    curr = """
    <div class="sidebar-pane" id="polarity">
            <h1 class="sidebar-header">Polarity<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h1>
            <div style="text-align: center; margin-top: 2%">
                <label for="sentimentPromptVersionColor"> Choose Prompt Version to Color:</label>
                <select id="sentimentPromptVersionColor" onchange="colorBySentimentPromptVersion()">
                    <option disabled selected value> -- select an option -- </option>
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                </select>
            </div>
            {}
            {}
    </div> """
    curr = curr.format(polarity_html,  "".join(summary_statistics['plot']))
    return curr


def gen_prompt_response_div(row, pvi):
    open_ended_prompt = row[f"prompt_open_ended_version_{pvi}"].replace('\n', '<br>')
    open_ended_response = row[f"response_open_ended_version_{pvi}"]
    #prompt_classification = row["prompt_classification"]
    prompt_classification = row["prompt_classification"].replace('\n', '<br>')
    classification_response = row[f"response_classification_version_{pvi}"]
    
    if f'log_prob_version_{pvi}' in row:
        probs = ast.literal_eval(row[f'log_prob_version_{pvi}'])
    else:
        probs = {}
    classes =  ast.literal_eval(row["classes"])
    class_probs = {}
    for k,v in probs.items():
        class_probs[classes[int(k) - 1]] = round(v, 2)
    d = "block" if pvi == 0 else None
    #print(prompt_classification)
    return f"""
        <div id="r{pvi}_response" style="display:{d}; overflow: hidden;">
            <span style="font-weight: bold; margin-top: 10px; display: block;">Prompt 1: </span> 
            <span>{open_ended_prompt}</span><br>
            <span style="font-weight: bold; margin-top: 10px; display: block;">Response: </span> <span id="r{pvi}_text">{open_ended_response.replace('`', "'")}</span> <br>
            <span style="font-weight: bold; margin-top: 10px; display: block;">Prompt 2: </span> 
            <span>{prompt_classification}</span><br> 
            <span style="font-weight: bold; margin-top: 10px; display: block;">Response: </span> <span>{str(classification_response).replace('`', "'")}</span> <br>
            <span style="font-weight: bold; display: block; margin-top: 10px"> Probabilities: </span> {str(class_probs)} <br>
        </div>
    """


def gen_popup_html(row, prompt_version_numbers, popup):
    country_name = row['country']
    responses = "\n".join([gen_prompt_response_div(row, i) for i in  range(prompt_version_numbers)])

    popup_html = f"""
    <div style="text-align: left; height: 300px; overflow-y: auto;">
        <b style="display: block; font-size: 16px;">{country_name}</b><br>
        {responses}

        <div style="position: absolute; top: 10px; right: 20px;">
            <button id="prev_button" style="background: none; border: none;" onclick='previousResponse("{popup.get_name()}")'>
                <i class="fa fa-chevron-left" aria-hidden="true"></i>
            </button>
            <button id="next_button" style="background: none; border: none;" onclick='nextResponse("{popup.get_name()}")'>
                <i class="fa fa-chevron-right" aria-hidden="true"></i>
            </button>
        </div>
    </div>
    """
    return popup_html




def gen_classification_popup_html(row):
    country_name = row['sovereignt']
    question = row['question']
    p0_response = str(row['response_top_p_0'])
    date_asked = row['date_asked']
    curr_class = row['class']

    popup_html = f"""
    <div style="text-align: left; height: 300px; overflow-y: auto;">
        <b style="display: block; font-size: 16px;">{country_name}</b><br>
        <span style="font-weight: bold; margin-top: 10px; display: block;">Question (date asked: {date_asked}): </span> {question}<br>

        <div id="p0_response" style="display:block;  overflow: hidden;">
            <span style="font-weight: bold; margin-top: 10px; display: block;">Response: </span> <span id="p0_text">{p0_response.replace('`', "'")} </span> <br>
            <span style="font-weight: bold; display: block;">Class: </span> {curr_class} <br>
        </div>
    </div>
    """
    return popup_html


def gen_open_ended_popup_html(row, df_name, question_type, layer_id, popup):
    country_name = row['sovereignt']
    question = row['question']
    p1_response = str(row['response_top_p_1'])
    p0_response = str(row['response_top_p_0'])
    p1_polarity_score = round(row['polarity_score_top_p_1'], 3)
    p0_polarity_score = round(row['polarity_score_top_p_0'], 3)
    p1_polarity_label = row['polarity_label_top_p_1']
    p0_polarity_label = row['polarity_label_top_p_0']
    date_asked = row['date_asked']

    popup_html = f"""
    <div style="text-align: left; height: 300px; overflow-y: auto;">
        <b style="display: block; font-size: 16px;">{country_name}</b><br>
        <span style="font-weight: bold; margin-top: 10px; display: block;">Question (date asked: {date_asked}): </span> {question}<br>

        <div id="p0_response" style="display:block;  overflow: hidden;">
            <span style="font-weight: bold; margin-top: 10px; display: block;">P0 Response: </span> <span id="p0_text">{p0_response.replace('`', "'")} </span> <br>
            <span style="font-weight: bold; display: block;">P0 Polarity: </span> Label: {p0_polarity_label}, Score: {p0_polarity_score} <br>
        </div>
        <div id="p1_response" style="display:none; overflow: hidden;">
            <span style="font-weight: bold; margin-top: 10px; display: block;">P1 Response: </span>  <span id="p1_text">{p1_response.replace('`', "'")} </span>  <br>
            <span style="font-weight: bold; display: block;">P1 Polarity: </span> Label: {p1_polarity_label}, Score: {p1_polarity_score}<br>
        </div>
        <div id="p2_response" style="display:none; width: 100%; height: 100%;">
            <iframe src="/sentiment_charts/{df_name}_{question_type.lower()}_{layer_id}.html" style="display:block; width: 350px; height: 250px;"></iframe>
        </div>
        <div style="position: absolute; top: 10px; right: 20px;">
            <button id="prev_button" style="background: none; border: none;" onclick='previousResponse("{popup.get_name()}")'>
                <i class="fa fa-chevron-left" aria-hidden="true"></i>
            </button>
            <button id="next_button" style="background: none; border: none;" onclick='nextResponse("{popup.get_name()}")'>
                <i class="fa fa-chevron-right" aria-hidden="true"></i>
            </button>
        </div>
    </div>
    """
    return popup_html

def gen_sidebar_html(model_name, summary_statistics, polarity_summary_statistics, t):
    map_name = t.replace(',','') + "_1"

    tfidf_tab = "" if model_name == "Qwen1.5-72B-Chat" else '<li><a href="#tfifdf" role="tab"><i class="fa fa-exclamation"></i></a></li>'
    tfidf_header = "" if model_name == "Qwen1.5-72B-Chat" else """
    <div class="sidebar-pane" id="tfifdf">
        <h1 class="sidebar-header">TF IDF<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h1>
        <p>Term Frequence Inverse Document Frequency (TF-IDF) is a technique for quantifying the importance of a word in a given document.  Words that appear frequently within a a document (term frequency) and appear infrequently in the 
        other documents in the corpus (inverse document frequency) are deemed to be more important.  In our case, we consider the reponses across all countries to be a corpus. 
        Select a threshold below and all words with a TFIDF score above the threshold will be <u>underlined</u> in the Base Layer. The qualifying words will also be listed below. </p>

        <div style="text-align: center;">
            <label for="tfidfThreshold">TF IDF Threshold:</label>
            <select id="tfidfThreshold" onchange="computeTFIDF()">
                <option disabled selected value> -- select an option -- </option>
                <option value="0.05">0.05</option>
                <option value="0.10">0.10</option>
                <option value="0.15">0.15</option>
                <option value="0.20">0.20</option>
                <option value="0.25">0.25</option>
                <option value="0.30">0.30</option>
            </select>
        </div>
        <ol id="tfidf-res"></ol>
        
    </div>
    """

    siderbar_html = """
    <div id="sidebar" class="sidebar collapsed">
        <!-- Nav tabs -->
        <div class="sidebar-tabs">
            <ul role="tablist">
                <li><a href="#home" role="tab"><i class="fa fa-info-circle"></i></a></li>
                <li><a href="#polarity" role="tab"><i class="fa fa-thermometer-full"></i></a></li>
                <li><a href="#classification" role="tab"><i class="fa fa-bar-chart"></i></a></li>
                {}
                <li><a href="#search" role="tab"><i class="fa fa-search"></i></a></li>
                <li><a href="#evluation" role="tab"><i class="fa fa-check-square"></i></a></li>
            </ul>
        </div>

        <!-- Tab panes -->
        <div class="sidebar-content">
            <div class="sidebar-pane" id="home">
                <h1 class="sidebar-header">
                    Info
                    <span class="sidebar-close"><i class="fa fa-caret-left"></i></span>
                </h1>

                <h4>Welcome to CAVA!</h4> 
                
                <p> In order to explore potential geographic bias in Large Language Models (LLMs), we have prompted various LLMs with country-specific questions and display the reponses on leaflet maps.
                The models we have prompted with include OpenAI's gpt-3.5-turbo, gpt-4-turbo, and gpt-4o as well as Meta's Llama-2-70B-chat-hf and Llama-3-70B-chat-hf and other models including Mixtral-8x22B-Instruct-v0.1 and Qwen1.5-72B-Chat.
                To view the reponse for any country simply click on that country in the map. A popup will appear with the country name, exact prompts we used, and the correponding response. Use the dropdown menus above to change between models
                or question topics. If you're interested in where different model's agree or disagree on a particular topic click the button on the top right to enter Comparison Mode.</p>
                
                <p>To analyze the reponses you can explore the other tabs in the sidebar which allow you to do things like views the distribution of predicted lables, determine geographically where a model aligns well with the ground truth, use TF-IDF to identify important words in the reponse, search for keywords your interested in, or visualize the distribution of response polarity.</p>
            </div>

            {}

            <div class="sidebar-pane" id="classification">
                <h1 class="sidebar-header">Classification<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h1>
                <div style="text-align: center; margin-top: 2%">
                    <label for="promptVersionColor"> Choose Prompt Version to Color:</label>
                    <select id="promptVersionColor" onchange="colorByPromptVersion()">
                        <option selected value="0">0</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                    </select>
                </div>
                {}
            </div>

            {}

            <div class="sidebar-pane" id="search">
                <h1 class="sidebar-header">Keyword Search<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h1>
                <p>Search for any word of interest in the search bar below. A new sub layer will be created for the search word and any country that contains this word in the reponse will be added to the layer. The search word will be shown in <strong>bold</strong> anwywhere it appears in the response in the new sub layer </p>
                <div style="text-align: center;">
                    <input type="text" id="search-input" placeholder="Search for keyword">
                    <button onclick="searchLocation({})">Search</button>
                </div>
            </div>
            <div class="sidebar-pane" id="evluation">
                <h1 class="sidebar-header">Evaluation<span class="sidebar-close"><i class="fa fa-caret-left"></i></span></h1>
                <p> In order to do visualize how well the model's responses align with the real World Value Survey Responses you can select a metric and a prompt version and the map will be recolored base on the alignment with the selected metric.</p>
                <div style="text-align: center;">
                    <label for="evluationMetrics">Metric</label>
                    <select id="evluationMetrics">
                        <option disabled selected value> -- </option>
                        <option value="soft_metric">soft_metric</option>
                        <option value="hard_metric">hard_metric</option>
                    </select>
                    <label for="promptVersionMetrics">Prompt Version</label>
                    <select id="promptVersionMetrics">
                        <option disabled selected value> -- </option>
                        <option value="0">0</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                    </select>
                    <input type="button" id="evaluationButton" value="GO!">
                    <div id="metric-table"></div>
                    
                </div>
                
            </div>
        </div>
    </div>
    <script src="./static/jquery-sidebar.js"></script>

    <script>
        var sidebar = $('#sidebar').sidebar();
    </script>
    """
    siderbar_html = siderbar_html.format(tfidf_tab, gen_polarity_classes_tab(polarity_summary_statistics), "".join(summary_statistics['plot']), tfidf_header, map_name)
    return siderbar_html
     

def gen_style_html():
    return f"""


     <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.1.0/css/font-awesome.min.css" rel="stylesheet">

    <link rel="stylesheet" href="./static/gmaps-sidebar.css" />

    <style>
        body {{
            padding: 0;
            margin: 0;
        }}

        html, body, #map {{
            height: 100%;
            font: 10pt "Helvetica Neue", Arial, Helvetica, sans-serif;
        }}

        .lorem {{
            font-style: italic;
            color: #AAA;
        }}
    </style>


    <style>
    path.leaflet-interactive:focus {{
        outline: none;
    }}
    </style>
    """