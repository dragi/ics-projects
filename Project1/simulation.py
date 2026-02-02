from pathlib import Path

from device import Device

class Simulation:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.devices = dict()
        self.time = 0
        self.length = 1

    def check_file_exists(self):
        if not self.file_path.exists():
            print('FILE NOT FOUND')
            raise SystemExit

    def read_file(self):
        with open(self.file_path) as f:
            line = f.readline()
            while line != '' and self.time < self.length:
                instruction = line[0:1]

                if instruction == 'L':
                    simulation_length = line.split()[1]
                    self.length = int(simulation_length)
                elif instruction == 'D':
                    device_id = line.split()[1]
                    device = Device(int(device_id))
                    self.devices[device_id] = device
                elif instruction == 'P':
                    line = line.split()
                    sender = line[1]
                    recipient = int(line[2])
                    delay = int(line[3])
                    self.devices[sender].recipients.append((recipient, delay))

                line = f.readline()