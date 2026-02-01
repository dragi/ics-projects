import unittest
from pathlib import Path

from simulation import Simulation
from device import Device

class Project1Test(unittest.TestCase):
    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            sim = Simulation(Path('samples/asdf.txt'))
            sim.check_file_exists()

    def test_devices_are_added_from_file(self):
        sim = Simulation(Path('samples/sample_input.txt'))
        sim.read_file()
        self.assertEqual(sim.devices['1'].device_id, 1)
        self.assertEqual(sim.devices['2'].device_id, 2)
        self.assertEqual(sim.devices['3'].device_id, 3)
        self.assertEqual(sim.devices['4'].device_id, 4)

if __name__ == '__main__':
    unittest.main()