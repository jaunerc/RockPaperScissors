import Game


def launch():
    #
    # Start the game
    #
    print 'Welcome'
    print 'Please type s to start'

    player, srv_addr = Game.init()

    Game.connect(player, srv_addr)

    Game.share_graphs(player)

    is_over = Game.play(player)
    while not is_over:
        print 'It is a draw'
        is_over = Game.play(player)

    raw_input()


launch()