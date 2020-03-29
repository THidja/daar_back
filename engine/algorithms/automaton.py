from operator import attrgetter
from engine.algorithms.regex import Operators
from engine.algorithms.regex import RegEx


class Edge(object):

    EPSILON = 0xFFFFFFFF

    def __init__(self, origin, destination, character):
        self.origin = origin
        self.destination = destination
        self.character = character

    def __str__(self):
        char = self.character
        if self.character == Edge.EPSILON:
            char = "epsilon"
        return "{} -- {} --> {}".format(self.origin, char, self.destination)

    def __repr__(self):
        return self.__str__()


class Automaton(object):

    def __init__(self, nb_states):
        self.nb_states = nb_states
        self.first = 0
        self.last = nb_states - 1
        self.edges = []
        self.init = [True] + [False] * (nb_states - 1)
        self.accept = [False] * (nb_states - 1) + [True]

    # public :
    def shift(self, value):
        for edge in self.edges:
            edge.origin = edge.origin + value
            edge.destination = edge.destination + value
        self.first = self.first + value
        self.last = self.last + value

    def _reach_string(self, origin, destination, current, next, text):
        if len(text) == 0:
            return None
        res = [current, next]
        for edge in self.edges:
            if edge.origin == origin and (edge.character == text[0] or edge.character == Operators.DOT):
                if edge.destination == destination:
                    return res
                return self._reach_string(edge.destination, destination, current, next + 1, text[1:])
        return self._reach_string(0, destination, next, next + 1, text[1:])

    @staticmethod
    def _concat(a1, a2):
        a = Automaton(a1.nb_states + a2.nb_states)
        a2.shift(a1.nb_states)
        a.edges = a1.edges + a2.edges
        a.edges.append(Edge(a1.last, a2.first, Edge.EPSILON))
        return a

    @staticmethod
    def _union(a1, a2):
        a = Automaton(a1.nb_states + a2.nb_states + 2)
        a1.shift(1)
        a2.shift(a1.nb_states)
        a.edges = a1.edges + a2.edges
        a.edges.append(Edge(a.first, a1.first, Edge.EPSILON))
        a.edges.append(Edge(a.first, a2.first, Edge.EPSILON))
        a.edges.append(Edge(a1.last, a.last, Edge.EPSILON))
        a.edges.append(Edge(a2.last, a.last, Edge.EPSILON))
        return a

    @staticmethod
    def _closure(a1):
        a = Automaton(a1.nb_states + 2)
        a1.shift(1)
        a.edges = a1.edges
        a.edges.append(Edge(a.first, a1.first, Edge.EPSILON))
        a.edges.append(Edge(a1.last, a.last, Edge.EPSILON))
        a.edges.append(Edge(a.first, a.last, Edge.EPSILON))
        a.edges.append(Edge(a1.last, a1.first, Edge.EPSILON))
        return a

    @classmethod
    def _regex_tree_to_epsilon_automaton(cls, regex_tree):
        if regex_tree.root == Operators.CONCAT:
            a1 = cls._regex_tree_to_epsilon_automaton(regex_tree.subTrees[0])
            a2 = cls._regex_tree_to_epsilon_automaton(regex_tree.subTrees[1])
            return cls._concat(a1, a2)
        elif regex_tree.root == Operators.ASTERISK:
            a1 = cls._regex_tree_to_epsilon_automaton(regex_tree.subTrees[0])
            return cls._closure(a1)
        elif regex_tree.root == Operators.ALTERNATIVE:
            a1 = cls._regex_tree_to_epsilon_automaton(regex_tree.subTrees[0])
            a2 = cls._regex_tree_to_epsilon_automaton(regex_tree.subTrees[1])
            return cls._union(a1, a2)
        elif regex_tree.root == Operators.DOT:
            a = Automaton(2)
            a.edges.append(Edge(a.first, a.last, Operators.DOT))
            return a
        else:
            a = Automaton(2)
            a.edges.append(Edge(a.first, a.last, regex_tree.root))
        a.edges = sorted(a.edges, key=attrgetter('origin', 'destination', 'character'))
        return a

    @classmethod
    def _remove_epsilons_transitions(cls, a):
        epsilons = []
        no_epsilons = []
        for edge in a.edges:
            if edge.character == Edge.EPSILON:
                epsilons.append(edge)
            else:
                no_epsilons.append(edge)

        real_states = [True] + [False] * (a.nb_states - 1)
        nb_states = 1
        for edge in no_epsilons:
            real_states[edge.destination] = True
            nb_states = nb_states + 1

        automaton = Automaton(nb_states)
        done = False
        current = []
        while not done:
            done = True
            for i in range(a.nb_states):
                if not real_states[i]:
                    for epsilon in epsilons:
                        if epsilon.destination == i:
                            for to_change in no_epsilons:
                                if to_change.origin == i:
                                    current.append(Edge(epsilon.origin, to_change.destination, to_change.character))
                                    done = False
                else:
                    for to_keep in no_epsilons:
                        if to_keep.origin == i and real_states[to_keep.destination]:
                            current.append(Edge(to_keep.origin, to_keep.destination, to_keep.character))
            no_epsilons = current
            current = []

        for edge in no_epsilons:
            cpt_origin = cpt_destination = 0
            for i in range(a.nb_states):
                if real_states[i] and i < edge.origin:
                    cpt_origin = cpt_origin + 1
                if real_states[i] and i < edge.destination:
                    cpt_destination = cpt_destination + 1
            automaton.edges.append(Edge(cpt_origin, cpt_destination, edge.character))

        cpt_states = 0
        for i in range(a.nb_states):
            if real_states[i]:
                if cls._reach(i, a.nb_states - 1, epsilons):
                    automaton.accept[cpt_states] = True
                cpt_states = cpt_states + 1
        automaton.edges = sorted(automaton.edges, key=attrgetter('origin', 'destination', 'character'))
        return automaton

    @classmethod
    def _reach(cls, origin, destination, edges):
        for edge in edges:
            if edge.origin == origin:
                if edge.destination == destination:
                    return True
                if cls._reach(edge.destination, destination, edges):
                    return True

        return False

    @classmethod
    def from_regex(cls, regex: str):
        return cls._remove_epsilons_transitions(
            cls._regex_tree_to_epsilon_automaton(RegEx.parse(regex))
        )

    def accept_str(self, text: str):
        for i in range(self.nb_states):
            if self.accept[i]:
                res = self._reach_string(0, i, 0, 1, text)
                if res is not None:
                    return res
        return None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        ret = "nb_states: {} \n".format(self.nb_states)
        ret += "accepting states: "
        for i in range(self.nb_states):
            if self.accept[i]:
                ret = ret + str(i) + " "
        ret += "\nEdges: \n"
        for edge in self.edges:
            ret += str(edge) + "\n"
        return ret
