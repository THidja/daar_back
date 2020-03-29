

class Kmp(object):

    @classmethod
    def search(cls, pattern: str, text: str):
        detention = cls._create_detention(pattern)
        i = j = 0
        while i < len(text):
            if j == len(pattern):
                return i - len(pattern)
            if text[i] == pattern[j]:
                i = i + 1
                j = j + 1
            elif detention[j] == -1:
                i = i + 1
                j = 0
            else:
                j = detention[j]
        return -1

    @staticmethod
    def _create_detention(pattern: str):
        detention = [-1] + [0] * (len(pattern) - 1)
        j = 0
        for i in range(len(pattern)):
            if pattern[i] == pattern[j]:
                detention[i] = detention[j]
            else:
                detention[i] = j
                while j >= 0 and pattern[i] != pattern[j]:
                    j = detention[j]
            j = j + 1
        return detention
