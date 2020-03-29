

class RadixTree(object):

    def __init__(self):
        self.children = {}
        self.indexes = []
        self.end_of_word = False

    def insert_word(self, word, indexes):
        def _insert_word(_root):
            current = _root
            for char in word:
                if char not in current.children.keys():
                    current.children[char] = RadixTree()
                current = current.children[char]
            current.end_of_word = True
            current.indexes = indexes
        _insert_word(self)

    def __contains__(self, word):
        def _search_word(_root):
            current = _root
            for char in word:
                if char not in current.children.keys():
                    return False
                current = current.children[char]
            if current.end_of_word:
                return True
            return False
        return _search_word(self)

    def indexes_of_word(self, word):
        def _indexes_of_word(_root):
            current = _root
            for char in word:
                if char not in current.children.keys():
                    return []
                current = current.children[char]
            if current.end_of_word:
                return current.indexes
            return []
        return _indexes_of_word(self)

    def __getitem__(self, word):
        return self.indexes_of_word(word)

    def all_words(self):
        def inner_all_words(prefix, node, result):
            if node.end_of_word:
                result.append(prefix)
            for char in node.children.keys():
                inner_all_words(prefix + char, node.children[char], result)
        result = []
        inner_all_words('', self, result)
        return result

    @staticmethod
    def jaccard_distance(t1, t2):
        t1_words = set(t1.all_words())
        t2_words = set(t2.all_words())
        union = len(set(t1_words).union(t2_words))
        intersection = len(t1_words.intersection(t2_words))
        return float(union - intersection) / union
