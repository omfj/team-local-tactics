from dataclasses import dataclass
from enum import Enum
from random import random, shuffle

_BEATS = {
    (1, 3),
    (3, 2),
    (2, 1)
}


class Shape(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    def __gt__(self, other):
        return (self.value, other.value) in _BEATS


@dataclass
class PairThrow:
    red: Shape
    blue: Shape


class Champion:

    def __init__(self, name, rock = 1, paper= 1, scissors = 1):
        self._name = name
        total = rock + paper + scissors
        self._rock = rock / total
        self._paper = paper / total

    @property
    def name(self) -> str:
        return self._name

    def throw(self) -> Shape:
        r = random()
        if r < self._rock:
            return Shape.ROCK
        if r < self._paper+self._rock:
            return Shape.PAPER
        return Shape.SCISSORS

    @property
    def str_tuple(self):
        return (self.name,
                f'{self._rock:.2f}',
                f'{self._paper:.2f}',
                f'{(1-self._rock-self._paper):.2f}')

    def __repr__(self) -> str:
        return (f'{self._name:10}|   {self._rock:.2f}   |   '
                f'{self._paper:.2f}   |   {(1-self._rock-self._paper):.2f}')


def pair_throw(red_champ, blue_champ,  max_iter = 100):

    for _ in range(max_iter):
        red_throw = red_champ.throw()
        blue_throw = blue_champ.throw()
        if red_throw != blue_throw:
            break
    return PairThrow(red_throw, blue_throw)


@dataclass
class Team:
    champions: list[Champion]

    def __iter__(self):
        shuffle(self.champions)
        return iter(self.champions)


@dataclass
class Match:
    red_team: Team
    blue_team: Team
    n_rounds: int = 3

    def play(self):
        """
        Play a match.
        """
        self._red_score = 0
        self._blue_score = 0
        self._rounds = [{} for _ in range(self.n_rounds)]
        for round in self._rounds:
            for red_champ, blue_champ in zip(self.red_team, self.blue_team):
                champ_names = red_champ.name + ', ' + blue_champ.name
                pair = pair_throw(red_champ, blue_champ)
                if pair.red > pair.blue:
                    self._red_score += 1
                elif pair.red < pair.blue:
                    self._blue_score += 1
                round[champ_names] = pair

    @property
    def score(self) -> tuple[int, int]:
        return (self._red_score, self._blue_score)

    @property
    def rounds(self) -> list[dict[str, PairThrow]]:
        return self._rounds
