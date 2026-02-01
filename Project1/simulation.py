from pathlib import Path

class Simulation:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def check_file_exists(self):
        if not self.file_path.exists():
            print('FILE NOT FOUND')
            raise SystemExit