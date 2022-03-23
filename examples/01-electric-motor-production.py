from typing import cast, Set

from logaut import ltl2dfa
from pylogics.parsers import parse_ltl
from pythomata.impl.symbolic import SymbolicDFA

from stochastic_service_composition.declare_utils import exactly_once, absence_2, alt_succession, alt_precedence, \
    build_declare_assumption, not_coexistence
from stochastic_service_composition.dfa_target import mdp_from_dfa
from stochastic_service_composition.rendering import (
    mdp_to_graphviz,
)


BUILD_RETRIEVE_STATOR = "build_retrieve_stator"
BUILD_RETRIEVE_ROTOR = "build_retrieve_rotor"
BUILD_RETRIEVE_INVERTER = "build_retrieve_inverter"
ASSEMBLE_MOTOR = "assemble_motor"
PAINTING = "painting"
RUNNING_IN = "running_in"
ELECTRIC_TEST = "electric_test"
STATIC_TEST = "static_test"

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
        build_declare_assumption(ALL_SYMBOLS),
    ]
    formula_str = " & ".join(map(lambda s: f"({s})", declare_constraints))
    formula = parse_ltl(formula_str)
    automaton = ltl2dfa(formula, backend="lydia")

    print(len(automaton.states))

    cast(SymbolicDFA, automaton).to_graphviz().render("automaton")
    target = mdp_from_dfa(
        automaton
    )
    mdp_to_graphviz(target).render("mdp")
