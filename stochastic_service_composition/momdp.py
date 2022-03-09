from collections import deque
from typing import List, Set, Deque

from mdp_dp_rl.processes.mdp import MDP

from stochastic_service_composition.composition import COMPOSITION_MDP_INITIAL_STATE, COMPOSITION_MDP_INITIAL_ACTION, \
    COMPOSITION_MDP_UNDEFINED_ACTION
from stochastic_service_composition.services import Service, build_system_service
from stochastic_service_composition.types import MDPDynamics, Action


def compute_final_mdp(
    mdp_ltlf: MDP,
    services: List[Service],
    weights: List[float]
) -> MDP:
    assert len(weights) == len(services) + 1

    system_service = build_system_service(*services)

    initial_state = COMPOSITION_MDP_INITIAL_STATE
    # one action per service (1..n) + the initial action (0)
    actions: Set[Action] = set(range(len(services)))
    initial_action = COMPOSITION_MDP_INITIAL_ACTION
    actions.add(initial_action)

    # add an 'undefined' action for sink states
    actions.add(COMPOSITION_MDP_UNDEFINED_ACTION)

    transition_function: MDPDynamics = {}

    visited = set()
    to_be_visited = set()
    queue: Deque = deque()

    # add initial transitions
    transition_function[initial_state] = {}
    initial_transition_dist = {}
    # TODO: fix mdp.initial_state
    # TODO: actions should be symbols, not PL formula!
    prop_formula_from_initial_state = mdp_ltlf.transitions[mdp_ltlf.initial_state].keys()
    # for prop_formula in prop_formula_from_initial_state:
    #     next_state = (system_service.initial_state, mdp_ltlf.initial_state, symbol)
    #     next_prob = target.policy[target.initial_state][symbol]
    #     initial_transition_dist[next_state] = next_prob
    #     queue.append(next_state)
    #     to_be_visited.add(next_state)
    transition_function[initial_state][initial_action] = (initial_transition_dist, 0.0)  # type: ignore

    return MDP(transition_function, mdp_ltlf.gamma)




