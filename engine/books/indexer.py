import logging
from engine import Config
from engine.books.db.index import IndexCollection
from engine.books.db.books import BooksCollection


class Indexer(object):

    _stop_words = None
    _special_characters = " !\"#$%&()*+,-./:;<=>?@[\\]^_`{|}~123456789"
    _books_path = '{}/books'.format(Config.resources_path)
    _logger = logging.getLogger(__name__)

    @classmethod
    def init(cls):
        if cls._stop_words is None:
            f = open('{}/indexing/stop_words'.format(Config.resources_path))
            cls._stop_words = [word.strip() for word in f.readlines()]
            f.close()

    @classmethod
    def index_books(cls, re_index=False):
        """
        for each book registered, read the associated file and build its index
        """
        cls._logger.info('running books indexing')
        cpt = 0
        registered_books = BooksCollection.get_books_infos()
        indexed_books_id = IndexCollection.get_indexed_books_id()
        for book_id in registered_books:
            if not re_index and book_id in indexed_books_id:
                continue
            file_path = '%s/%s' % (cls._books_path, registered_books[book_id]['local_file_name'])
            words = cls._get_book_words(file_path)
            book_index = {
                '_id': book_id,
                'score': 0,
                'words': words
            }
            if re_index and book_id in indexed_books_id:
                IndexCollection.update_index(book_index)
            else:
                IndexCollection.add_index(book_index)
            cpt = cpt + 1
            cls._logger.info('indexing book[id=%d]' % book_id)
        cls._logger.info('%d books indexed' % cpt)

    @classmethod
    def _get_book_words(cls, book_path: str):
        f = open(book_path, encoding='utf-8')
        lines = f.readlines()
        book_words = {}
        line_index = 0
        for line in lines:
            line_index = line_index + 1
            line = line.strip()
            if len(line) != 0:
                word = ''
                column_index = 0
                for c in line:
                    column_index = column_index + 1
                    if c in cls._special_characters:
                        if cls._is_word_accepted(word):
                            word = word.lower()
                            if word in book_words:
                                book_words[word] = book_words[word] + 1
                            else:
                                book_words[word] = 1
                        del word
                        word = ''
                    else:
                        word = word + c
        f.close()
        return book_words

    @staticmethod
    def _is_word_accepted(word: str):
        return len(word) >= 3 and word not in Indexer._stop_words


Indexer.init()
