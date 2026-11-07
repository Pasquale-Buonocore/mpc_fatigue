"""Check the optional CSV warm start used by Box optimizers."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from solver_io import initial_guess_from_env


class SolverIoTest(unittest.TestCase):
    def test_reads_expected_vector_and_rejects_wrong_size(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'solution.csv'
            path.write_text('1.0,2.0\n3.0\n')
            with patch.dict(os.environ, {'MPC_INITIAL_GUESS_CSV': str(path)}):
                self.assertEqual(initial_guess_from_env(3), [1.0, 2.0, 3.0])
                with self.assertRaisesRegex(ValueError, 'expected 2'):
                    initial_guess_from_env(2)


if __name__ == '__main__':
    unittest.main()
