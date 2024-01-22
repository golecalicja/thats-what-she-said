import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_all_lines_from_the_office():
    base_url = 'http://officequotes.net/no'
    list_all_lines = list()
    scene_counter = 0

    for season in range(1, 10):
        half_of_url = base_url + str(season) + '-'

        for episode in range(1, 28):
            if episode <= 9:
                full_url = half_of_url + '0' + str(episode) + '.php'
            else:
                full_url = half_of_url + str(episode) + '.php'

            error_message_404 = '\n<p align="center"><img src="img/dwight_ahh.jpg" /></p>\n<p align="center"><font size="8">404 Page Not Found</font></p>\n<p align="center">(Did you ask yourself "Would an idiot do that?" before you typed in the URL?)</p>\n'
            full_url_response = requests.get(full_url).content.decode(errors='ignore')

            if error_message_404 in full_url_response:
                pass
            else:
                soup = BeautifulSoup(full_url_response, 'html.parser')

                for element in soup.find_all('b')[13:]:
                    if element.name == 'b':
                        dict_episode = dict()
                        dict_episode['character'] = element.text
                        dict_episode['line'] = element.next_sibling
                        dict_episode['season'] = season
                        dict_episode['episode'] = episode
                        dict_episode['scene'] = scene_counter
                        list_all_lines.append(dict_episode)
                    elif element.name == 'hr':  # nowa scena
                        scene_counter += 1

    return list_all_lines


def list_to_pandas_df(list_data):
    pandas_df = pd.DataFrame(list_data)

    return pandas_df


def clean_all_lines(pandas_df):
    pandas_df_cleaned = pandas_df[~pandas_df['character'].str.contains("^(Deleted|Season|Main|None|Other)")]
    pandas_df_cleaned.dropna(subset=['line'], inplace=True)

    pandas_df_cleaned = pandas_df_cleaned.replace('\\n', ' ', regex=True)
    pandas_df_cleaned = pandas_df_cleaned.replace('\\t', '', regex=True)

    pandas_df_cleaned['character'] = pandas_df_cleaned['character'].str.title()
    pandas_df_cleaned['character'] = [character.strip() for character in pandas_df_cleaned['character']]
    pandas_df_cleaned['character'] = [character.strip('"') for character in pandas_df_cleaned['character']]
    pandas_df_cleaned['character'] = [character.strip(':') for character in pandas_df_cleaned['character']]
    pandas_df_cleaned.replace({'character': {'Michel:': 'Michael:', 'Darry:': 'Darryl:'}}, inplace=True)

    return pandas_df_cleaned


def main():
    list_all_lines = get_all_lines_from_the_office()
    pandas_df = list_to_pandas_df(list_all_lines)
    the_office_df_cleaned = clean_all_lines(pandas_df)
    the_office_df_cleaned.to_csv('the_office.csv')


if __name__ == "__main__":
    main()
