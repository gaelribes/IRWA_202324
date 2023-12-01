from collections import defaultdict
import collections
import numpy as np
from numpy import linalg as la


from myapp.search.index import stem_tweet
from myapp.search.objects import ResultItem


def rank(stemmed_query, unranked_results, index, tf, idf, our_score, alpha):
                                        
    doc_vectors = defaultdict(lambda: [0] * len(stemmed_query))
    query_vector = [0] * len(stemmed_query)

    query_terms_count = collections.Counter(stemmed_query)

    query_norm = la.norm(list(query_terms_count.values()))

    for termIndex, term in enumerate(stemmed_query):
        if term not in index:
            continue
        query_vector[termIndex] = query_terms_count[term] / query_norm * idf[term]

        for doc_index, (doc, postings) in enumerate(index[term]):

            if doc in unranked_results:
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term] 

    doc_scores = [[(1-alpha) * np.dot(curDocVec, query_vector) +
                    alpha * our_score[doc], doc] for doc, curDocVec in doc_vectors.items()]
    doc_scores.sort(reverse=True)
    result_docs = [x[1] for x in doc_scores]

    return result_docs

def search_in_corpus(query, index, tf, idf, popularity, corpus, search_id, alpha=0.5):

        query = stem_tweet(query)
        docs = set()
        for term in query:
            try:
                # store in term_docs the ids of the docs that contain "term"
                term_docs = set([posting[0] for posting in index[term]])
                                          
                # retain all documents which contain all words from the query
                if len(docs)==0:
                    docs = term_docs
                else:
                    docs = docs.intersection(term_docs)
            except:
                #term is not in index
                pass
            
        docs = list(docs) #docs are the unranked results
                                          
        ranked_docs = rank(query, docs, index, tf, idf, popularity, alpha)

        results = []
        counter = 1 #store the ranking position
        for i, num in zip(ranked_docs, range(len(ranked_docs))):
            item = corpus[i]
            results.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                                "doc_details?id={}&search_id={}&ranking={}".format(item.id, search_id, counter), num+1))
            counter+=1

        return results