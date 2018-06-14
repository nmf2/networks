import json
from pathlib import Path


class FSHandler():
    def __init__(self, path):
        self.user = Path(path).name
        self.path = Path(path)
        with open(str(self.path) + '/' + self.user + '.json') as file:
            self.files = json.load(file)

    def create_folder(self, path):
        print("ok")
        path = Path(path)
        print("ok")
        if not path.exists():
            print("ok")
            path.mkdir(parents=True)
            return True
        return False

    def login(self, user):
        init = json.dumps({".": []}, indent=4, separators=(',', ': '))
        with open(user, "w+") as files:
            files.write(init)