from pathlib import Path
from collections import defaultdict

from device import Device

class Simulation:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.devices = dict()
        self.alert_queue = defaultdict(list)
        self.length = None

    def check_file_exists(self) -> None:
        if not self.file_path.exists():
            print('FILE NOT FOUND')
            raise SystemExit

    def read_file(self) -> None:
        with open(self.file_path) as f:
            line = f.readline()
            while line != '':
                instruction = line[0:1]

                if instruction == 'L':
                    self.set_simulation_length(line)
                elif instruction == 'D':
                    self.add_device(line)
                elif instruction == 'P':
                    self.propagate_device(line)
                elif instruction == 'A':
                    self.add_to_queue(line, 'A')
                elif instruction == 'C':
                    self.add_to_queue(line, 'C')

                line = f.readline()

    def set_simulation_length(self, line: str) -> None:
        simulation_length = line.split()[1]
        self.length = int(simulation_length)

    def add_device(self, line: str) -> None:
        device_id = line.split()[1]
        device = Device(int(device_id))
        self.devices[device_id] = device

    def propagate_device(self, line: str) -> None:
        line = line.split()
        sender = line[1]
        recipient = int(line[2])
        delay = int(line[3])
        self.devices[sender].recipient_list.append((recipient, delay))

    def add_to_queue(self, line: str, event_type: str) -> None:
        line = line.split()
        sender = line[1]
        recipients = self.devices[sender].recipient_list[:]
        message = line[2]
        simulation_time = line[3]
        self.alert_queue[simulation_time].append((event_type, sender, recipients, message))

    def run_simulation(self) -> None:
        for timestamp in sorted(self.alert_queue.keys()):
            if int(timestamp) < self.length:
                for event_type, sender, recipients, message in self.alert_queue[timestamp]:
                    if event_type == 'A':
                        self.devices[sender].send(recipients, message, timestamp, self.alert_queue, self.devices)
                    elif event_type == 'C':
                        self.devices[sender].cancel(recipients, message, timestamp, self.alert_queue)
                    elif event_type == 'RA':
                        self.devices[sender].receive_alert(recipients, message, timestamp)
                    elif event_type == 'RC':
                        self.devices[sender].receive_cancellation(recipients, message, timestamp, self.devices)
        print(f'@{self.length}: END')