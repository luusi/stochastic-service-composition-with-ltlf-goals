from typing import cast

from logaut import ltl2dfa
from pylogics.parsers import parse_ltl
from pythomata.impl.symbolic import SymbolicDFA

from stochastic_service_composition.declare_utils import alt_precedence, alt_succession, build_declare_assumption
from stochastic_service_composition.dfa_target import MdpDfa, mdp_from_dfa, from_symbolic_automaton_to_declare_automaton
from stochastic_service_composition.momdp import compute_final_mdp
from stochastic_service_composition.rendering import (
    mdp_to_graphviz,
    service_to_graphviz,
)
from stochastic_service_composition.services import Service

if __name__ == "__main__":
    # without declare
    # formula = parse_ltl("a U b")
    # with declare:
    formula = parse_ltl("(a U b) & (G(a -> !b) & G(b -> !a) & G(a | b))")
    automaton = cast(SymbolicDFA, ltl2dfa(formula, backend="lydia"))
    all_symbols = {"a", "b"}
    mdp: MdpDfa = mdp_from_dfa(from_symbolic_automaton_to_declare_automaton(automaton, all_symbols.union({})))

    cast(SymbolicDFA, automaton).to_graphviz().render("automaton")
    mdp_to_graphviz(mdp).render("mdp")

    a = Service({"a1", "a_broken"}, {"a", "tau_a"}, {"a1"}, "a1", {"a1": {"a": ({"a1": 0.95, "a_broken": 0.05}, (1.0, 1.0))}, "a_broken": {"tau_a": ({"a1": 1.0}, (0.0, 0.0))}})
    b = Service({"b1"}, {"b", "tau_b"}, {"b1"}, "b1", {"b1": {"b": ({"b1": 1.0}, (2.0, 2.0)), "tau_b": ({"b1": 1.0}, (0.0, 0.0))}})
    service_to_graphviz(a).render("service_a")
    service_to_graphviz(b).render("service_b")

    weights = []
    final_mdp = compute_final_mdp(mdp, [a, b], [10.0, 2.0, 1.0])
    mdp_to_graphviz(final_mdp).render("final_mdp")
