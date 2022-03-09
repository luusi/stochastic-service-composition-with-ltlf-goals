from stochastic_service_composition.dfa_target import mdp_from_ltlf

from pylogics.parsers import parse_ltl

if __name__ == '__main__':
    formula = parse_ltl("F(a)")
    mdp_from_ltlf(formula)
