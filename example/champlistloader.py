from core import Champion

# Added os for testing
import os
cwd = os.getcwd()

def _parse_champ(champ_text):
    name, rock, paper, scissors = champ_text.split(sep=',')
    return Champion(name, float(rock), float(paper), float(scissors))


def from_csv(filename)
    champions = {}
    with open(filename, 'r') as f:
        for line in f.readlines():
            champ = _parse_champ(line)
            champions[champ.name] = champ
    return champions


def load_some_champs():
    return from_csv(cwd + '/some_champs.txt')
