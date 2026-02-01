import unittest
from pathlib import Path

from simulation import Simulation

class Project1Test(unittest.TestCase):
    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            sim = Simulation(Path('samples/asdf.txt'))
            sim.check_file_exists()


if __name__ == '__main__':
    unittest.main()