# RockPaperScissors

## Synopsis
Rock-Paper-Scissor game based on graphtheory.

## Installation / Execution
The RPS-Application can be started with the Launch.py file in a python console. It requires all *.py files of this repo.

## Motivation
There was a math school module last semester, where we were introduced to discrete mathematics. One of the topics was graphtheory.
We learned the basics and some possible applications of graphisomorphism and there was an idea of a Rock-Paper-Scissor game where each
object (Rock, Paper or Scissor) is represented by a graph. Those three graphs should be non-isomorphic. When the game starts
and a player sends a isomorphic copy of his choice (e.g. Rock), the opponent can't figure out quickly which original graph was chosen.
That's because determining whether two graphs are isomorphic is very hard 
(Take a look at [wikipedia](https://en.wikipedia.org/wiki/Graph_isomorphism_problem) for detailed informations about the graph isomorphism problem.).
That was the initial idea of this project.

## Requirements
This application is written in Python 2 and tested with Python 2.7.3. It uses the standard python module pickle for the network communication.

## License
All files are published under the MIT license.
