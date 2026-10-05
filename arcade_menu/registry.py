"""Game registry. Add a cabinet by appending an entry to games.json."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = Path(__file__).with_name("games.json")


@dataclass(frozen=True)
class Game:
    title: str
    tagline: str
    about: str
    controls: tuple
    cwd: Path
    module: str
    args: tuple = field(default=())
    requires_env: str = ""
    note: str = ""

    @property
    def installed(self):
        return (self.cwd / self.module / "__main__.py").is_file()

    @property
    def missing_env(self):
        return bool(self.requires_env) and not os.environ.get(self.requires_env)

    @property
    def available(self):
        return self.installed and not self.missing_env

    @property
    def status(self):
        if not self.installed:
            return "NOT INSTALLED"
        if self.missing_env:
            return f"NEEDS {self.requires_env}"
        return "READY"

    def command(self, python, no_color=False):
        extra = list(self.args) + (["--no-color"] if no_color else [])
        return [python, "-m", self.module, *extra]


def load_games(path=REGISTRY):
    games = []
    for entry in json.loads(Path(path).read_text()):
        games.append(Game(
            title=entry["title"],
            tagline=entry.get("tagline", ""),
            about=entry.get("about", ""),
            controls=tuple(entry.get("controls", ())),
            cwd=(ROOT / entry["path"]).resolve(),
            module=entry["module"],
            args=tuple(entry.get("args", ())),
            requires_env=entry.get("requires_env", ""),
            note=entry.get("note", ""),
        ))
    return games
