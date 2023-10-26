from collections import defaultdict
from array import array
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import math
import numpy as np
import collections
from numpy import linalg as la
import time
import nltk
import pandas as pd
import re

"""

    ********** DATA CLEANING **********

    
"""

def remove_emojis(tweet):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emojis
                           u"\U0001F300-\U0001F5FF"  # symbols & pictograms
                           u"\U0001F680-\U0001F6FF"  # map symbols
                           u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', tweet)


def clean_tweet(line):
    
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    ## START CODE
    line = re.sub(r'[.,;:!?"\'-@]', '', line).replace("#", "").replace("’", "").replace("“", "").replace("\n"," ")
    line =  line.lower() ## Transform in lowercase
    line = remove_emojis(line).strip().replace("  ", " ")
    line = line.split(" ") ## Tokenize the text to get a list of terms
    line =[word for word in line if word not in stop_words]  ##eliminate the stopwords (HINT: use List Comprehension)
    line =[stemmer.stem(word) for word in line] ## perform stemming (HINT: use List Comprehension)
    line = [word for word in line if word != ""]
    ## END CODE
    
    return line

def create_and_clean_dataset(doc_path):
    
    with open(doc_path) as fp:
        lines = fp.readlines()
    
    df=pd.read_json(doc_path, lines=True)

    df_clean = df[["created_at","id_str","full_text","entities","favorite_count","retweet_count","user"]]

    renames = {"created_at":"date", "full_text":"tweet", "favorite_count":"likes","retweet_count":"retweets", "id_str":"tweet_id"}
    df_clean=df_clean.rename(columns=renames)

    df_hashtags = pd.json_normalize(df_clean["entities"])["hashtags"]

    df_hashtags = df_hashtags.apply(lambda x: [item["text"] for item in x])

    df_user = pd.json_normalize(df_clean["user"])["id"].rename("user_id")

    df_concat = pd.concat([df_clean,df_hashtags,df_user], axis=1).drop(columns=["entities","user"])

    df_concat["url"] = "https://twitter.com/" + df_concat["user_id"].astype(str) + "/status/" + df_concat["tweet_id"].astype(str)

    df_concat["tags"] = df_concat["tweet"].apply(lambda x: re.findall(r"@(\w+)", x))
    df_def = df_concat.copy()

    df_def["clean_tweet"] = df_def["tweet"].apply(clean_tweet)

    docs = pd.read_csv("IRWA_data_2023/Rus_Ukr_war_data_ids.csv", sep="\t", header=None)
    docs = docs.rename(columns={0:"doc_id",1:"tweet_id"})
    tweets = df_def.join(docs.set_index('tweet_id'), on='tweet_id')

    return tweets