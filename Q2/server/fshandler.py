import json
from pathlib import Path


class FSHandler():
    def __init__(self, path):
        self.user = Path(path).parts[0]
        self.path = Path(self.user)
        self.files = json.load(self.path.open())

    def create_folder(self, path):
        path = Path(path)
        if path.is_dir() and not path.exists():
            path.mkdir(parents=True)
            # for part in path.parts:

            return True
        return False

    def login(self, user):
        init = json.dumps({".": []}, indent=4, separators=(',', ': '))
        with open(user, "w+") as files:
            files.write(init)
