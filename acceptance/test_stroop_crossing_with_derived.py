import pytest
import operator as op

from itertools import permutations

from sweetpea.primitives import Factor, DerivedLevel, WithinTrial, Transition
from sweetpea.constraints import AtMostKInARow
from sweetpea.encoding_diagram import print_encoding_diagram
from sweetpea import fully_cross_block, synthesize_trials_non_uniform, print_experiments


direction = Factor("direction", ["up", "down"])

color_list = ["red", "blue"]
color = Factor("color", color_list)
text  = Factor("text",  color_list)

congruent_factor = Factor("congruent?", [
    DerivedLevel("con", WithinTrial(op.eq, [color, text])),
    DerivedLevel("inc", WithinTrial(op.ne, [color, text]))
])

repeated_color_factor = Factor("repeated color?", [
    DerivedLevel("yes", Transition(lambda colors: colors[0] == colors[1], [color])),
    DerivedLevel("no",  Transition(lambda colors: colors[0] != colors[1], [color]))
])


@pytest.mark.parametrize('design', [[direction, color, text, congruent_factor],
                                    [congruent_factor, direction, color, text],
                                    [direction, congruent_factor, color, text]])
def test_correct_solution_count_when_unconstrained(design):
    crossing = [direction, congruent_factor]
    constraints = []

    block  = fully_cross_block(design, crossing, constraints)
    experiments  = synthesize_trials_non_uniform(block, 500)

    assert len(experiments) == 384


@pytest.mark.parametrize('design', permutations([direction, color, text, congruent_factor]))
def test_correct_solution_count_when_constrained(design):
    crossing = [direction, congruent_factor]
    constraints = [AtMostKInARow(1, congruent_factor)]

    block  = fully_cross_block(design, crossing, constraints)
    experiments  = synthesize_trials_non_uniform(block, 500)

    assert len(experiments) == 128


@pytest.mark.parametrize('design', permutations([direction, color, repeated_color_factor]))
def test_correct_solution_count_when_transition_in_crossing_and_unconstrained(design):
    crossing = [direction, repeated_color_factor]
    constraints = []

    block  = fully_cross_block(design, crossing, constraints)
    experiments  = synthesize_trials_non_uniform(block, 100)

    assert len(experiments) == 96


@pytest.mark.parametrize('design', permutations([direction, color, repeated_color_factor]))
def test_correct_solution_count_when_transition_in_crossing_and_constrained(design):
    crossing = [direction, repeated_color_factor]
    constraints = [AtMostKInARow(1, ("color", "red"))]

    block  = fully_cross_block(design, crossing, constraints)
    experiments  = synthesize_trials_non_uniform(block, 100)

    assert len(experiments) == 32


@pytest.mark.parametrize('design', permutations([color, repeated_color_factor]))
def test_correct_solution_count_when_crossing_with_derived_transition(design):
    crossing = [color, repeated_color_factor]
    constraints = []

    block  = fully_cross_block(design, crossing, constraints)
    experiments  = synthesize_trials_non_uniform(block, 100)

    assert len(experiments) == 4
