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

    def test_file_exists(self):
        sim = Simulation(Path('samples/sample_input.txt'))
        sim.check_file_exists()
        self.assertTrue(True)

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
        self.assertEqual(device.message_list, set())
        self.assertEqual(device.cancelled_messages, {})

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

    def test_receive_alert_prevents_duplicate_forwarding(self):
        test_queue = defaultdict(list)
        test_devices = {}
        device = Device(2)
        device.recipient_list = [(3, 100)]
        device.message_list = ['Test']
        test_devices['2'] = device

        device.receive_alert(1, 'Test', 100, test_queue)
        self.assertEqual(len(test_queue), 1)

    def test_receive_alert_does_not_forward_if_cancelled(self):
        test_queue = defaultdict(list)
        device = Device(2)
        device.recipient_list = [(3, 100)]
        device.cancelled_messages = {'Test': 50}

        device.receive_alert(1, 'Test', 100, test_queue)

        self.assertIn('Test', device.message_list)
        self.assertEqual(len(test_queue), 0)

    def test_cancellation_sending(self):
        test_queue = defaultdict(list)
        device = Device(1)
        device.cancel([(2, 500)], 'Test', 1000, test_queue)
        self.assertEqual(test_queue, {'1500': [('RC', 2, 1, 'Test')]})

    def test_receive_cancellation_forwards_once(self):
        test_queue = defaultdict(list)
        test_devices = {}
        device = Device(2)
        device.recipient_list = [(3, 100)]
        device.message_list = ['Test']
        test_devices['2'] = device

        device.receive_cancellation(1, 'Test', 1000, test_queue)
        self.assertIn('Test', device.cancelled_messages)
        self.assertEqual(len(test_queue['1100']), 1)

        test_queue.clear()
        device.receive_cancellation(3, 'Test', 1200, test_queue)
        self.assertEqual(len(test_queue), 0)

    def test_receive_cancellation_without_alert(self):
        test_queue = defaultdict(list)
        device = Device(2)
        device.recipient_list = [(3, 100)]

        device.receive_cancellation(1, 'Test', 1000, test_queue)

        self.assertIn('Test', device.cancelled_messages)
        self.assertEqual(device.cancelled_messages['Test'], 1000)
        self.assertEqual(len(test_queue), 0)

    def test_run_simulation_stops_at_length(self):
        sim = Simulation(Path('asdf'))
        sim.length = 50
        sim.devices['1'] = Device(1)
        sim.alert_queue['10'] = [('A', '1', [], 'Early')]
        sim.alert_queue['100'] = [('A', '1', [], 'Late')]
        sim.run_simulation()
        self.assertIn('Early', sim.devices['1'].message_list)
        self.assertNotIn('Late', sim.devices['1'].message_list)

    def test_run_simulation_handles_ra_events(self):
        sim = Simulation(Path('asdf'))
        sim.length = 100
        sim.devices['2'] = Device(2)
        sim.alert_queue['10'] = [('RA', 2, 1, 'Alert')]
        sim.run_simulation()
        self.assertIn('Alert', sim.devices['2'].message_list)

    def test_run_simulation_handles_rc_events(self):
        sim = Simulation(Path('asdf'))
        sim.length = 100
        sim.devices['2'] = Device(2)
        sim.devices['2'].message_list = ['Cancel']
        sim.alert_queue['10'] = [('RC', 2, 1, 'Cancel')]
        sim.run_simulation()
        self.assertIn('Cancel', sim.devices['2'].cancelled_messages)

    def test_duplicate_messages_prevented(self):
        sim = Simulation(Path('asdf'))
        sim.length = 100
        sim.devices[1] = Device(1)
        sim.alert_queue['5'] = [('A', 1, [], 'Msg'), ('A', 1, [], 'Msg')]
        sim.alert_queue['10'] = [('C', 1, [], 'Msg'), ('C', 1, [], 'Msg')]
        sim.run_simulation()
        self.assertIn('Msg', sim.devices[1].message_list)
        self.assertIn('Msg', sim.devices[1].cancelled_messages)

if __name__ == '__main__':
    unittest.main()