import pandas as pd

import re

from myapp.core.utils import load_json_file
from myapp.search.objects import Document

_corpus = {}


def their_load_corpus(path) -> [Document]:
    """
    Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
     in results, stats, etc.
    :param path:
    :return:
    """
    print("-- Loading corpus...")
    df = _load_corpus_as_dataframe(path)
    df.apply(_row_to_doc_dict, axis=1)
    print("-- Corpus loaded! Returning", type(df))
    return _corpus

def load_corpus(path) -> [Document]:
    """
    Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
     in results, stats, etc.
    :param path:
    :return:
    """
    print("-- Loading corpus...")

    df = pd.read_json(path, lines=True)
    df = clean_raw_dataset(df)
    df.apply(_row_to_doc_dict, axis=1)
    print("-- Corpus loaded! Returning", type(_corpus))
    return _corpus

def clean_raw_dataset(raw_df):
    # Select only relevant columns
    clean_df = raw_df[["created_at","id","full_text","entities","favorite_count","retweet_count","user"]]

    # Rename columns
    renames = {"created_at":"date", "full_text":"tweet", "favorite_count":"likes","retweet_count":"retweets", "id":"tweet_id"}
    clean_df = clean_df.rename(columns=renames)

    # Create Series of list of hashtags from `entities` object
    df_hashtags = pd.json_normalize(clean_df["entities"])["hashtags"]
    df_hashtags = df_hashtags.apply(lambda x: [item["text"] for item in x])

    # Create Series of username ids
    df_user = pd.json_normalize(clean_df["user"])["id"].rename("user_id")
    df_username = pd.json_normalize(clean_df["user"])["screen_name"].rename("username")

    # Merge hashtags and username columns to the DataFrame
    clean_df = pd.concat([clean_df,df_hashtags,df_user, df_username], axis=1).drop(columns=["entities","user"])

    # Create URL column manually from the user id and tweet id columns
    clean_df["url"] = "https://twitter.com/" + clean_df["user_id"].astype(str) + "/status/" + clean_df["tweet_id"].astype(str)

    # Extract tags to other users from the tweet body
    clean_df["tags"] = clean_df["tweet"].apply(lambda x: re.findall(r"@(\w+)", x))

    # Returns a DataFrame of tweets with columns ["date", "tweet_id", "tweet", "likes", "retweets", "hashtags", "user_id", "url", "tags", "tags"]
    # Should return ["Id", "Tweet", "Date", "Likes", "Retweets", "Url", "Hashtags"]
    clean_df = clean_df.rename(columns={"tweet_id": "Id", "tweet": "Tweet", "date": "Date", "likes": "Likes", "retweets": "Retweets", "url": "Url", "hashtags": "Hashtags"})
    return clean_df



def _load_corpus_as_dataframe(path):
    """
    Load documents corpus from file in 'path'
    :return:
    """
    print("---- Loading corpus as DataFrame...")
    json_data = load_json_file(path)
    tweets_df = _load_tweets_as_dataframe(json_data)
    _clean_hashtags_and_urls(tweets_df)
    # Rename columns to obtain: Tweet | Username | Date | Hashtags | Likes | Retweets | Url | Language
    corpus = tweets_df.rename(
        columns={"id": "Id", "full_text": "Tweet", "screen_name": "Username", "created_at": "Date",
                 "favorite_count": "Likes",
                 "retweet_count": "Retweets", "lang": "Language"})

    # select only interesting columns
    filter_columns = ["Id", "Tweet", "Username", "Date", "Hashtags", "Likes", "Retweets", "Url", "Language"]
    corpus = corpus[filter_columns]
    print("---- Corpus loaded as DataFrame! Returning", type(corpus))
    return corpus


def _load_tweets_as_dataframe(json_data):
    data = pd.DataFrame(json_data).transpose()
    # parse entities as new columns
    data = pd.concat([data.drop(['entities'], axis=1), data['entities'].apply(pd.Series)], axis=1)
    # parse user data as new columns and rename some columns to prevent duplicate column names
    data = pd.concat([data.drop(['user'], axis=1), data['user'].apply(pd.Series).rename(
        columns={"created_at": "user_created_at", "id": "user_id", "id_str": "user_id_str", "lang": "user_lang"})],
                     axis=1)
    return data


def _build_tags(row):
    tags = []
    # for ht in row["hashtags"]:
    #     tags.append(ht["text"])
    for ht in row:
        tags.append(ht["text"])
    return tags


def _build_url(row):
    url = ""
    try:
        url = row["entities"]["url"]["urls"][0]["url"]  # tweet URL
    except:
        try:
            url = row["retweeted_status"]["extended_tweet"]["entities"]["media"][0]["url"]  # Retweeted
        except:
            url = ""
    return url


def _clean_hashtags_and_urls(df):
    df["Hashtags"] = df["hashtags"].apply(_build_tags)
    df["Url"] = df.apply(lambda row: _build_url(row), axis=1)
    # df["Url"] = "TODO: get url from json"
    df.drop(columns=["entities"], axis=1, inplace=True)


def load_tweets_as_dataframe2(json_data):
    """Load json into a dataframe

    Parameters:
    path (string): the file path

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """
    # Load the JSON as a Dictionary
    tweets_dictionary = json_data.items()
    # Load the Dictionary into a DataFrame.
    dataframe = pd.DataFrame(tweets_dictionary)
    # remove first column that just has indices as strings: '0', '1', etc.
    dataframe.drop(dataframe.columns[0], axis=1, inplace=True)
    return dataframe


def load_tweets_as_dataframe3(json_data):
    """Load json data into a dataframe

    Parameters:
    json_data (string): the json object

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """

    # Load the JSON object into a DataFrame.
    dataframe = pd.DataFrame(json_data).transpose()

    # select only interesting columns
    filter_columns = ["id", "full_text", "created_at", "entities", "retweet_count", "favorite_count", "lang"]
    dataframe = dataframe[filter_columns]
    return dataframe


def _row_to_doc_dict(row: pd.Series):
    _corpus[row['Id']] = Document(row['Id'], row['Tweet'][0:100], row['Tweet'], row['Date'], row['Likes'],
                                  row['Retweets'],
                                  row['Url'], row['Hashtags'])
