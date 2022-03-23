from enum import Enum
from typing import cast, Set

from logaut import ltl2dfa
from pylogics.parsers import parse_ltl
from pythomata.impl.symbolic import SymbolicDFA

from stochastic_service_composition.dfa_target import MdpDfa, mdp_from_dfa
from stochastic_service_composition.momdp import compute_final_mdp
from stochastic_service_composition.rendering import (
    mdp_to_graphviz,
    service_to_graphviz,
)
from stochastic_service_composition.services import Service

"""
(F build_retrieve_stator & !F (build_retrieve_stator & F build_retrieve_stator)) & 
(F assemble_motor & !F (assemble_motor & F assemble_motor)) & 
(G(build_retrieve_stator -> X(!build_retrieve_stator U assemble_motor)) & (!assemble_motor W build_retrieve_stator) & G(assemble_motor -> X(!assemble_motor W build_retrieve_stator))) & 
(F build_retrieve_rotor & !F (build_retrieve_rotor & F build_retrieve_rotor)) & (G(build_retrieve_rotor -> X(!build_retrieve_rotor U assemble_motor)) & (!assemble_motor W build_retrieve_rotor) & G(assemble_motor -> X(!assemble_motor W build_retrieve_rotor))) & (F build_retrieve_inverter & !F (build_retrieve_inverter & F build_retrieve_inverter)) & (G(build_retrieve_inverter -> X(!build_retrieve_inverter U assemble_motor)) & (!assemble_motor W build_retrieve_inverter) & G(assemble_motor -> X(!assemble_motor W build_retrieve_inverter))) & (! F(painting & F painting)) & ((!painting W assemble_motor) & G(painting -> X(! painting W assemble_motor))) & (F running_in & !F (running_in & F running_in)) & (G(assemble_motor -> X(!assemble_motor U running_in)) & (!running_in W assemble_motor) & G(running_in -> X (!running_in W assemble_motor))) & (! F(static_test & F static_test)) & ((!static_test W assemble_motor) & G(static_test -> X(! static_test W assemble_motor))) & (!(F electric_test & F static_test)) & (! F(electric_test & F electric_test)) & ((!electric_test W assemble_motor) & G(electric_test -> X(! electric_test W assemble_motor)))")
"""


def weak_until(a, b):
    return f"(G({a}) | ({a} U {b}))"


def absence_2(a):
    return f"G({a} | G(!{a}))"


def exactly_once(a):
    return f"(F({a}) & G({a} -> XG(!{a})))"


def alt_response(a, b):
    return f"(G({a} -> X[!](!{a} U {b})))"


def alt_succession(a, b):
    return f"({alt_response(a, b)} & {alt_precedence(a, b)})"


def alt_precedence(a, b):
    return f"({weak_until(f'!{b}', a)} & G({b} -> X({weak_until(f'!{b}', a)})))"


def not_coexistence(a, b):
    return f"G(G(!{a}) | G(!{b}))"


def declare(all_symbols: Set[str]) -> str:
    assert len(all_symbols) > 1
    at_least_one = f"G({' | '.join(all_symbols)})"
    at_most_one_subformulas = []
    for symbol in all_symbols:
        all_nots = " & ".join(map(lambda s: "!" + s, all_symbols.difference([symbol])))
        subformula = f"G({symbol} -> ({all_nots}))"
        at_most_one_subformulas.append(subformula)
    at_most_one = " & ".join(at_most_one_subformulas)
    return f"{at_least_one} & {at_most_one}"


BUILD_RETRIEVE_STATOR = "buildretrievestator"
BUILD_RETRIEVE_ROTOR = "buildretrieverotor"
BUILD_RETRIEVE_INVERTER = "buildretrieveinverter"
ASSEMBLE_MOTOR = "assemblemotor"
PAINTING = "painting"
RUNNING_IN = "runningin"
ELECTRIC_TEST = "electrictest"
STATIC_TEST = "statictest"

ALL_SYMBOLS = {
    BUILD_RETRIEVE_STATOR,
    BUILD_RETRIEVE_ROTOR,
    BUILD_RETRIEVE_INVERTER,
    ASSEMBLE_MOTOR,
    PAINTING,
    RUNNING_IN,
    ELECTRIC_TEST,
    STATIC_TEST,
}


if __name__ == '__main__':
    declare_constraints = [
        exactly_once(BUILD_RETRIEVE_STATOR),
        exactly_once(BUILD_RETRIEVE_ROTOR),
        exactly_once(BUILD_RETRIEVE_INVERTER),
        exactly_once(RUNNING_IN),
        exactly_once(ASSEMBLE_MOTOR),
        absence_2(ELECTRIC_TEST),
        absence_2(PAINTING),
        absence_2(STATIC_TEST),
        alt_succession(BUILD_RETRIEVE_STATOR, ASSEMBLE_MOTOR),
        alt_succession(BUILD_RETRIEVE_ROTOR, ASSEMBLE_MOTOR),
        alt_succession(BUILD_RETRIEVE_INVERTER, ASSEMBLE_MOTOR),
        alt_succession(ASSEMBLE_MOTOR, RUNNING_IN),
        alt_precedence(ASSEMBLE_MOTOR, PAINTING),
        alt_precedence(ASSEMBLE_MOTOR, ELECTRIC_TEST),
        alt_precedence(ASSEMBLE_MOTOR, STATIC_TEST),
        not_coexistence(ELECTRIC_TEST, STATIC_TEST),
        declare(ALL_SYMBOLS)
    ]

    formula_str = " & ".join(map(lambda s: f"({s})", declare_constraints))

    print(formula_str)


    formula = parse_ltl(formula_str)
    automaton = ltl2dfa(formula, backend="lydia")
    #
    # for trace in [
    #     [],
    #     [{"build_retrieve_stator": True}],
    #     [{"build_retrieve_stator": True}, {"build_retrieve_stator": True}]
    # ]:
    #     print(f"trace: {trace}. accepts: {automaton.accepts(trace)}")

    print(len(automaton.states))
    cast(SymbolicDFA, automaton).to_graphviz().render("automaton")

    # formula = parse_ltl(
    #     "(F build_retrieve_stator & !F (build_retrieve_stator & F build_retrieve_stator)) & (F assemble_motor & !F (assemble_motor & F assemble_motor)) & (G(build_retrieve_stator -> X(!build_retrieve_stator U assemble_motor)) & (!assemble_motor W build_retrieve_stator) & G(assemble_motor -> X(!assemble_motor W build_retrieve_stator))) & (F build_retrieve_rotor & !F (build_retrieve_rotor & F build_retrieve_rotor)) & (G(build_retrieve_rotor -> X(!build_retrieve_rotor U assemble_motor)) & (!assemble_motor W build_retrieve_rotor) & G(assemble_motor -> X(!assemble_motor W build_retrieve_rotor))) & (F build_retrieve_inverter & !F (build_retrieve_inverter & F build_retrieve_inverter)) & (G(build_retrieve_inverter -> X(!build_retrieve_inverter U assemble_motor)) & (!assemble_motor W build_retrieve_inverter) & G(assemble_motor -> X(!assemble_motor W build_retrieve_inverter))) & (! F(painting & F painting)) & ((!painting W assemble_motor) & G(painting -> X(! painting W assemble_motor))) & (F running_in & !F (running_in & F running_in)) & (G(assemble_motor -> X(!assemble_motor U running_in)) & (!running_in W assemble_motor) & G(running_in -> X (!running_in W assemble_motor))) & (! F(static_test & F static_test)) & ((!static_test W assemble_motor) & G(static_test -> X(! static_test W assemble_motor))) & (!(F electric_test & F static_test)) & (! F(electric_test & F electric_test)) & ((!electric_test W assemble_motor) & G(electric_test -> X(! electric_test W assemble_motor)))")
    # automaton = ltl2dfa(formula, backend="lydia")
    # cast(SymbolicDFA, automaton).to_graphviz().render("automaton")
    target = mdp_from_dfa(
        automaton
    )
    mdp_to_graphviz(target).render("mdp")
