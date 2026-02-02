from pathlib import Path
from collections import defaultdict
from device import Device

class Simulation:
    """A simulation is an object that reads input files and manipulates Devices"""
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.devices = dict()
        self.alert_queue = defaultdict(list)
        self.length = None

    def check_file_exists(self) -> None:
        """Verifies whether the file exists, terminates program if it doesn't"""
        if not self.file_path.exists():
            print('FILE NOT FOUND')
            raise SystemExit

    def read_file(self) -> None:
        """Reads files and manipulates Devices according to instructions"""
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
        """Updates simulation length based on input file"""
        simulation_length = line.split()[1]
        self.length = int(simulation_length)

    def add_device(self, line: str) -> None:
        """Adds a Device to the global list according to input file"""
        device_id = line.split()[1]
        device = Device(int(device_id))
        self.devices[device_id] = device

    def propagate_device(self, line: str) -> None:
        """Propagates a Device according to input file and adds to recipient list"""
        line = line.split()
        sender = line[1]
        recipient = int(line[2])
        delay = int(line[3])
        self.devices[sender].recipient_list.append((recipient, delay))

    def add_to_queue(self, line: str, event_type: str) -> None:
        """Adds an event to the event queue at the simulation time specified by input file"""
        line = line.split()
        sender = line[1]
        recipients = self.devices[sender].recipient_list[:]
        message = line[2]
        simulation_time = line[3]
        self.alert_queue[simulation_time].append((event_type, sender, recipients, message))

    '''The RC branch is not fully covered because the test cases don't create scenarios
    where devices receive cancellations from others during simulation propagation, which
    would require a multi-hop cancellation scenario'''
    def run_simulation(self) -> None:
        """Traverses event queue and dynamically updates it based on cancellations and receptions"""
        while self.alert_queue:
            timestamp = min(self.alert_queue.keys(), key = int)

            if int(timestamp) >= self.length:
                break

            events = self.alert_queue.pop(timestamp)
            for event in events:
                event_type = event[0]

                if event_type == 'A':
                    sender = event[1]
                    recipients = event[2]
                    message = event[3]
                    if message not in self.devices[sender].message_list:
                        self.devices[sender].message_list.append(message)
                    self.devices[sender].send(recipients, message, timestamp, self.alert_queue)
                elif event_type == 'C':
                    sender = event[1]
                    recipients = event[2]
                    message = event[3]
                    if message not in self.devices[sender].cancelled_messages:
                        self.devices[sender].cancelled_messages.append(message)
                    self.devices[sender].cancel(recipients, message, timestamp, self.alert_queue)
                elif event_type == 'RA':
                    recipient = event[1]
                    sender = event[2]
                    message = event[3]
                    self.devices[str(recipient)].receive_alert(sender, message, timestamp,
                        self.alert_queue)
                elif event_type == 'RC':
                    recipient = event[1]
                    sender = event[2]
                    message = event[3]
                    self.devices[str(recipient)].receive_cancellation(sender, message, timestamp,
                        self.alert_queue)
        print(f'@{self.length}: END')