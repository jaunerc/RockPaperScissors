import Game


def playing(player):
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