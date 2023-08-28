from enum import Enum
from typing import List, Dict

# hand, battlefield, graveyard, exile, library

edge_names = {
    ("hand", "battlefield"): ["put", "cast", "morph"],
    ("hand", "graveyard"): ["discard"],
    ("hand", "exile"): ["exile", "foretell", "madness"],
    ("hand", "library"): ["shuffle", "put"],

    ("battlefield", "graveyard"): ["", "sacrifice", "die", "destroy", "damage"],
    ("battlefield", "exile"): ["", "exile"],
    ("battlefield", "library"): ["shuffle", "put"],
    ("battlefield", "hand"): ["return"],

    ("graveyard", "exile"): ["", "exile"],
    ("graveyard", "library"): ["shuffle", "put"],
    ("graveyard", "hand"): ["return"],
    ("graveyard", "battlefield"): ["", "return", "cast"],

    ("exile", "library"): ["shuffle", "put"],
    ("exile", "hand"): ["return"],
    ("exile", "battlefield"): ["return", "cast"],
    ("exile", "graveyard"): ["put"],

    ("library", "hand"): ["draw", "put"],
    ("library", "battlefield"): ["cast", "search"],
    ("library", "graveyard"): ["mill", "search"],
    ("library", "exile"): ["search", "exile"],
}