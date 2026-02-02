from pathlib import Path

from device import Device

class Simulation:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.devices = dict()
        self.time = 0
        self.length = 1

    def check_file_exists(self) -> None:
        if not self.file_path.exists():
            print('FILE NOT FOUND')
            raise SystemExit

    def read_file(self) -> None:
        with open(self.file_path) as f:
            line = f.readline()
            while line != '' and self.time < self.length:
                instruction = line[0:1]

                if instruction == 'L':
                    self.set_simulation_length(line)
                elif instruction == 'D':
                    self.add_device(line)
                elif instruction == 'P':
                    self.propagate_device(line)

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
        self.devices[sender].recipients.append((recipient, delay))