from collections import deque
from typing import Deque, Dict, List, Tuple

import numpy as np

from stochastic_service_composition.dfa_target import MdpDfa, guard_to_symbol
from stochastic_service_composition.services import Service, build_system_service
from stochastic_service_composition.types import Action, MDPDynamics, State, MOMDPDynamics


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

        next_system_state_trans = system_service.transition_function[
            cur_system_state
        ].items()

        # iterate over all available actions of system service
        # in case symbol is in DFA available actions, progress DFA state component
        for (symbol, service_id), next_state_info in next_system_state_trans:
            next_system_state_distr, reward_vector = next_state_info
            system_reward = sum(weights[i + 1] * r for i, r in enumerate(reward_vector))

            if symbol not in mdp_ltlf.all_actions:
                # it is a tau action
                next_dfa_state = cur_dfa_state
                goal_reward = 0.0
            else:
                symbol_to_next_dfa_states = mdp_ltlf.transitions[cur_dfa_state]
                next_dfa_state_distr = symbol_to_next_dfa_states[symbol]
                next_dfa_state, _prob = list(next_dfa_state_distr.items())[0]
                goal_reward = weights[0] * mdp_ltlf.rewards[cur_dfa_state][symbol]
            final_reward = goal_reward + system_reward

            for next_system_state, prob in next_system_state_distr.items():
                assert prob > 0.0
                next_state = (next_system_state, next_dfa_state)
                trans_dist.setdefault((symbol, service_id), ({}, final_reward))[0][
                    next_state
                ] = prob
                if next_state not in visited and next_state not in to_be_visited:
                    queue.append(next_state)
                    to_be_visited.add(next_state)

        transition_function[cur_state] = trans_dist

    return MdpDfa(transition_function, mdp_ltlf.gamma)
