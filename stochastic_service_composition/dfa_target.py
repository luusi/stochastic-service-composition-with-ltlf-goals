"""Represent a target service."""

from mdp_dp_rl.processes.mdp import MDP

from pylogics.syntax.base import Formula, Logic
from logaut import ltl2dfa
from pylogics.parsers import parse_ltl

def mdp_from_ltlf(
    formula: Formula,
    reward: float = 1.0) -> MDP:
    assert formula.logic == Logic.LTL
    dfa = ltl2dfa(formula, backend="lydia")
    return dfa
