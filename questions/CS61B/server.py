import itertools
import random
import string

import networkx as nx
import numpy as np
import numpy.linalg as la
import prairielearn as pl


def generate(data):
    data["correct_answers"]["DFSPreorder"] = "9-0-1-6-5-2-7"
    data["correct_answers"]["DFSPostorder"] = "0-2-7-5-6-1-9"
    data["correct_answers"]["BFSOrder"] = "9-0-1-2-6-7-5"

    data["correct_answers"]["trie1"] = "U"
    data["correct_answers"]["trie2"] = "E"
    data["correct_answers"]["trie3"] = "N/A"
    data["correct_answers"]["trie4"] = "F"
    data["correct_answers"]["trie5"] = "I"
    data["correct_answers"]["trie6"] = "G"
    data["correct_answers"]["trie7"] = "M"
    data["correct_answers"]["trie8"] = "A"
    data["correct_answers"]["trie9"] = "T"
    data["correct_answers"]["trie10"] = "R"
    data["correct_answers"]["trie11"] = "U"
    data["correct_answers"]["trie12"] = "E"
    data["correct_answers"]["trie13"] = "N/A"
    data["correct_answers"]["trie14"] = "N/A"
    data["correct_answers"]["trie15"] = "N/A"
    data["correct_answers"]["underlined"] = "2, 6, 8, 12"
    
    data["correct_answers"]["ab1"] = "U"
    data["correct_answers"]["ab2"] = "E"
    data["correct_answers"]["ab3"] = "N/A"
    data["correct_answers"]["ab4"] = "F"
    data["correct_answers"]["ab5"] = "I"
    data["correct_answers"]["ab6"] = "G"
    data["correct_answers"]["ab7"] = "M"
    data["correct_answers"]["ab8"] = "A"
    data["correct_answers"]["ab9"] = "T"
    data["correct_answers"]["ab10"] = "R"
    data["correct_answers"]["ab11"] = "U"
    data["correct_answers"]["ab12"] = "E"
    data["correct_answers"]["ab13"] = "N/A"
    data["correct_answers"]["ab14"] = "N/A"
    data["correct_answers"]["ab15"] = "N/A"
    data["correct_answers"]["ab16"] = "N/A"