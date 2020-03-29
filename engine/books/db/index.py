import pymongo
from engine.books.db import config
from typing import Dict, List


class IndexCollection(object):

    _col = None

    @classmethod
    def init(cls):
        if cls._col is None:
            client = pymongo.MongoClient('mongodb://{}:{}/'.format(config['host'], config['port']))
            db = client[config['db']]
            cls._col = db['index']

    @classmethod
    def add_index(cls, index: Dict):
        cls._col.insert_one(index)

    @classmethod
    def update_index(cls, index: Dict):
        query = {'_id': index['_id']}
        cls._col.delete_one(query)
        cls._col.insert_one(index)

    @classmethod
    def add_indexes(cls, indexes: List[Dict]):
        cls._col.insert_many(indexes)

    @classmethod
    def get_indexes(cls) -> List[Dict]:
        return [index for index in cls._col.find({})]

    @classmethod
    def get_indexed_books_id(cls) -> List[int]:
        cursor = cls._col.find({}, {'_id': 1})
        result = [c['_id'] for c in cursor]
        return result

    @classmethod
    def update_index_score(cls, index_id: int, score: float):
        query = {'_id': index_id}
        update = {'$set': {'score': score}}
        cls._col.update_one(query, update)


IndexCollection.init()
