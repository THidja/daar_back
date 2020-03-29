import os
import re
import requests
import logging

from engine.books.db.books import BooksCollection
from engine import Config


class BooksRegister(object):

    _logger = logging.getLogger(__name__)

    _books_path = Config.books_path

    @classmethod
    def _get_book_infos(cls, book_id: int):
        """
        retrieve information about the book whose id is specified as a parameter
        as an example of information recover the subjects of the book
        information is retrieved from gutindex.com
        """
        res = requests.get('http://gutendex.com/books/{book_id}'.format(book_id=book_id))
        if res.status_code == 200:
            res.encoding = 'utf-8'
            return res.json()
        else:
            warning_msg = 'book[id=%d] infos could not be retrieved, reason: %s' % (book_id, res.text)
            cls._logger.warning(warning_msg)

    @classmethod
    def _get_book_cover_link(cls, book_id: int):
        """
        check if a cover photo is available for the book,
        if it is, retrieve its link,
        otherwise return an empty string
        """
        pic_url = 'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg'.format(book_id=book_id)
        res = requests.head(pic_url)
        if res.status_code == 200:
            return pic_url
        return ""

    @classmethod
    def register_books(cls, re_register=False):
        """
        for each book file present in the resources, retrieve information and its cover photo
        each time this function is called, an update is made in relation to the books already saved
        param to true, the function overwrites the existing data so no update
        """
        cls._logger.info('running books registration')
        cpt = 0
        for file_name in os.listdir(cls._books_path):
            match = re.match(r'([0-9]+).+', file_name)
            registered_books = BooksCollection.get_registered_books_id()
            if match:
                book_id = int(match.group(1))
                if not re_register and book_id in registered_books:
                    continue
                infos = cls._get_book_infos(book_id)
                del infos['id']
                infos['_id'] = book_id
                infos['local_file_name'] = file_name
                infos['cover_link'] = cls._get_book_cover_link(book_id)
                if re_register and book_id in registered_books:
                    BooksCollection.update_book_infos(infos)
                else:
                    BooksCollection.add_book_infos(infos)
                cpt = cpt + 1
                cls._logger.info("%d book(s) registered" % cpt)
