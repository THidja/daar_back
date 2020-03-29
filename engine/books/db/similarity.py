import pymongo
from engine.books.db import config
from typing import Dict, List


class SimilarityCollection(object):

    _col = None

    @classmethod
    def init(cls):
        if not cls._col:
            client = pymongo.MongoClient('mongodb://{}:{}/'.format(config['host'], config['port']))
            db = client[config['db']]
            cls._col = db['similarity']

    @classmethod
    def save(cls, similarity: List[Dict]):
        cls._col.insert_many(similarity)

    @classmethod
    def load(cls) -> Dict:
        res = [c for c in cls._col.find({})]
        ret = {}
        for c in res:
            ret[c['_id']] = c['similar']
        return ret

    @classmethod
    def clear(cls):
        cls._col.drop()


SimilarityCollection.init()
