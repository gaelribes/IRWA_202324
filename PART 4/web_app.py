import os
from json import JSONEncoder
import datetime

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
import pickle
import pandas as pd
import json
from collections import Counter

from flask import Flask, render_template, session
from flask import request

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine

# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# instantiate our search engine
search_engine = SearchEngine()

# instantiate our in memory persistence
analytics_data = AnalyticsData()

# print("current dir", os.getcwd() + "\n")
# print("__file__", __file__ + "\n")
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
# print(path + ' --> ' + filename + "\n")
# load documents corpus into memory.

file_path = path + "/../data/Rus_Ukr_war_data.json"
FILE_PATH_CLICKS = path + "/../data/clicks_data.pkl"
FILE_PATH_QUERIES = path + "/../data/queries_data.pkl"
FILE_PATH_QUERIES_JSON = path + "/../data/queries_data.json"
FILE_PATH_TIME = path + "/../data/time_data.pkl"


# file_path = "../../tweets-data-who.json"
corpus = load_corpus(file_path)
print("\nloaded corpus. first elem:", list(corpus.values())[0], "\n")
print("\nBuilding index....")
search_engine.build_index(corpus)
print("Index built!!\n")

if os.path.exists(FILE_PATH_QUERIES):
    with open(FILE_PATH_QUERIES, 'rb') as handle:
        analytics_data.fact_queries = pickle.load(handle)

if os.path.exists(FILE_PATH_CLICKS):
    with open(FILE_PATH_CLICKS, 'rb') as handle:
        analytics_data.fact_clicks = pickle.load(handle)

# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2021 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    print(session)

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['GET'])
def search_form_post():
    #search_query = request.form['search-query']
    search_query = request.args.get('q')

    session['last_search_query'] = search_query

    search_id = analytics_data.save_query_terms(search_query)
    
    start = datetime.datetime.now()
    results = search_engine.search(search_query, search_id, corpus)
    end = datetime.datetime.now()
    total_time_search = (end-start).total_seconds()
    
    # Store 

    analytics_data.fact_time[search_id] = total_time_search

    with open(FILE_PATH_TIME, 'wb') as handle:
        pickle.dump(analytics_data.fact_time, handle, protocol=pickle.HIGHEST_PROTOCOL)


    if search_query in analytics_data.fact_queries.keys():
        analytics_data.fact_queries[search_query] += 1
    else:
        analytics_data.fact_queries[search_query] = 1

    with open(FILE_PATH_QUERIES, 'wb') as handle:
        pickle.dump(analytics_data.fact_queries, handle, protocol=pickle.HIGHEST_PROTOCOL)


    found_count = len(results)
    session['last_found_count'] = found_count

    print(session)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    # user = request.args.get('user')

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    p1 = int(request.args["search_id"])  # transform to Integer
    #p2 = int(request.args["param2"])  # transform to Integer
    print("click in id={}".format(clicked_doc_id))

    # store "click" data in csv
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    with open(FILE_PATH_CLICKS, 'wb') as handle:
        pickle.dump(analytics_data.fact_clicks, handle, protocol=pickle.HIGHEST_PROTOCOL)


    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))

    return render_template('doc_details.html')#, results_list=results, page_title="Results", found_counter=found_count)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []
    # ### Start replace with your code ###

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    return render_template('stats.html', clicks_data=docs)
    # ### End replace with your code ###


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    print(analytics_data.fact_clicks.keys())
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[int(doc_id)]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)
    visited_docs = [d.to_json() for d in visited_docs ]

    terms_query = json.dumps(analytics_data.fact_queries)
    
    #print(terms_query)
    # for doc in visited_docs: print(doc)
    # print(type(analytics_data.fact_queries))
    # print(visited_docs)
    # print(analytics_data.fact_queries)
    # print(type(terms_query))
    # print(type(visited_docs))
    return render_template('dashboard.html', visited_docs=visited_docs, terms_query = terms_query, page_title="Tweets Dashboard")


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":

    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
