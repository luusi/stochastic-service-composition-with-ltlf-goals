"""Represent a target service."""
from typing import Any, Mapping, Set, Tuple

from mdp_dp_rl.processes.mdp import MDP
from mdp_dp_rl.utils.generic_typevars import A, S
from pythomata.core import DFA
from sympy.logic.boolalg import BooleanTrue

from stochastic_service_composition.composition import DEFAULT_GAMMA
from stochastic_service_composition.types import MDPDynamics


class MdpDfa(MDP):

    initial_state: Any
    failure_state: Any
    all_actions: Set[str]

    def __init__(
        self,
        info: Mapping[S, Mapping[A, Tuple[Mapping[S, float], float]]],
        gamma: float,
    ) -> None:
        super().__init__(info, gamma)

        self.all_actions = set(a for s, trans in info.items() for a, _ in trans.items())


def mdp_from_dfa(dfa: DFA, reward: float = 2.0, gamma: float = DEFAULT_GAMMA) -> MdpDfa:
    transition_function: MDPDynamics = {}

    for _start in dfa.states:
        for start, action, end in dfa.get_transitions_from(_start):
            # TODO: with declare assumption
            # symb = tuple([arg for arg in action.args if not isinstance(arg, Not)])
            # if len(symb) == 1:
            #     symb = str(symb[0])
            dest = ({end: 1.0}, reward if end in dfa.accepting_states else 0.0)
            transition_function.setdefault(start, {}).setdefault(action, dest)

    result = MdpDfa(transition_function, gamma)
    result.initial_state = dfa.initial_state
    result.failure_state = _find_failure_state(dfa)
    return result


def _find_failure_state(dfa: DFA):
    """Find failure state, if any."""
    for state in dfa.states:
        if state in dfa.accepting_states:
            continue
        transitions = dfa.get_transitions_from(state)
        if len(transitions) == 1:
            t = list(transitions)[0]
            start, guard, end = t
            if start == end and isinstance(guard, BooleanTrue):
                # non-accepting, self-loop with true
                return start
    return None
