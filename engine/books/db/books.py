from typing import Dict, List
from engine.books.db import config
import pymongo


class BooksCollection(object):

    _col = None

    @classmethod
    def init(cls):
        if cls._col is None:
            client = pymongo.MongoClient('mongodb://{}:{}/'.format(config['host'], config['port']))
            db = client[config['db']]
            cls._col = db['books']

    @classmethod
    def add_book_infos(cls, book_infos: Dict):
        cls._col.insert_one(book_infos)

    @classmethod
    def update_book_infos(cls, book_infos: Dict):
        query = {'_id': book_infos['_id']}
        cls._col.delete_one(query)
        cls._col.insert_one(book_infos)

    @classmethod
    def get_books_infos(cls) -> Dict:
        result = dict()
        for d in cls._col.find({}):
            result[d['_id']] = d
        return result

    @classmethod
    def get_registered_books_id(cls) -> List[int]:
        db_result = cls._col.find({}, {'_id': 1})
        result = [d['_id'] for d in db_result]
        return result


BooksCollection.init()
