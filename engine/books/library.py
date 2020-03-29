from sys import argv
from engine.books.register import BooksRegister
from engine.books.indexer import Indexer
from engine.books.centrality import Centrality
from engine.books.similarity import Similarity

if __name__ == '__main__':

    reset = False
    if len(argv) > 1 and argv[1] == 're_index':
        reset = True
    # register books library
    BooksRegister.register_books(re_register=reset)
    # index book files
    Indexer.index_books(re_index=reset)
    # compute jaccard graph and centrality
    Centrality.compute_centrality(re_compute=reset)
    # compute suggestions for each book
    Similarity.compute_similarity()
