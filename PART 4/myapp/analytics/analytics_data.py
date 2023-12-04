import json
import random


class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """
    fact_clicks = dict([]) # Key: doc_Id, Value: num_cliks

    fact_queries = dict([]) # Key: Query term, Value: number_of_times_each_term_has_appeared_in_the_query

    fact_time = dict([]) # Key: Query_id, Value: time
    
    def save_query_terms(self, terms: str) -> int:
        print(self)
        return random.randint(0, 100000)


class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
