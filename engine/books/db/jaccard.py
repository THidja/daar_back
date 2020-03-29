import pymongo
from engine.books.db import config
from typing import List, Dict

JaccardGraph = List[Dict]


class JaccardCollection(object):

    _col = None

    @classmethod
    def init(cls):
        if cls._col is None:
            client = pymongo.MongoClient('mongodb://{}:{}/'.format(config['host'], config['port']))
            db = client[config['db']]
            cls._col = db['jaccard']

    @classmethod
    def save(cls, graph: JaccardGraph):
        cls._col.insert_many(graph)

    @classmethod
    def load(cls) -> JaccardGraph:
        return [c for c in cls._col.find({})]

    @classmethod
    def clear(cls):
        cls._col.drop()


JaccardCollection.init()
