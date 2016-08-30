"""
Copyright (c) 2016 Cyrill Jauner

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import Game


def playing(player):
    """
    Handles the playing steps.
    :param player: The player object.
    """
    is_over = Game.play(player)

    while not is_over:
        print 'It is a draw'
        Game.separator(2)

        is_over = Game.play(player)


def launch():
    """
    Function to launch a RPS game.
    """

    Game.separator(1)
    print 'Welcome to Rock-Paper-Scissor'
    Game.separator(1)
    print 'Please type s to start'

    player, srv_addr = Game.init()

    Game.connect(player, srv_addr)

    Game.share_graphs(player)

    playing(player)

    while Game.play_again(player):
        playing(player)


launch()