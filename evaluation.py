import pandas as pd
import ast


class Evaluator:
    def __init__(self, abbrev_to_country, incorrect_color="#FF0000", correct_color="000000"):
        self.abbrev_to_country = abbrev_to_country
        self.correct_color = correct_color
        self.incorrect_color = incorrect_color

    def score_to_hex_color(self, score):
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

        correct_rgb = hex_to_rgb(self.correct_color)
        incorrect_rgb = hex_to_rgb(self.incorrect_color)

        interpolated_rgb = tuple(int(incorrect_rgb[i] + (correct_rgb[i] - incorrect_rgb[i]) * score) for i in range(3))
        interpolated_hex = '#{:02X}{:02X}{:02X}'.format(*interpolated_rgb)
        return interpolated_hex
    

    def compute_hard_metric(self, df_gt, df_model_response, wv_ids, unique_countries):
        for abbrev in unique_countries:
            if abbrev not in self.abbrev_to_country:
                print(f"{abbrev} not included in model responses")
                continue
            country = self.abbrev_to_country[abbrev]
            df_curr = df_gt[df_gt['B_COUNTRY_ALPHA'] == abbrev]
            for wv_id in wv_ids:
                counts = df_curr[wv_id].value_counts().to_dict()
                filtered_counts = {k: v for k, v in counts.items() if k >= 0}
                total_count = sum(filtered_counts.values())
                if total_count == 0:
                    print(f"question {wv_id} not asked for {country}")
                    continue
                df_response = df_model_response[(df_model_response['wv_id'] == wv_id) & (df_model_response['country'] == country)]
                assert(len(df_response) == 1) # there should only be one response row for a given wv_id and country but multiple versions in the row
                df_res = df_response.reset_index(drop=True)
                for prompt_version in range(3):
                    res = int(df_res.loc[0, f'response_classification_version_{prompt_version}'])
                    if res not in filtered_counts:
                        filtered_counts[res] = 0

                    df_model_response.loc[(df_model_response['wv_id'] == wv_id) & (df_model_response['country'] == country), f'hard_metric_{prompt_version}'] = filtered_counts[res] / total_count
                    df_model_response.loc[(df_model_response['wv_id'] == wv_id) & (df_model_response['country'] == country), f'hard_metric_{prompt_version}_color'] = self.score_to_hex_color(filtered_counts[res] / total_count)
            print(f"finished {country}!")
        return df_model_response



    
    def compute_soft_metric(self, df_gt, df_model_response, wv_ids, unique_countries):
        for abbrev in unique_countries:
            if abbrev not in self.abbrev_to_country:
                print(f"{abbrev} not included in model responses")
                continue
            country = self.abbrev_to_country[abbrev]
            df_curr = df_gt[df_gt['B_COUNTRY_ALPHA'] == abbrev]
            for wv_id in wv_ids:
                counts = df_curr[wv_id].value_counts().to_dict()
                filtered_counts = {k: v for k, v in counts.items() if k >= -1}
                total_count = sum(filtered_counts.values())
                if total_count == 0:
                    print(f"question {wv_id} not asked for {country}")
                    continue
                df_response = df_model_response[(df_model_response['wv_id'] == wv_id) & (df_model_response['country'] == country)]
                assert(len(df_response) == 1) # there should only be one response row for a given wv_id and country but multiple versions in the row
                df_res = df_response.reset_index(drop=True)
                for prompt_version in range(3):
                    res = int(df_res.loc[0, f'response_classification_version_{prompt_version}'])
                    number_options = len(ast.literal_eval(df_res.loc[0, 'classes']))

                    total = 0
                    for op, count in filtered_counts.items():
                        if op == -1 and res == number_options:
                            total += count
                        elif res != number_options:
                            # if res == number_options then model answered idk and survey respondent did not
                            score = 1 - abs(res - op)/(number_options - 1)
                            total += score * count

                    df_model_response.loc[(df_model_response['wv_id'] == wv_id) & (df_model_response['country'] == country), f'soft_metric_{prompt_version}'] = total / total_count
                    df_model_response.loc[(df_model_response['wv_id'] == wv_id) & (df_model_response['country'] == country), f'soft_metric_{prompt_version}_color'] = self.score_to_hex_color(total / total_count)
            print(f"finished {country}!")
        return df_model_response

        
if __name__=='__main__':
    df_gt = pd.read_csv('data/WVS_Cross-National_Wave_7_csv_v5_0.csv')
    unique_countries = list(df_gt['B_COUNTRY_ALPHA'].unique())
    #models = ['gpt-3.5-turbo', 'Llama-2-70b-chat-hf']
    models = ['Mixtral-8x22B-Instruct-v0.1']
    abbrev_to_country = {'ABW': 'Aruba',  'AFG': 'Afghanistan',  'AGO': 'Angola',  'AIA': 'Anguilla',  'ALB': 'Albania',  'ALD': 'Aland',  'AND': 'Andorra',  'ARE': 'United Arab Emirates',  'ARG': 'Argentina',  'ARM': 'Armenia',  'ASM': 'American Samoa',  'ATA': 'Antarctica',  'ATC': 'Ashmore and Cartier Is.',  'ATF': 'Fr. S. Antarctic Lands',  'ATG': 'Antigua and Barb.',  'AUS': 'Australia',  'AUT': 'Austria',  'AZE': 'Azerbaijan',  'BDI': 'Burundi',  'BEL': 'Belgium',  'BEN': 'Benin',  'BFA': 'Burkina Faso',  'BGD': 'Bangladesh',  'BGR': 'Bulgaria',  'BHR': 'Bahrain',  'BHS': 'Bahamas',  'BIH': 'Bosnia and Herz.',  'BLM': 'St-Barthélemy',  'BLR': 'Belarus',  'BLZ': 'Belize',  'BMU': 'Bermuda',  'BOL': 'Bolivia',  'BRA': 'Brazil',  'BRB': 'Barbados',  'BRN': 'Brunei',  'BTN': 'Bhutan',  'BWA': 'Botswana',  'CAF': 'Central African Rep.',  'CAN': 'Canada',  'CHE': 'Switzerland',  'CHL': 'Chile',  'CHN': 'China',  'CIV': "Côte d'Ivoire",  'CMR': 'Cameroon',  'COD': 'Dem. Rep. Congo',  'COG': 'Congo',  'COK': 'Cook Is.',  'COL': 'Colombia',  'COM': 'Comoros',  'CPV': 'Cape Verde',  'CRI': 'Costa Rica',  'CUB': 'Cuba',  'CUW': 'Curaçao',  'CYM': 'Cayman Is.',  'CYN': 'N. Cyprus',  'CYP': 'Cyprus',  'CZE': 'Czech Rep.',  'DEU': 'Germany',  'DJI': 'Djibouti',  'DMA': 'Dominica',  'DNK': 'Denmark',  'DOM': 'Dominican Rep.',  'DZA': 'Algeria',  'ECU': 'Ecuador',  'EGY': 'Egypt',  'ERI': 'Eritrea',  'ESP': 'Spain',  'EST': 'Estonia',  'ETH': 'Ethiopia',  'FIN': 'Finland',  'FJI': 'Fiji',  'FLK': 'Falkland Is.',  'FRA': 'France',  'FRO': 'Faeroe Is.',  'FSM': 'Micronesia',  'GAB': 'Gabon',  'GBR': 'United Kingdom',  'GEO': 'Georgia',  'GGY': 'Guernsey',  'GHA': 'Ghana',  'GIN': 'Guinea',  'GMB': 'Gambia',  'GNB': 'Guinea-Bissau',  'GNQ': 'Eq. Guinea',  'GRC': 'Greece',  'GRD': 'Grenada',  'GRL': 'Greenland',  'GTM': 'Guatemala',  'GUM': 'Guam',  'GUY': 'Guyana',  'HKG': 'Hong Kong',  'HMD': 'Heard I. and McDonald Is.',  'HND': 'Honduras',  'HRV': 'Croatia',  'HTI': 'Haiti',  'HUN': 'Hungary',  'IDN': 'Indonesia',  'IMN': 'Isle of Man',  'IND': 'India',  'IOA': 'Indian Ocean Ter.',  'IOT': 'Br. Indian Ocean Ter.',  'IRL': 'Ireland',  'IRN': 'Iran',  'IRQ': 'Iraq',  'ISL': 'Iceland',  'ISR': 'Israel',  'ITA': 'Italy',  'JAM': 'Jamaica',  'JEY': 'Jersey',  'JOR': 'Jordan',  'JPN': 'Japan',  'KAS': 'Siachen Glacier',  'KAZ': 'Kazakhstan',  'KEN': 'Kenya',  'KGZ': 'Kyrgyzstan',  'KHM': 'Cambodia',  'KIR': 'Kiribati',  'KNA': 'St. Kitts and Nevis',  'KOR': 'Korea',  'KOS': 'Kosovo',  'KWT': 'Kuwait',  'LAO': 'Lao PDR',  'LBN': 'Lebanon',  'LBR': 'Liberia',  'LBY': 'Libya',  'LCA': 'Saint Lucia',  'LIE': 'Liechtenstein',  'LKA': 'Sri Lanka',  'LSO': 'Lesotho',  'LTU': 'Lithuania',  'LUX': 'Luxembourg',  'LVA': 'Latvia',  'MAC': 'Macao',  'MAF': 'St-Martin',  'MAR': 'Morocco',  'MCO': 'Monaco',  'MDA': 'Moldova',  'MDG': 'Madagascar',  'MDV': 'Maldives',  'MEX': 'Mexico',  'MHL': 'Marshall Is.',  'MKD': 'Macedonia',  'MLI': 'Mali',  'MLT': 'Malta',  'MMR': 'Myanmar',  'MNE': 'Montenegro',  'MNG': 'Mongolia',  'MNP': 'N. Mariana Is.',  'MOZ': 'Mozambique',  'MRT': 'Mauritania',  'MSR': 'Montserrat',  'MUS': 'Mauritius',  'MWI': 'Malawi',  'MYS': 'Malaysia',  'NAM': 'Namibia',  'NCL': 'New Caledonia',  'NER': 'Niger',  'NFK': 'Norfolk Island',  'NGA': 'Nigeria',  'NIC': 'Nicaragua',  'NIU': 'Niue',  'NLD': 'Netherlands',  'NOR': 'Norway',  'NPL': 'Nepal',  'NRU': 'Nauru',  'NZL': 'New Zealand',  'OMN': 'Oman',  'PAK': 'Pakistan',  'PAN': 'Panama',  'PCN': 'Pitcairn Is.',  'PER': 'Peru',  'PHL': 'Philippines',  'PLW': 'Palau',  'PNG': 'Papua New Guinea',  'POL': 'Poland',  'PRI': 'Puerto Rico',  'PRK': 'Dem. Rep. Korea',  'PRT': 'Portugal',  'PRY': 'Paraguay',  'PSX': 'Palestine',  'PYF': 'Fr. Polynesia',  'QAT': 'Qatar',  'ROU': 'Romania',  'RUS': 'Russia',  'RWA': 'Rwanda',  'SAH': 'W. Sahara',  'SAU': 'Saudi Arabia',  'SDN': 'Sudan',  'SDS': 'S. Sudan',  'SEN': 'Senegal',  'SGP': 'Singapore',  'SGS': 'S. Geo. and S. Sandw. Is.',  'SHN': 'Saint Helena',  'SLB': 'Solomon Is.',  'SLE': 'Sierra Leone',  'SLV': 'El Salvador',  'SMR': 'San Marino',  'SOL': 'Somaliland',  'SOM': 'Somalia',  'SPM': 'St. Pierre and Miquelon',  'SRB': 'Serbia',  'STP': 'São Tomé and Principe',  'SUR': 'Suriname',  'SVK': 'Slovakia',  'SVN': 'Slovenia',  'SWE': 'Sweden',  'SWZ': 'Swaziland',  'SXM': 'Sint Maarten',  'SYC': 'Seychelles',  'SYR': 'Syria',  'TCA': 'Turks and Caicos Is.',  'TCD': 'Chad',  'TGO': 'Togo',  'THA': 'Thailand',  'TJK': 'Tajikistan',  'TKM': 'Turkmenistan',  'TLS': 'Timor-Leste',  'TON': 'Tonga',  'TTO': 'Trinidad and Tobago',  'TUN': 'Tunisia',  'TUR': 'Turkey',  'TWN': 'Taiwan',  'TZA': 'Tanzania',  'UGA': 'Uganda',  'UKR': 'Ukraine',  'URY': 'Uruguay',  'USA': 'United States',  'UZB': 'Uzbekistan',  'VAT': 'Vatican',  'VCT': 'St. Vin. and Gren.',  'VEN': 'Venezuela',  'VGB': 'British Virgin Is.',  'VIR': 'U.S. Virgin Is.',  'VNM': 'Vietnam',  'VUT': 'Vanuatu',  'WLF': 'Wallis and Futuna Is.',  'WSM': 'Samoa',  'YEM': 'Yemen',  'ZAF': 'South Africa',  'ZMB': 'Zambia',  'ZWE': 'Zimbabwe'}
    e = Evaluator(abbrev_to_country)
    prompt_versions = 3
    for model in models:
        df = pd.read_csv(f'data/responses/test/{model}_responses.csv')
        wv_ids = df['wv_id'].unique()
        df = e.compute_hard_metric(df_gt, df, wv_ids, unique_countries)
        df = e.compute_soft_metric(df_gt, df, wv_ids, unique_countries)
        df.to_csv(f'data/responses/test/{model}_responses.csv', index=False)
        
        



        