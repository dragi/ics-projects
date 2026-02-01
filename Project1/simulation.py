from pathlib import Path

from device import Device

class Simulation:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.devices = dict()
        self.length = None

    def check_file_exists(self):
        if not self.file_path.exists():
            print('FILE NOT FOUND')
            raise SystemExit

    def read_file(self):
        with open(self.file_path) as f:
            line = f.readline()
            while line:
                instruction = line[0:1]

                if instruction == 'D':
                    device_id = line.split()[1]
                    device = Device(int(device_id))
                    self.devices[device_id] = device
                elif instruction == 'L':
                    simulation_length = line.split()[1]
                    self.length = int(simulation_length)

                line = f.readline()