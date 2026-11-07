"""Small input helpers shared by the optimization experiments."""

import csv
import os


def initial_guess_from_env(expected_size):
    """Read a flattened solution from MPC_INITIAL_GUESS_CSV when provided."""
    path = os.environ.get('MPC_INITIAL_GUESS_CSV')
    if not path:
        return None
    with open(path, newline='') as source:
        values = [float(value) for row in csv.reader(source) for value in row]
    if len(values) != expected_size:
        raise ValueError('initial guess has {} values; expected {}'.format(len(values), expected_size))
    return values
