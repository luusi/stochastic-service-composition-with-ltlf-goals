"""Represent a target service."""

from mdp_dp_rl.processes.mdp import MDP
from pythomata.core import DFA

from stochastic_service_composition.composition import DEFAULT_GAMMA
from stochastic_service_composition.types import MDPDynamics


def mdp_from_dfa(
    dfa: DFA,
    reward: float = 1.0,
    gamma: float = DEFAULT_GAMMA) -> MDP:

    transition_function: MDPDynamics = {}

    for _start in dfa.states:
        for start, action, end in dfa.get_transitions_from(_start):
            # TODO: with declare assumption
            # symb = tuple([arg for arg in action.args if not isinstance(arg, Not)])
            # if len(symb) == 1:
            #     symb = str(symb[0])
            dest = ({end: 1.0}, reward if end in dfa.accepting_states else 0.0)
            transition_function.setdefault(start, {}).setdefault(action, dest)

    result = MDP(transition_function, gamma)
    result.initial_state = dfa.initial_state
    return result
