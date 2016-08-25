import Game


def launch():
    #
    # Start the game
    #
    print 'Welcome'
    print 'Please type s to start'

    res = Game.init()

    Game.connect(res[0], res[1])

    Game.share_graphs(res[0])

    Game.play(res[0])

    raw_input()


launch()