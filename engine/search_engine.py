import re
import logging
from engine.books.db.books import BooksCollection
from engine.books.db.index import IndexCollection
from engine.books.db.similarity import SimilarityCollection

logger = logging.getLogger(__name__)


class SearchEngine(object):

    def __init__(self, response_filter=lambda x: x):
        # load indexes and sort theme by the centrality score
        self._indexes = IndexCollection.get_indexes()
        self._indexes.sort(key=lambda x: x['score'], reverse=True)
        # to optimize advanced search
        for index in self._indexes:
            index['book_words'] = ' '.join(index['words'])
        # load books infos, filter and render infos using user response_filter function
        # used to search
        self._infos = BooksCollection.get_books_infos()
        # used to return, rendered as user want
        self._books_infos = {}
        for book_id in self._infos:
            self._books_infos[book_id] = response_filter(self._infos[book_id])
        # load suggestions
        self._similarities = SimilarityCollection.load()

    def simple_search(self, word: str):
        result = []
        for index in self._indexes:
            if word in index['words']:
                result.append(self._books_infos[index['_id']])
        return result

    def advanced_search(self, pattern: str, criteria=None):
        result = []
        for index in self._indexes:
            index_id = index['_id']
            if criteria:
                if not criteria.filter(self._infos[index_id]):
                    continue
                elif pattern == '':
                    result.append(self._books_infos[index_id])
            pattern = pattern.replace('.', '[^ ]')
            if re.search(pattern, index['book_words']):
                result.append(self._books_infos[index_id])
        return result

    def similar_books(self, book_id: int):
        if book_id not in self._infos:
            return []
        return [self._books_infos[b_id] for b_id in self._similarities[book_id]]


class SearchCriteria(object):

    def __init__(self, language=None, author=None, subject=None, title=None):
        self.language = language
        self.author = author
        self.subject = subject
        self.title = title

    def _language_filter(self, book_infos):
        if not self.language:
            return True
        return self.language in book_infos['languages']

    def _title_filter(self, book_infos):
        if not self.title:
            return True
        return self.title in book_infos['title'].lower()

    def _author_filter(self, book_infos):
        if not self.author:
            return True
        book_authors = [author['name'].lower() for author in book_infos['authors']]
        for auth in book_authors:
            if self.author in auth:
                return True
        return False

    def _subject_filter(self, book_infos):
        if not self.subject:
            return True
        book_subjects = [subject.lower() for subject in book_infos['subjects']]
        for subject in book_subjects:
            if self.subject in subject or subject in self.subject:
                return True
        return False

    def filter(self, book):
        return self._author_filter(book) and self._language_filter(book) and self._subject_filter(book) \
               and self._title_filter(book)
