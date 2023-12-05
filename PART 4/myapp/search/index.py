from collections import defaultdict
import math
import array
import numpy as np
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
nltk.download("stopwords")


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


def stem_tweet(line):
    
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    ## START CODE
    line = re.sub(r'[.,;:!?"\'-@]', '', line).replace("#", "").replace("’", "").replace("“", "").replace("\n"," ")
    line =  line.lower() ## Transform in lowercase
    line = remove_emojis(line).strip().replace("  ", " ")
    line = line.split(" ") ## Tokenize the text to get a list of terms
    line =[word for word in line if word not in stop_words]  ## eliminate the stopwords (HINT: use List Comprehension)
    line =[stemmer.stem(word) for word in line] ## perform stemming (HINT: use List Comprehension)
    line = [word for word in line if word != ""]
    ## END CODE
    
    return line

# Function to display the title of the tweet in the search page
def stem_tweet_display_version(line):
    
    line = re.sub(r'[.,;:!?"\'-@]', '', line).replace("#", "").replace("’", "").replace("“", "").replace("\n"," ")
    line = remove_emojis(line).strip().replace("  ", " ")
    
    return line

class TfIdfIndex():

    def __init__(self, corpus, num_documents):
        
        self.index = defaultdict(list)
        self.tf = defaultdict(list)
        self.df = defaultdict(int)
        self.idf = defaultdict(float)

        for key in corpus:

            tweet = corpus[key]
            terms = stem_tweet(tweet.description)

            current_page_index = {}

            for position, term in enumerate(terms):
                try:
                    current_page_index[term][1].append(position)
                except:
                    current_page_index[term] = [key, [position]]

            norm = 0
            for term, posting in current_page_index.items():
                norm += len(posting[1]) ** 2
            norm = math.sqrt(norm)

            for term, posting in current_page_index.items():
                self.tf[term].append(np.round(len(posting[1]) / norm, 4))
                self.df[term] += 1

            for term_page, posting_page in current_page_index.items():
                self.index[term_page].append(posting_page)

            for term in self.df:
                self.idf[term] = np.round(np.log(float(num_documents / self.df[term])), 4)