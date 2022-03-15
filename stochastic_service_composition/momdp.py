from collections import deque
from typing import Deque, Dict, List, Set, Tuple

from sympy import Symbol
from sympy.logic.boolalg import And, BooleanFunction, Or

from stochastic_service_composition.dfa_target import MdpDfa
from stochastic_service_composition.services import Service, build_system_service
from stochastic_service_composition.types import Action, MDPDynamics, State


def guard_to_symbol(prop_formula: BooleanFunction) -> Set[str]:
    """From guard to symbol."""
    if isinstance(prop_formula, Symbol):
        return {str(prop_formula)}
    elif isinstance(prop_formula, And):
        symbol_args = [arg for arg in prop_formula.args if isinstance(arg, Symbol)]
        assert len(symbol_args) == 1
        return {str(symbol_args[0])}
    elif isinstance(prop_formula, Or):
        operands_as_symbols = [
            symb for arg in prop_formula.args for symb in guard_to_symbol(arg)
        ]
        operands_as_symbols = list(filter(lambda x: x is not None, operands_as_symbols))
        assert len(operands_as_symbols) > 0
        return set(operands_as_symbols)
    # None case
    return None


def get_system_transition_function_by_symbol(
    system_service: Service,
) -> Dict[State, Dict[Action, Dict[int, Tuple[Dict[int, float], float]]]]:
    new_system_transition_function = {}
    for (
        start_state,
        next_transitions_by_action,
    ) in system_service.transition_function.items():
        new_trans_by_symbol_and_service = {}
        for (symbol, service_id), next_trans_dist in next_transitions_by_action.items():
            new_trans_by_symbol_and_service.setdefault(symbol, {})[
                service_id
            ] = next_trans_dist
        new_system_transition_function[start_state] = new_trans_by_symbol_and_service
    return new_system_transition_function


def compute_final_mdp(
    mdp_ltlf: MdpDfa, services: List[Service], weights: List[float]
) -> MdpDfa:
    assert len(weights) == len(services) + 1

    system_service = build_system_service(*services)
    system_transition_function_by_symbol = get_system_transition_function_by_symbol(
        system_service
    )

    transition_function: MDPDynamics = {}

    visited = set()
    to_be_visited = set()
    queue: Deque = deque()

    # add initial transitions
    initial_state = (system_service.initial_state, mdp_ltlf.initial_state)
    queue.append(initial_state)
    to_be_visited.add(initial_state)

    while len(queue) > 0:
        cur_state = queue.popleft()
        to_be_visited.remove(cur_state)
        visited.add(cur_state)
        cur_system_state, cur_dfa_state = cur_state
        trans_dist = {}

        prop_formula_from_dfa_state = mdp_ltlf.transitions[cur_dfa_state].items()
        for prop_formula, dest_state_prob in prop_formula_from_dfa_state:
            assert len(dest_state_prob) == 1
            next_dfa_state, prob = list(dest_state_prob.items())[0]
            goal_reward = weights[0] * mdp_ltlf.rewards[cur_dfa_state][prop_formula]
            if next_dfa_state == mdp_ltlf.failure_state:
                continue
            symbols = guard_to_symbol(prop_formula)
            for symbol in symbols:
                next_system_state_trans = system_transition_function_by_symbol[
                    cur_system_state
                ].get(symbol, None)
                if next_system_state_trans is None:
                    continue
                for service_id, (
                    next_system_state_dist,
                    next_system_reward,
                ) in next_system_state_trans.items():
                    weighted_next_system_reward = (
                        weights[service_id + 1] * next_system_reward
                    )
                    final_reward = goal_reward + weighted_next_system_reward
                    for next_system_state, prob in next_system_state_dist.items():
                        assert prob > 0.0
                        next_state = (next_system_state, next_dfa_state)
                        trans_dist.setdefault((symbol, service_id), ({}, final_reward))[
                            0
                        ][next_state] = prob
                        if (
                            next_state not in visited
                            and next_state not in to_be_visited
                        ):
                            queue.append(next_state)
                            to_be_visited.add(next_state)

        transition_function[cur_state] = trans_dist

    return MdpDfa(transition_function, mdp_ltlf.gamma)
