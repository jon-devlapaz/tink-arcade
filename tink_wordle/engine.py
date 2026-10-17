"""Deterministic Wordle rules, independent of curses and audio."""
from pathlib import Path
import random

WORD_LENGTH = 5
MAX_GUESSES = 6
WORDS = (
    "arise", "audio", "baker", "badge", "beach", "blaze", "brave", "brick", "brush", "cabin",
    "candy", "cargo", "charm", "chase", "chess", "chief", "civic", "clean", "clear", "climb",
    "clock", "cloud", "coast", "crane", "crisp", "crown", "dance", "delta", "dream", "eagle",
    "early", "earth", "eerie", "epoch", "event", "faith", "fancy", "field", "flame", "flock", "flute",
    "frame", "frost", "giant", "glade", "globe", "grace", "grain", "grand", "grape", "graph",
    "heart", "honey", "horse", "house", "human", "ivory", "jelly", "jolly", "judge", "latch",
    "lemon", "light", "maple", "match", "metal", "model", "money", "month", "mouse", "music",
    "night", "ocean", "olive", "orbit", "paper", "pearl", "piano", "pilot", "plane", "plant",
    "pride", "prize", "quiet", "radio", "raise", "raven", "reach", "river", "robot", "round",
    "scale", "scene", "scope", "shine", "shore", "sketch", "skill", " slate".strip(), "smile", "sound",
    "spark", "spice", "spoke", "sport", "stage", "stare", "steam", "stone", "story", "straw",
    "sugar", "sweep", "table", "teach", "theme", "thunder", "tiger", "toast", "today", "torch",
    "touch", "tower", "trace", "track", "trade", "train", "treat", "trust", "ultra", "union",
    "vivid", "voice", "watch", "water", "whale", "wheel", "world", "write", "young", "zebra",
)
WORDS = tuple(word for word in WORDS if len(word) == WORD_LENGTH)
_GUESS_WORDS_PATH = Path(__file__).with_name("guess_words.txt")
GUESS_WORDS = frozenset(
    word.strip() for word in _GUESS_WORDS_PATH.read_text().splitlines()
    if len(word.strip()) == WORD_LENGTH and word.strip().isalpha()
)
VALID_WORDS = frozenset(WORDS) | GUESS_WORDS


class Game:
    def __init__(self, answer=None, seed=None):
        self.seed = seed
        self._answer = answer.lower() if answer else None
        if self._answer is not None and (len(self._answer) != WORD_LENGTH or not self._answer.isalpha()):
            raise ValueError("answer must be a five-letter word")
        self.restart()

    def restart(self):
        rng = random.Random(self.seed)
        self.answer = self._answer or rng.choice(WORDS)
        self.guesses = []
        self.results = []
        self.current = ""
        self.status = "playing"
        self.message = ""

    @property
    def remaining(self):
        return MAX_GUESSES - len(self.guesses)

    @property
    def letter_states(self):
        """Best-known feedback for every letter used in submitted guesses."""
        priority = {"absent": 0, "present": 1, "correct": 2}
        states = {}
        for guess, result in zip(self.guesses, self.results):
            for letter, state in zip(guess, result):
                if priority[state] > priority.get(states.get(letter, "absent"), -1):
                    states[letter] = state
        return states

    def add_letter(self, letter):
        if self.status != "playing" or len(self.current) >= WORD_LENGTH:
            return False
        if len(letter) != 1 or not letter.isalpha():
            return False
        self.current += letter.lower()
        self.message = ""
        return True

    def remove_letter(self):
        if self.status != "playing" or not self.current:
            return False
        self.current = self.current[:-1]
        self.message = ""
        return True

    def submit(self):
        if self.status != "playing":
            return None
        if len(self.current) != WORD_LENGTH:
            self.message = "Need five letters."
            return None
        if self.current not in VALID_WORDS:
            self.message = "Not a recognized word."
            return None
        guess = self.current
        counts = {}
        for letter in self.answer:
            counts[letter] = counts.get(letter, 0) + 1
        result = ["absent"] * WORD_LENGTH
        for index, letter in enumerate(guess):
            if letter == self.answer[index]:
                result[index] = "correct"
                counts[letter] -= 1
        for index, letter in enumerate(guess):
            if result[index] == "absent" and counts.get(letter, 0):
                result[index] = "present"
                counts[letter] -= 1
        self.guesses.append(guess)
        self.results.append(tuple(result))
        self.current = ""
        if guess == self.answer:
            self.status = "won"
            self.message = "You found it."
        elif len(self.guesses) == MAX_GUESSES:
            self.status = "lost"
            self.message = f"The word was {self.answer.upper()}."
        else:
            self.message = ""
        return tuple(result)
