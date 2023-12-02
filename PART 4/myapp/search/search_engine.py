import random
import numpy as np
import os
import pickle

from myapp.search.objects import ResultItem, Document
from myapp.search.index import TfIdfIndex
from myapp.search.algorithms import search_in_corpus

INDEX_PATH = "index.pkl"

def build_demo_results(corpus: dict, search_id):
    """
    Helper method, just to demo the app
    :return: a list of demo docs sorted by ranking
    """
    res = []
    size = len(corpus)
    ll = list(corpus.values())
    for index in range(random.randint(0, 40)):
        item: Document = ll[random.randint(0, size)]
        res.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(item.id, search_id), random.random()))

    # for index, item in enumerate(corpus['Id']):
    #     # DF columns: 'Id' 'Tweet' 'Username' 'Date' 'Hashtags' 'Likes' 'Retweets' 'Url' 'Language'
    #     res.append(DocumentInfo(item.Id, item.Tweet, item.Tweet, item.Date,
    #                             "doc_details?id={}&search_id={}&param2=2".format(item.Id, search_id), random.random()))

    # simulate sort by ranking
    res.sort(key=lambda doc: doc.ranking, reverse=True)
    return res

def compute_popularities(corpus):

    """
    tweet_ids = clean_df["tweet_id"]

    # LOG-SCALE AND NORMALIZE 0-1
    likes = np.log(clean_df["likes"].apply(lambda x: x + 1))
    likes = (likes - np.min(likes)) / (np.max(likes) - np.min(likes))

    retweets = np.log(clean_df["retweets"].apply(lambda x: x + 1))
    retweets = (retweets - np.min(retweets)) / (np.max(retweets) - np.min(retweets))

    # COMPUTE USING OUR FORMULA
    our_score = likes.apply(lambda x: x*0.25) + likes.apply(lambda x: x*0.75)

    # RETURN DATAFRAME OF TWEET IDS AND SCORES

    """
    max_likes = 0
    min_likes = np.inf
    max_retweets = 0
    min_retweets = np.inf

    popularities = {}

    for key in corpus:
        if corpus[key].likes > max_likes:
            max_likes = corpus[key].likes

        if corpus[key].likes < min_likes:
            min_likes = corpus[key].likes

        if corpus[key].retweets > max_retweets:
            max_retweets = corpus[key].retweets

        if corpus[key].retweets < min_retweets:
            min_retweets = corpus[key].retweets

    for key in corpus:
        likes = np.log(corpus[key].likes + 1)
        likes = (likes - min_likes)/(max_likes-min_likes)
        retweets = np.log(corpus[key].retweets + 1)
        retweets = (retweets - min_retweets)/(max_retweets-min_retweets)
        popularities[key] = likes*0.25 + retweets*0.75

    return popularities 

class SearchEngine:

    def build_index(self, corpus):

        if not os.path.exists(INDEX_PATH):
            self.index = TfIdfIndex(corpus, len(corpus))
            a = {"index": self.index}
            with open(INDEX_PATH, 'wb') as handle:
                pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(INDEX_PATH, 'rb') as handle:
                a = pickle.load(handle)
            self.index = a["index"]


        self.popularity = compute_popularities(corpus)

    def search(self, search_query, search_id, corpus):
        print("Search query:", search_query)
        results = []

        results = search_in_corpus(search_query,
                                   self.index.index,
                                   self.index.tf,
                                   self.index.idf,
                                   self.popularity,
                                   corpus, 
                                   search_id)  # replace with call to search algorithm !!!!!!!!!!!!!!!!!!!!!!!!

        return results
