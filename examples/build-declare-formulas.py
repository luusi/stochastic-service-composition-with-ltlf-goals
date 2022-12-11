#!/usr/bin/env python3
import shutil
from pathlib import Path
from typing import cast, Set

from logaut import ltl2dfa
from pylogics.parsers import parse_ltl
from pythomata.impl.symbolic import SymbolicDFA

from stochastic_service_composition.declare_utils import absence_2, build_declare_assumption, exactly_once, \
    alt_response, alt_precedence, alt_succession, not_coexistence
from stochastic_service_composition.dfa_target import MdpDfa, mdp_from_dfa, from_symbolic_automaton_to_declare_automaton
from stochastic_service_composition.rendering import mdp_to_graphviz


def print_automaton_of_formula(formula_str: str, all_symbols: Set[str], name: str, output_dir: Path):
    assumption = " & " + build_declare_assumption(all_symbols) if len(all_symbols) > 1 else ""
    formula = parse_ltl(formula_str + assumption)
    automaton = ltl2dfa(formula, backend="lydia")
    simple_automaton = from_symbolic_automaton_to_declare_automaton(cast(SymbolicDFA, automaton), all_symbols)
    mdp: MdpDfa = mdp_from_dfa(simple_automaton)
    mdp_to_graphviz(mdp).render(output_dir / f"{name}-mdp")
    digraph = cast(SymbolicDFA, automaton).to_graphviz()
    digraph.body.append("labelloc=top;")
    digraph.body.append(f'label="{name}";')
    digraph.render(output_dir / f"{name}-automaton")
    (output_dir / f"{name}-formula.ltlf").write_text(formula_str)


if __name__ == '__main__':
    # setup
    output_dir = Path("declare-formulas")
    shutil.rmtree(str(output_dir), ignore_errors=True)
    output_dir.mkdir(exist_ok=False)

    a, b, c = "a", "b", "c"
    symbols = {a, b}

    # print simple DECLARE operators
    print_automaton_of_formula(absence_2(a), {a, b, c}, "01-absence-2", output_dir)
    print_automaton_of_formula(exactly_once(a), {a}, "02-exactly-1", output_dir)
    print_automaton_of_formula(alt_response(a, b), {a, b}, "03-alt-response", output_dir)
    print_automaton_of_formula(alt_precedence(a, b), {a, b}, "04-alt-precedence", output_dir)
    print_automaton_of_formula(alt_succession(a, b), {a, b}, "05-alt-succession", output_dir)
    print_automaton_of_formula(not_coexistence(a, b), {a, b}, "06-not-coexistence", output_dir)

    print_automaton_of_formula(alt_succession(alt_succession(a, b), c), {a, b, c}, "07-alt-succession-a-b-c", output_dir)
