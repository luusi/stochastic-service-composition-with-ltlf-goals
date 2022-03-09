from typing import cast

from logaut import ltl2dfa
from mdp_dp_rl.processes.mdp import MDP
from pythomata.impl.symbolic import SymbolicDFA

from stochastic_service_composition.dfa_target import mdp_from_dfa

from pylogics.parsers import parse_ltl

from stochastic_service_composition.momdp import compute_final_mdp
from stochastic_service_composition.rendering import mdp_to_graphviz, service_to_graphviz
from stochastic_service_composition.services import Service
from stochastic_service_composition.types import MDPDynamics

if __name__ == '__main__':
    # without declare
    formula = parse_ltl("a U b")
    # with declare:
    # formula = parse_ltl("(a U b) & (G(a -> !b) & G(b -> !a))")
    automaton = ltl2dfa(formula, backend="lydia")
    mdp: MDP = mdp_from_dfa(automaton)

    cast(SymbolicDFA, automaton).to_graphviz().render("automaton")
    mdp_to_graphviz(mdp).render("mdp")

    a = Service({"s1"}, {"a"}, {"s1"}, "s1", {"s1": {"a": ({"s1": 1.0}, 1.0)}})
    b = Service({"s1"}, {"b"}, {"s1"}, "s1", {"s1": {"b": ({"s1": 1.0}, 1.0)}})
    service_to_graphviz(a).render("service_a")
    service_to_graphviz(b).render("service_b")

    weights = []
    final_mdp = compute_final_mdp(mdp, [a, b], [10.0, 1.0, 1.0])
    mdp_to_graphviz(final_mdp).render("final_mdp")
