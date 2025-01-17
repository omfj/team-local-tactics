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

When running it locally, make sure that the scripts folder is its root folder.
Run in this order:
1. Database
2. Server
3. Clients

### Docker
1. Buld and run the database and server detached
```bash
docker-compose up -d database server
```

2. Starts a client
```bash
docker-compose run client
```

3. To play TLT you need two run two client. Just run the same command in another tab/window.

#### Docker video
https://user-images.githubusercontent.com/32321558/156929374-4dff4bd8-8cd6-47af-82dd-086a175befc4.mp4

## After installation
1. When you're inside the container type help to get a list of all the commands
```bash
>>> help
```

GL HF!

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
