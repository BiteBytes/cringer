#!/usr/bin/python

from backend.games.counter.SourceLib import SourceRcon

rcon = SourceRcon.SourceRcon('213.149.249.33', 27160, 'nocr1p')
#213.149.249.33:27160
#27105

status = rcon.rcon("say testing");
print status
status = rcon.rcon("say r hola");
print status