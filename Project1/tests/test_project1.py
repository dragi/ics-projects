import unittest
from pathlib import Path
from collections import defaultdict
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

    def test_simulation_length(self):
        sim = Simulation(Path('samples/sample_input.txt'))
        sim.read_file()
        self.assertEqual(sim.length, 9999)

    def test_devices_propagate(self):
        sim = Simulation(Path('samples/sample_input.txt'))
        sim.read_file()
        self.assertEqual(sim.devices['1'].recipient_list, [(2, 750)])
        self.assertEqual(sim.devices['2'].recipient_list, [(3, 1250)])
        self.assertEqual(sim.devices['3'].recipient_list, [(4, 500)])
        self.assertEqual(sim.devices['4'].recipient_list, [(1, 1000)])

    def test_alerts_can_be_created(self):
        sim = Simulation(Path('samples/sample_input.txt'))
        sim.read_file()
        self.assertEqual(sim.alert_queue, {'0': [('A', '1', [(2, 750)], 'Trouble')],
             '2200': [('C', '1', [(2, 750)], 'Trouble')]})

    def test_alerts_can_be_sent(self):
        test_queue = defaultdict(list)
        device = Device(1)
        device.send([(2, 300)], 'Test', 0, test_queue)
        self.assertEqual(test_queue, {'300': [('RA', 2, 1, 'Test')]})

    def test_device_initialization(self):
        device = Device(5)
        self.assertEqual(device.device_id, 5)
        self.assertEqual(device.recipient_list, [])
        self.assertEqual(device.message_list, [])
        self.assertEqual(device.cancelled_messages, [])

    def test_multiple_recipients_propagation(self):
        test_queue = defaultdict(list)
        device = Device(1)
        device.send([(2, 100), (3, 200), (4, 300)], 'Test', 0, test_queue)
        self.assertEqual(len(test_queue), 3)
        self.assertIn(('RA', 2, 1, 'Test'), test_queue['100'])
        self.assertIn(('RA', 3, 1, 'Test'), test_queue['200'])
        self.assertIn(('RA', 4, 1, 'Test'), test_queue['300'])

    def test_receive_alert_adds_to_message_list(self):
        test_queue = defaultdict(list)
        device = Device(2)
        device.recipient_list = [(3, 100)]

        device.receive_alert(1, 'Test', 100, test_queue)
        self.assertIn('Test', device.message_list)

if __name__ == '__main__':
    unittest.main()