from enum import Enum


class Operators(Enum):
    CONCAT = 0xC04CA7
    ASTERISK = 0xE7011E
    ALTERNATIVE = 0xA17E54
    PROTECTION = 0xBADDAD
    OPEN_BRACKET = 0x16641664
    CLOSE_BRACKET = 0x51515151
    DOT = 0xD07


class RegEx(object):

    @classmethod
    def parse(cls, regex):
        result = []
        for c in regex:
            result.append(RegExTree(cls._char_to_node_value(c), []))

        return cls._parse(result)

    @staticmethod
    def _char_to_node_value(c: str):
        values = {
            '.': Operators.DOT,
            '*': Operators.ASTERISK,
            '|': Operators.ALTERNATIVE,
            '(': Operators.OPEN_BRACKET,
            ')': Operators.CLOSE_BRACKET
        }
        if c in values:
            return values[c]
        return c

    @classmethod
    def _parse(cls, result):
        while cls._contains_bracket(result):
            result = cls._process_bracket(result)
        while cls._contains_asterisk(result):
            result = cls._process_asterisk(result)
        while cls._contains_concat(result):
            result = cls._process_concat(result)
        while cls._contains_alternative(result):
            result = cls._process_alternative(result)

        if len(result) > 1:
            raise Exception()

        return cls._remove_protection(result[0])

    @staticmethod
    def _contains_bracket(trees):
        for tree in trees:
            if tree.root == Operators.OPEN_BRACKET or tree.root == Operators.CLOSE_BRACKET:
                return True
        return False

    @classmethod
    def _process_bracket(cls, trees):
        result = []
        found = False
        for tree in trees:
            if not found and tree.root == Operators.CLOSE_BRACKET:
                done = False
                content = []
                while not done and len(result) != 0:
                    if result[-1].root == Operators.OPEN_BRACKET:
                        done = True
                        del result[-1]
                    else:
                        content.insert(0, result.pop())
                if not done:
                    raise Exception()
                found = True
                sub_trees = [cls._parse(content)]
                result.append(RegExTree(Operators.PROTECTION, sub_trees))
            else:
                result.append(tree)
        if not found:
            raise Exception()
        return result

    @staticmethod
    def _contains_asterisk(trees):
        for tree in trees:
            if tree.root == Operators.ASTERISK and len(tree.subTrees) == 0:
                return True
        return False

    @staticmethod
    def _process_asterisk(trees):
        result = []
        found = False
        for tree in trees:
            if not found and tree.root == Operators.ASTERISK and len(tree.subTrees) == 0:
                if len(result) == 0:
                    raise Exception()
                found = True
                sub_trees = [result.pop()]
                result.append(RegExTree(Operators.ASTERISK, sub_trees))
            else:
                result.append(tree)
        return result

    @staticmethod
    def _contains_concat(trees):
        first_found = False
        for tree in trees:
            if not first_found and tree.root != Operators.ALTERNATIVE:
                first_found = True
                continue
            if first_found:
                if tree.root != Operators.ALTERNATIVE:
                    return True
                else:
                    first_found = False
        return False

    @staticmethod
    def _process_concat(trees):
        result = []
        found = first_found = False
        for tree in trees:
            if not found and not first_found and tree.root != Operators.ALTERNATIVE:
                first_found = True
                result.append(tree)
                continue
            if not found and first_found and tree.root == Operators.ALTERNATIVE:
                first_found = False
                result.append(tree)
                continue
            if not found and first_found and tree.root != Operators.ALTERNATIVE:
                found = True
                sub_trees = [result.pop(), tree]
                result.append(RegExTree(Operators.CONCAT, sub_trees))
            else:
                result.append(tree)
        return result

    @staticmethod
    def _contains_alternative(trees):
        for tree in trees:
            if tree.root == Operators.ALTERNATIVE and len(tree.subTrees) == 0:
                return True
        return False

    @staticmethod
    def _process_alternative(trees):
        result = []
        found = done = False
        left = None
        for tree in trees:
            if not found and tree.root == Operators.ALTERNATIVE and len(tree.subTrees) == 0:
                if len(result) == 0:
                    raise Exception()
                found = True
                left = result.pop()
                continue
            if found and not done:
                if left is None:
                    raise Exception()
                done = True
                sub_trees = [left, tree]
                result.append(RegExTree(Operators.ALTERNATIVE, sub_trees))
            else:
                result.append(tree)
        return result

    @classmethod
    def _remove_protection(cls, tree):
        if tree.root == Operators.PROTECTION and len(tree.subTrees) != 1:
            raise Exception()
        if len(tree.subTrees) == 0:
            return tree
        if tree.root == Operators.PROTECTION:
            return cls._remove_protection(tree.subTrees[0])
        sub_trees = []
        for t in tree.subTrees:
            sub_trees.append(cls._remove_protection(t))
        return RegExTree(tree.root, sub_trees)


class RegExTree(object):

    def __init__(self, root, sub_trees):
        self.root = root
        self.sub_tree = sub_trees

    def _root_to_str(self):
        values = {
            Operators.CONCAT:       '.',
            Operators.ALTERNATIVE:  '|',
            Operators.ASTERISK:     '*',
            Operators.DOT:          '.'
        }
        if self.root in values:
            return values[self.root]
        return self.root

    def __repr__(self):
        if len(self.sub_tree) == 0:
            return self._root_to_str()
        sub_trees_str = ""
        for sub_tree in self.sub_tree:
            sub_trees_str = sub_trees_str + ", {}".format(sub_tree.__repr__())
        return "({}{})".format(self._root_to_str(), sub_trees_str)
