from collections import deque
from typing import Deque, List

from stochastic_service_composition.dfa_target import MdpDfa
from stochastic_service_composition.services import Service, build_system_service
from stochastic_service_composition.types import MDPDynamics


def compute_final_mdp(
    mdp_ltlf: MdpDfa, services: List[Service], weights: List[float], with_all_initial_states: bool = False
) -> MdpDfa:
    assert all(service.nb_rewards for service in services)
    assert len(weights) == services[0].nb_rewards + 1

    system_service = build_system_service(*services)

    transition_function: MDPDynamics = {}

    visited = set()
    to_be_visited = set()
    queue: Deque = deque()

    # add initial transitions
    initial_state = (system_service.initial_state, mdp_ltlf.initial_state)
    queue.append(initial_state)
    to_be_visited.add(initial_state)
    if with_all_initial_states:
        for system_service_state in system_service.states:
            if system_service_state == system_service.initial_state: continue
            new_initial_state = (system_service_state, mdp_ltlf.initial_state)
            queue.append(new_initial_state)
            to_be_visited.add(new_initial_state)

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
            # not a tau action -> check we can
            elif symbol not in mdp_ltlf.transitions[cur_dfa_state]:
                # target does not have such transition -> failure
                next_dfa_state = mdp_ltlf.failure_state
                goal_reward = 0
            else:
                symbol_to_next_dfa_states = mdp_ltlf.transitions[cur_dfa_state]
                next_dfa_state_distr = symbol_to_next_dfa_states[symbol]
                assert len(next_dfa_state_distr) == 1
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

    result = MdpDfa(transition_function, mdp_ltlf.gamma)
    result.initial_state = initial_state
    return result
