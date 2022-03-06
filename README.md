# Team Local Tactics
## What?

A game made for the mandatory assignment in INF142 (Computer Networks) @ University of Bergen.

Rock, paper, scissors with a twist! Choose between the different champions and crush your friends with even more [RNG](https://www.freecodecamp.org/news/rng-meaning-what-does-rng-stand-for-in-gaming/)!

## Installation

### Dependencies
The program is written in [Python 3.10.x](https://www.python.org/downloads/release/python-3102/). For running the game locally on your own computer download the following dependencies with `pip`:
```
rich
pyaml
```

### Download the files
1. Clone the files to your computer.
```bash
git clone https://github.com/omfj/team-local-tactics.git
```

2. Change directory to `team-local-tactics`.
```bash
cd team-local-tactics
```

### Docker

1. Builds all the docker files 
```bash
docker-compose build
```

2. Starts the database and server
```bash
docker-compose up -d database server
```

3. Starts client 1 and client 2
```bash
docker-compose run client-1 /client.py
docker-compose run client-2 /client.py
```
#### Docker video
https://user-images.githubusercontent.com/32321558/156919676-ad5614f1-c39c-46df-9f79-6cdd763bdfec.mp4


## After installation

1. When you're inside the container type help to get a list of all the commands
```bash
>>> help
```

Have fun!

# Made by group 71:
<table>
    <td align="center">
        <a href="https://github.com/omfj">
            <img height="100" src="https://avatars.githubusercontent.com/u/32321558?v=4" />
            <br>
            <sub><b>Ole Magnus</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/eirikbe01">
            <img height="100" src="https://avatars.githubusercontent.com/u/100426260?v=4" />
            <br>
            <sub><b>Eirik</b></sub>
        </a>
    </td>
</table>
