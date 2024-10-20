import folium
import pandas as pd
import requests
import geopandas
import branca
from folium.plugins import FeatureGroupSubGroup, GroupedLayerControl
from branca.element import Element
import json
from html_constants import gen_dropdown_html_entry, gen_dropdown_html, gen_legend_html, gen_style_html, gen_layer_dict_html, gen_sidebar_html, gen_open_ended_popup_html, gen_classification_popup_html, gen_popup_html, gen_dropdown_html_comparison
from country_list import COUNTRIES
from keywords import find_keywords
import plotly.express as px
import html
import shapely
from shapely.geometry import shape
from shapely import wkt
from bs4 import BeautifulSoup
import ast
import yaml


def build_entry_page(gpt_3_point_5_turbo):
    m = folium.Map(location=(30, 10), zoom_start=3, tiles="cartodb positron", width='100%', height='87%')

    dropdown_elem = Element(gen_dropdown_html_entry(gpt_3_point_5_turbo)) 
    m.get_root().html.add_child(dropdown_elem, index=0)
    
    with open('static/custom_script_entry.js', 'r') as file:
        javascript_content = file.read()
    m.get_root().script.add_child(Element(javascript_content))

    m.save(f'./templates/entry.html')

def build_comparison_page(df):
    m = folium.Map(location=(30, 10), zoom_start=3, tiles=None, width='100%', height='87%')
    folium.TileLayer('cartodbpositron', name='Keywords').add_to(m)

    dropdown_elem = Element(gen_dropdown_html_comparison(df)) 
    m.get_root().html.add_child(dropdown_elem, index=0)
    
    with open('static/custom_script_comparison.js', 'r') as file:
        javascript_content = file.read()
    m.get_root().script.add_child(Element(javascript_content))


    # Get country GeoJSON
    with open('countries.json', 'r') as f:
        data = json.load(f)
    countries = geopandas.GeoDataFrame.from_features(data, crs="EPSG:4326")
    countries['country'] = countries['name']

    df = df[df['type'] == 'satisfied_class']
    merged_df = countries.merge(df, on='country', how='inner')

    layer_dict = {}


    print(len(merged_df))
    for idx, row in merged_df.iterrows():
        if isinstance(row.geometry, shapely.geometry.multipolygon.MultiPolygon):
            polys = list(row.geometry.geoms)
            sorted_polygons = sorted(polys, key=lambda x: shapely.count_coordinates(x), reverse=True)
            truncated_polygons = [shapely.wkt.loads(shapely.wkt.dumps(poly, rounding_precision=1)) for poly in sorted_polygons]
            feature = {
                "type": "Feature",
                "geometry": shapely.geometry.MultiPolygon(truncated_polygons).__geo_interface__,
            }
        else: 
            res = shapely.wkt.loads(shapely.wkt.dumps(row.geometry, rounding_precision=1))
            feature = {
                "type": "Feature",
                "geometry": res.__geo_interface__,
            }
        
        layer_id = row['name'].replace(' ', '_').replace('.','').replace("'", '').replace('-','').lower()

        popup = folium.Popup(max_width=400, sticky=False)

        country_name = row['name']
        popup_html = f"""
        <div style="text-align: left; height: 300px; overflow-y: auto;">
            <b style="display: block; font-size: 16px;">{country_name}</b><br>
            <span style="font-weight: bold; margin-top: 10px; display: block;">Prompt 1: </span> 
            <span id="prompt_open_ended"></span><br>
            <span style="font-weight: bold; margin-top: 10px; display: block;">Prompt 2: </span> 
            <span id="prompt_classification"></span><br>
            <span>Model 1: </span> <span id="model_1_response"></span> <br>
            <span>Model 2: </span> <span id="model_2_response"></span>
        </div>
        """

        popup.html._children[popup.get_name()+'_content'] = folium.Html(popup_html, script=True)
        geojson_layer = folium.GeoJson(
            feature,
            tooltip=folium.Tooltip(row['country']),
            style_function=lambda x, color="black": {
                'fillColor': "white",
                "color": color,
            },
            popup=popup

        )

        layer_dict[layer_id] = geojson_layer

        geojson_layer.add_to(m)  

    
    style_elem = Element(gen_style_html()) 
    m.get_root().header.add_child(style_elem, index=0)

    d = f"""
    <script> 
        var layerDict = {json.dumps({key: layer.get_name() for key, layer in layer_dict.items()})}; 
    </script>
    """

    layer_dict_elem = Element(d)
    m.get_root().html.add_child(layer_dict_elem)


    m.save(f'./templates/comparison.html')

    


def compute_summary_stats_classes(df, prompt_version_config):
    classes = df['classes'].unique()
    assert(len(classes) == 1)
    classes = ast.literal_eval(classes[0])

    colors = prompt_version_config['classification_questions']['color_list']
    num_versions  = len(prompt_version_config['open_ended_questions']['prompt_version'])

    colors = colors[:len(classes)]
    color_map = dict(zip(classes, colors))
    class_map = dict(zip([i+1 for i in range(len(classes))], classes))

    charts = []
    for i in range(num_versions):
        class_counts = df[f'response_classification_version_{i}'].value_counts()
        class_counts = class_counts.sort_index()

        class_counts.index = class_counts.index.map(class_map.get)
        fig = px.bar(x=class_counts.index, y=class_counts.values,
                    labels={'y': 'Count', 'x': 'Class'},
                    title=f'Prompt Version {i}: {prompt_version_config["open_ended_questions"]["prompt_version"][i]}',
                    color=class_counts.index,
                    color_discrete_map=color_map)

        # Customize the layout
        fig.update_layout(xaxis_title='Class', yaxis_title='Count', width=400, height=400)

        # Save the standalone HTML file without the full Plotly JavaScript library
        bar_chart_html_string = fig.to_html(full_html=False, include_plotlyjs='cdn', default_width='100%', default_height='100%', config={'displayModeBar': False})
        charts.append(bar_chart_html_string)

    res = {}
    res['plot'] = charts
    res['colors'] = colors
    res['classes'] = classes
    return res
    

def compute_average_score(row, label_columns, score_columns):
    avg_score = 0
    for label_col, score_col in zip(label_columns, score_columns):
        label = row[label_col]
        score = row[score_col]
        if label == 'positive':
            avg_score += score
        elif label == 'negative':
            avg_score -= score
    return avg_score


def compute_summary_stats_polarity(df, prompt_version_config):
    num_versions  = len(prompt_version_config['open_ended_questions']['prompt_version'])
    label_columns = [f'sentiment_label_verion_{i}' for i in range(num_versions)]
    score_columns = [f'sentiment_score_verion_{i}' for i in range(num_versions)]

    avg_scores = df.apply(compute_average_score, axis=1, label_columns=label_columns, score_columns=score_columns)
    

    n = 5  
    highest_average = avg_scores.nlargest(n)
    highest_average_list = df.loc[highest_average.index,'country'].to_list()

    smallest_average = avg_scores.nsmallest(n)
    smallest_average_list = df.loc[smallest_average.index, 'country'].to_list()

    charts = []
    for i in range(num_versions):
        sentiment_counts = df[f'sentiment_label_verion_{i}'].value_counts()

        colors = {'positive': 'green', 'negative': 'red', 'neutral': 'yellow'}
        # Create a bar chart using plotly express
        fig = px.bar(x=sentiment_counts.index, y=sentiment_counts.values,
                    labels={'y': 'Count', 'x': 'Sentiment'},
                    title=f'Prompt Version {i}: {prompt_version_config["open_ended_questions"]["prompt_version"][i]}',
                    color=sentiment_counts.index,
                    color_discrete_map=colors)

        # Customize the layout
        fig.update_layout(xaxis_title='Sentiment', yaxis_title='Count', width=400, height=400)

        # Save the standalone HTML file without the full Plotly JavaScript library
        bar_chart_html_string = fig.to_html(full_html=False, include_plotlyjs='cdn', default_width='100%', default_height='100%', config={'displayModeBar': False})
        charts.append(bar_chart_html_string)

    res = {}

    res['highest_score_countries'] = highest_average_list
    res['lowest_score_countries'] = smallest_average_list
    res['plot'] = charts
    return res


def build_map(dfs):
    # Get country GeoJSON
    with open('countries.json', 'r') as f:
        data = json.load(f)

    with open("planned_prompt_config.yaml") as f:
        prompt_version_config = yaml.safe_load(f)

    #dfs = [dfall]
    df_names = ['gpt-3.5-turbo', 'gpt-4o', 'gpt-4-turbo', 'Llama-2-70b-chat-hf', 'Llama-3-70b-chat-hf', 'Mixtral-8x22B-Instruct-v0.1', 'Qwen1.5-72B-Chat']
    #df_names = ['Qwen1.5-72B-Chat']
    question_types=sorted(list(set(dfs[0]['type'])))


    # Intialize map
    # Countres we have data for
    countries = geopandas.GeoDataFrame.from_features(data, crs="EPSG:4326")
    #countries = countries[countries['sovereignt'].isin(COUNTRIES)]
    countries['country'] = countries['name']

  
    # Add Data to Groups
    for df, df_name in zip(dfs, df_names):
        for question_type in question_types:
            layer_dict = {}
            popup_dict = {}
            m = folium.Map(location=(30, 10), zoom_start=3, tiles=None, width='100%', height='87%')
            folium.TileLayer('cartodbpositron', name='Keywords').add_to(m)

            m._name = question_type.replace(',','')
            m._id = "1"
            df_subset = df[df['type'] == question_type]
            #is_open_ended = df_subset['classes'].isna().all()

            polarity_summary_statistics = compute_summary_stats_polarity(df_subset, prompt_version_config) 
            class_summary_stats =  compute_summary_stats_classes(df_subset, prompt_version_config)

            merged_subset_df = countries.merge(df_subset, on='country', how='inner')

            blank_fg = folium.FeatureGroup(name='General')

            for idx, row in merged_subset_df.iterrows():
                if isinstance(row.geometry, shapely.geometry.multipolygon.MultiPolygon):
                    polys = list(row.geometry.geoms)
                    sorted_polygons = sorted(polys, key=lambda x: shapely.count_coordinates(x), reverse=True)
                    truncated_polygons = [shapely.wkt.loads(shapely.wkt.dumps(poly, rounding_precision=1)) for poly in sorted_polygons]
                    feature = {
                        "type": "Feature",
                        "geometry": shapely.geometry.MultiPolygon(truncated_polygons).__geo_interface__,
                    }
                else: 
                    res = shapely.wkt.loads(shapely.wkt.dumps(row.geometry, rounding_precision=1))
                    feature = {
                        "type": "Feature",
                        "geometry": res.__geo_interface__,
                    }

                #plot_df = pd.DataFrame({
                #    'Responses': ['P0 Response', 'P1 Response'],
                #    'Polarity Score': [p0_polarity_score, p1_polarity_score],
                #    'Polarity Label': [p0_polarity_label, p1_polarity_label]
                #})

                #colors = {'positive': 'green', 'negative': 'red', 'neutral': 'yellow'}

                #fig = px.bar(plot_df, x='Responses', y='Polarity Score', color='Polarity Label', color_discrete_map=colors)

                layer_id = row['name'].replace(' ', '_').replace('.','').replace("'", '').replace('-','').lower()


                #fig.write_html(f'sentiment_charts/{df_name}_{question_type.lower()}_{layer_id}.html', full_html=True, include_plotlyjs='cdn', default_width='100%', default_height='100%')

                #escaped_sentiment_bar_chart_html = html.escape(sentiment_bar_chart_html)

                #sentiment_bar_chart_html = folium.IFrame(sentiment_bar_chart_html).render()

        
                popup = folium.Popup(max_width=400, sticky=False)

                popup_html = gen_popup_html(row, 3, popup) #gen_open_ended_popup_html(row, df_name, question_type, layer_id, popup) if is_open_ended else gen_classification_popup_html(row)

                popup.html._children[popup.get_name()+'_content'] = folium.Html(popup_html, script=True)

                num_responses = 3
                popup_dict[popup.get_name()] = [0, num_responses]
                
                c1 = class_summary_stats['colors'][int(row['response_classification_version_0']) - 1]
                c2 = class_summary_stats['colors'][int(row['response_classification_version_1']) - 1]
                c3 = class_summary_stats['colors'][int(row['response_classification_version_2']) - 1]
                sentiment_colors = [row[f'sentiment_color_verion_{i}'] for i in range(3)]
                soft_metric_colors = [row[f'soft_metric_{i}_color'] if pd.notna(row[f'soft_metric_{i}_color']) else 'white' for i in range(3)]
                hard_metric_colors = [row[f'hard_metric_{i}_color'] if pd.notna(row[f'hard_metric_{i}_color']) else 'white' for i in range(3)]
                feature['properties'] = {'classification_colors': [c1, c2, c3], 'sentiment_colors': sentiment_colors, 'soft_metric_colors': soft_metric_colors, 'hard_metric_colors': hard_metric_colors}
                #color_col = 'hex_color' if is_open_ended else 'color'
                geojson_layer = folium.GeoJson(
                    feature,
                    tooltip=folium.Tooltip(row['country']),
                    style_function=lambda x, color=c1: {
                        'fillColor': color,
                        'color': color
                    },
                    popup=popup
                )

              
                
                #if layer_id in layer_dict:
                #    layer_dict[layer_id].append(geojson_layer)
                #else:
                #    layer_dict[layer_id] = [geojson_layer]
                layer_dict[layer_id] = geojson_layer
              


                geojson_layer.add_to(blank_fg)                       
                
            dropdown_elem = Element(gen_dropdown_html(df, df_name, question_type)) # Dropdown in HTML at index 0 
            m.get_root().html.add_child(dropdown_elem, index=0)

            style_elem = Element(gen_style_html()) 
            m.get_root().header.add_child(style_elem, index=0)

            sidebar_elem = Element(gen_sidebar_html(df_name, class_summary_stats, polarity_summary_statistics, question_type))
            m.get_root().html.add_child(sidebar_elem)


            layer_dict_elem = Element(gen_layer_dict_html(layer_dict, popup_dict))
            m.get_root().html.add_child(layer_dict_elem)

            m.add_child(blank_fg)
            glc = GroupedLayerControl(
                groups={'Keywords': [blank_fg]},
                collapsed=False,
            )
            glc._id = "1"
    
            glc.add_to(m)

            with open('static/custom_script.js', 'r') as file:
                javascript_content = file.read()
            m.get_root().script.add_child(Element(javascript_content))

            legend_elem = gen_legend_html(class_summary_stats['colors'], class_summary_stats['classes'], "Classes")
            

            m.save(f'./templates/{df_name}_{question_type.lower()}.html')

            with open(f'./templates/{df_name}_{question_type.lower()}.html', "r") as file:
                html_string = file.read()
            soup = BeautifulSoup(html_string, 'lxml')
            target_element_id = f'{m._name}_{m._id}'
            target_element = soup.find(id=target_element_id)
            target_element.append(BeautifulSoup(legend_elem, 'lxml'))
            modified_html_string = str(soup)
            with open(f'./templates/{df_name}_{question_type.lower()}.html', "w") as file:
                file.write(modified_html_string)

            
            
        
if __name__ == "__main__":
    #chat_questions_df = pd.read_csv('data/responses/chat_responses.csv')
    #completion_questions_df = pd.read_csv('data/responses/completion_responses.csv')
    gpt_3_point_5_turbo = pd.read_csv('data/responses/test/gpt-3.5-turbo_responses.csv')
    gpt_4o = pd.read_csv('data/responses/test/gpt-4o_responses.csv')
    gpt_4_turbo = pd.read_csv('data/responses/test/gpt-4-turbo_responses.csv')


    llama = pd.read_csv('data/responses/test/Llama-2-70b-chat-hf_responses.csv')
    llama3 = pd.read_csv('data/responses/test/Llama-3-70b-chat-hf_responses.csv')
    mixtral = pd.read_csv('data/responses/test/Mixtral-8x22B-Instruct-v0.1_responses.csv')
    qwen = pd.read_csv('data/responses/test/Qwen1.5-72B-Chat_responses.csv')
    
    build_map([gpt_3_point_5_turbo, gpt_4o, gpt_4_turbo, llama, llama3, mixtral, qwen])
    build_entry_page(gpt_3_point_5_turbo)
    build_comparison_page(gpt_3_point_5_turbo)