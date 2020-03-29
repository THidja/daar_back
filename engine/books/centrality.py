from engine.books.db.index import IndexCollection
from engine.books.db.jaccard import JaccardCollection
import numpy as np
from typing import List, Dict
import logging

JaccardGraph = List[Dict]


class Centrality(object):

    _logger = logging.getLogger(__name__)

    @classmethod
    def compute_centrality(cls, re_compute=False):
        """
        for the books database, calculate the associated jaccard graph,
            the closeness of each book and record these two calculations
        """
        cls._logger.info('computing centrality')
        # indexed books
        indexes = IndexCollection.get_indexes()
        if re_compute:
            JaccardCollection.clear()
        graph = JaccardCollection.load()
        if len(graph) == 0:
            # first compute or re-compute
            graph = cls._compute_jaccard_graph(indexes)
        else:
            # update the Jaccard graph
            old = []
            new = []
            for i in indexes:
                found = False
                for e in graph:
                    if i['_id'] == e['s'] or i['_id'] == e['t']:
                        found = True
                        break
                if found:
                    old.append(i)
                else:
                    new.append(i)
                if len(new) == 0:
                    cls._logger.debug('nothing to update')
                    return
                graph = cls._compute_jaccard_graph(old, new)
        # convert Jaccard graph to numpy matrix to facilitate operations on the graph
        cls._logger.debug('converting Jaccard graph to numpy matrix')
        graph_matrix = cls._jaccard_matrix(graph, indexes)
        cls._logger.debug('floyd warshall on the graph')
        shortest_paths = cls._floyd_warshall(graph_matrix)
        cls._logger.info('computing closeness of each node')
        for i in range(len(indexes)):
            ci = cls._closeness_centrality(shortest_paths, i)
            IndexCollection.update_index_score(indexes[i]['_id'], ci)
        cls._logger.info('all done :) , centrality computed and saved')

    @classmethod
    def _compute_jaccard_graph(cls, indexes: List[Dict], new_indexes=None):
        graph: JaccardGraph = []
        n = len(indexes)
        if new_indexes is None:
            cls._logger.info('computing Jaccard graph')
            for i in range(n):
                for j in range(i + 1, n):
                    wij = Centrality._jaccard_distance(indexes[i]['words'], indexes[j]['words'])
                    doc = {'s': indexes[i]['_id'], 't': indexes[j]['_id'], 'w': wij}
                    graph.append(doc)
        else:
            cls._logger.info('updating Jaccard graph')
            for i in range(len(new_indexes)):
                for j in range(len(indexes)):
                    wij = Centrality._jaccard_distance(new_indexes[i]['words'], indexes[j]['words'])
                    doc = {'s': new_indexes[i]['_id'], 'j': indexes[j]['_id'], 'w': wij}
                    graph.append(doc)
        JaccardCollection.save(graph)
        return graph

    @classmethod
    def _jaccard_matrix(cls, graph: JaccardGraph, indexes: List[Dict]):
        n = len(indexes)
        matrix = np.zeros((n, n), dtype=float)
        mapping = {}
        for i in range(n):
            mapping[indexes[i]['_id']] = i
        for edge in graph:
            i = mapping[edge['s']]
            j = mapping[edge['t']]
            matrix[i, j] = edge['w']
            matrix[j, i] = edge['w']
        return matrix

    @classmethod
    def _floyd_warshall(cls, matrix):
        n = matrix.shape[0]
        d = matrix.copy()
        for k in range(n):
            d = np.minimum(d, d[np.newaxis, k, :] + d[:, k, np.newaxis])
        return d

    @classmethod
    def _closeness_centrality(cls, d, i):
        n = d.shape[0]
        cc = 0
        for j in range(n):
            if i != j:
                cc = cc + d[i, j]
        return (n-1) / cc

    @staticmethod
    def _jaccard_distance(words1, words2):
        s1 = set(words1)
        s2 = set(words2)
        union = len(set(s1).union(s2))
        intersection = len(s1.intersection(s2))
        return float(union - intersection) / union
