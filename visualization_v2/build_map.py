import folium
import pandas as pd
import requests
import geopandas
import branca
from folium.plugins import GroupedLayerControl
import json

def create_map(dfs, df_names, question_types):
    with open('countries.json', 'r') as f:
        data = json.load(f)
    
    # Intialize map
    m = folium.Map(location=(30, 10), zoom_start=3, tiles="cartodb positron")
    # Countres we have data for
    countries = geopandas.GeoDataFrame.from_features(data, crs="EPSG:4326")
    countries = countries[countries['sovereignt'].isin(['China', 'India', 'United States of America', 'Norway', 'Saudi Arabia', 'South Africa'])]
    # Build layers
    feature_group_dict = dict()
    for df_name in df_names:
        feature_group_dict[df_name] = dict()
        for question_type in question_types:
            feature_group_dict[df_name][question_type] = folium.FeatureGroup(name=question_type, show=False)
            m.add_child(feature_group_dict[df_name][question_type])

    # Add Data to Groups
    for df, df_name in zip(dfs, df_names):
        for question_type in question_types:
            df_subset = df[df['type'] == question_type]
            merged_subset_df = countries.merge(df_subset, on='sovereignt', how='left')

            for idx, row in merged_subset_df.iterrows():
                country_name = row['sovereignt']
                question = row['question']
                p1_response = row['response_top_p_1']
                p0_response = row['response_top_p_0']

                popup_html = f"""
                        <h3>{country_name}: {question}</h3>
                        <div style="display: flex; flex-direction: row;">
                            <div style="margin-right: 10px; border:1px solid black; width: 50%">
                                <h4>top_p = 1:</h4>
                                <p>{p1_response}</p>
                            </div>
                            <div style="border:1px solid black; width: 50%">
                                <h4>top_p = 0:</h4>
                                <p>{p0_response}</p>
                            </div>
                        </div>
                """
                iframe = branca.element.IFrame(html=popup_html, width=500, height=500)
                geo_json_layer = folium.GeoJson(
                    row.geometry.__geo_interface__,
                    popup=folium.Popup(iframe, max_width=500),
                    tooltip=folium.Tooltip(country_name),
                    # This stylefunction is fucking weird https://stackoverflow.com/questions/62744522/colorize-polygons-in-folium
                    style_function= lambda x, color=row['hex_color_p_0']: {
                        'fillColor': color,
                        'color': color
                    },
                )
                geo_json_layer.add_to(feature_group_dict[df_name][question_type])

    # Update group layers
    GroupedLayerControl(
        groups={df_name: list(feature_group_dict[df_name].values()) for df_name in feature_group_dict},
        collapsed=True,
        exclusive_groups=False
    ).add_to(m)

    return m