from pathlib import Path

from device import Device

class Simulation:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.devices = dict()

    def check_file_exists(self):
        if not self.file_path.exists():
            print('FILE NOT FOUND')
            raise SystemExit

    def read_file(self):
        with open(self.file_path) as f:
            line = f.readline()
            while line:
                if line[0:1] == 'D':
                    device_id = line.split()[1]
                    device = Device(int(device_id))
                    self.devices[device_id] = device

                line = f.readline()