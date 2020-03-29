from engine.books.db.books import BooksCollection
from engine.books.db.jaccard import JaccardCollection
from engine.books.db.similarity import SimilarityCollection
import logging


class Similarity(object):

    _graph = None
    _infos = None
    _logger = logging.getLogger(__name__)

    @classmethod
    def compute_similarity(cls, n=10, re_compute=True):
        """
        :param graph: Jaccard graph of the books library
        :param infos: books information
        :param n: number of similar books to compute for each book
        :param re_compute: recompute similarity
        """
        cls._logger.info("start computing books similarities")
        cls._infos = BooksCollection.get_books_infos()
        cls._graph = JaccardCollection.load()
        if re_compute:
            SimilarityCollection.clear()
        # for each book compute list of 10 books similar
        books_id = BooksCollection.get_registered_books_id()
        result = []
        # for each book found the n most similar books
        for bi in books_id:
            bj = None
            similar = []
            # compute similarity with all other books for bi
            for edge in cls._graph:
                if edge['s'] == bi:
                    bj = edge['t']
                elif edge['t'] == bi:
                    bj = edge['s']
                else:
                    continue
                s = cls._books_similarity(bi, bj, edge['w'])
                similar.append({'id': bj, 's': s})
            # sort computed similarities for bi and select the most n similar
            similar = sorted(similar, key=lambda e: e['s'], reverse=True)
            similar = [e['id'] for e in similar[0:n]]
            cls._logger.info('similarity computed for book[id:%d]' % bi)
            result.append({'_id': bi, 'similar': similar})
        # saved computed similarities
        SimilarityCollection.save(result)
        cls._logger.info("similarities computed and saved")

    @classmethod
    def _books_similarity(cls, b1_id: int, b2_id: int, jc_distance: float):
        b1_infos = cls._infos[b1_id]
        b2_infos = cls._infos[b2_id]
        # titles similarity
        ts = cls._sequence_similarity(b1_infos['title'], b2_infos['title'])
        # subjects similarity
        ss = cls._sequence_similarity(b1_infos['subjects'], b2_infos['subjects'])
        # authors similarity
        b1_authors = [a['name'] for a in b1_infos['authors']]
        b2_authors = [a['name']for a in b2_infos['authors']]
        ats = cls._sequence_similarity(b1_authors, b2_authors)
        # content similarity
        js = 1 - jc_distance
        # and compute books similarity
        return 0.4 * js + 0.15 * ats + 0.15 * ts + 0.3 * ss

    @classmethod
    def _sequence_similarity(cls, str1, str2):
        s1 = set(str1)
        s2 = set(str2)
        if len(s1.union(s2)) == 0:
            return 0
        similarity = len(s1.intersection(s2)) / len(s1.union(s2))
        return similarity
