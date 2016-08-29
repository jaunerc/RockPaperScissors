import sys, RPSNetwork, socket, Graphs, pickle, time
from thread import *

#
# User input to start the game.
#
USR_START = 's'

#
# The number of graphs in a game.
#
GRAPH_NUMBERS = 3

#
# Flag for the input_handler function. Indicates that the input should be string.
#
REQ_STRING = 0

#
# Flag for the input_handler function. Indicates that the input should be int.
#
REQ_INTEGER = 1

#
# Flag for the input_handler function. Indicates that the input should be a valid port number.
#
REQ_PORT = 2

#
# The game result for winning.
#
RES_WIN = 1

#
# The game result for loosing.
#
RES_LOOSE = 0

#
# The game result for a draw.
#
RES_DRAW = -1


class Player:
    """
    This class represents a player. A player object stores the name, the RPSClient
    and a graph list.
    """
    def __init__(self):
        """
        Creates a new player object.
        """
        self.name = ''
        self.client = None
        self.graphs = []

    def look_for_server(self, port):
        """
        Invokes the discover function of self.client.
        :param port: The port number of the RPSServer.
        :return: The address tuple of the RPSServer or None, if it can't find a server.
        """
        return self.client.discover(port)

    def connect(self, srv_addr):
        """
        Connects the self.client to the given address.
        :param srv_addr: Address tuple of the server.
        """
        self.client.connect(srv_addr)

    def send(self, msg):
        """
        Sends the given message with self.client.
        :param msg: String message to send.
        """
        self.client.send(msg)

    def receive(self):
        """
        Receives a message with self.client.
        :return: The received message or None if the socket of the client is None.
        """
        return self.client.receive()

    def add_graph(self, g):
        """
        Appends the given graph to self.graphs.
        :param g: Reference to graph object.
        """
        self.graphs.append(g)

    def send_graph(self, i):
        """
        Sends the graph on the given index with self.client.
        :param i: The index of a graph in self.graphs.
        """
        g = self.graphs[i]
        self.send(pickle.dumps(g.edges))

    def load_graph(self, dmp):
        """
        Receives a graphs and appends it at self.graphs.
        :param dmp: A pickle dump that contains the edge list of a graph.
        """
        edges = pickle.loads(dmp)
        self.graphs.append(Graphs.Graph(edges))

    def get_graph(self, i):
        """
        Returns the graph at index i in self.graphs or None if i is out of range.
        :param i: The index of the graph.
        :return: The graph at index i or None.
        """
        if 0 <= i < len(self.graphs):
            return self.graphs[i]
        else:
            return None

    def get_graph_index(self, g):
        """
        Returns the index of the given graph in the self.graphs list.
        :param g: The graph to find the index of.
        :return: The index of the graph or -1 if the graph is not found.
        """
        for i in range(0, len(self.graphs)):
            if (self.graphs[i]).edges == g.edges:
                return i
        return -1


def separator(num_lines):
    """
    Prints a string of *-signs to the console.
    :param num_lines: The number of lines to print out.
    """
    for i in range(0, num_lines):
        print '******************************************'


def input_handler(req=REQ_STRING, prompt=''):
    """
    Helper function to read user input from the console.
    :param req: Value for the required data type.
    :param prompt: String to show on the console.
    :return: The users input if it is valid or None.
    """
    inp = None
    if req == REQ_STRING:
        inp = raw_input(prompt)

    elif req == REQ_INTEGER:
        try:
            inp = int(raw_input(prompt))
        except ValueError:
            inp = None

    elif req == REQ_PORT:
        inp = input_handler(REQ_INTEGER, prompt)
        if inp is None or inp < 0 or inp > 65535:
            inp = None

    return inp


def init():
    """
    Initializes the game. Asks for the user name and connection details. The server address can be None
    if no server can be found and a own server can not be started.
    :return: [0] A player object and [1] the server address.
    """

    # Waits for the user input.
    # Exits the program if the input is not correct.
    inp = input_handler()
    if inp == USR_START:
        print 'Type your name'
        inp = input_handler(REQ_STRING, 'Your name: ')
    else:
        sys.exit(0)

    # Creates a new player object to store the name and a client object.
    player = Player()
    player.name = inp
    player.client = RPSNetwork.RPSClient()

    # Asks for the server port.
    print 'Type the servers port'
    inp = input_handler(REQ_PORT, 'Port number:')
    while inp is None:
        print "Your input is not valid..."
        inp = input_handler(REQ_INTEGER, 'Port number:')

    # Discovers the network for a RPS server.
    srv_addr = player.look_for_server(inp)

    # Starts own server if no server can be found.
    if srv_addr is None:
        print 'No RPS Server found, try to start a new server'
        print 'On which port should your server listen?'

        # Waits for a valid port number
        inp = input_handler(REQ_PORT, 'Port number:')
        while inp is None:
            print "Your input is not valid..."
            inp = input_handler(REQ_INTEGER, 'Port number:')

        # Creates a new RPSServer
        server = RPSNetwork.RPSServer()
        # Starts new server threads
        start_new_thread(server.start, (inp, inp))

        # Wait for the server startup
        time.sleep(2)

        if not server.running:
            print 'Unable to start server'
            sys.exit(0)
        else:
            srv_addr = ('localhost', inp)

    separator(1)

    return player, srv_addr


def connect(player, srv_addr):
    """
    Connects the given player to the given server address.
    :param player: The player object.
    :param srv_addr: Server address, port tuple.
    """

    # Connects this player with the server and send the player name.
    player.connect(srv_addr)
    player.send(player.name)

    print 'Successfully connected with '+str(srv_addr[0])
    print 'Wait for other players'

    # Waits for the opponent
    opponents_name = player.receive()
    print 'Your opponent is '+opponents_name


def share_graphs(player):
    """
    The first player has to generate and share graphs. The players client must be connected to
    invoke this function.
    :param player: The player object.
    :return: Whether the sharing was successfully or not.
    """

    separator(1)

    success = False

    # Waits for the server response. There are two possible cases
    # either, this player has to generate graphs
    # or, this player gets graphs from the other player
    srv_req = player.receive()
    if srv_req is not None:

        if srv_req == RPSNetwork.GRAPHS_NEED:
            # This player has to generate graphs
            # Each graph is sent to the server

            print 'Generate graphs...'

            for i in range(0, GRAPH_NUMBERS):
                # Creates new random graphs
                g = Graphs.random_graph(100, 2)
                player.add_graph(g)
                player.send_graph(i)

            print 'All graphs sent'
            success = True

        elif srv_req == RPSNetwork.GRAPHS_SEND_START:
            # This player receives graphs

            srv_req = player.receive()

            while srv_req != RPSNetwork.GRAPHS_SEND_END:
                # Receive graphs until the end request is received

                player.load_graph(srv_req)
                srv_req = player.receive()

            print 'All graphs received'
            success = True

    else:
        print 'The server is not accessible'

    separator(1)

    return success


def ask_for_graph(player):
    """
    Lets the user choose a graph. This function checks the user input.
    As long as the input is not valid, the function asks for a new value.
    :param player: The player object.
    :return: The chosen index.
    """

    print 'Your turn. Choose an integer in the range 0 to 2'
    print 'The values stands for: 0-Rock, 1-Paper, 2-Scissor'
    i = input_handler(REQ_INTEGER, 'Choice:')
    while i is None:
        print 'The input was not correct. Try again!'
        i = input_handler(REQ_INTEGER, 'Choice:')

    print "You're choice " + ['Rock', 'Paper', 'Scissor'][i]

    separator(1)

    return i


def ask_for_isomorphic_graph(player):
    """
    Lets the user choose a graph and returns a random isomorphic copy.
    :param player: The player object.
    :return: The graph object, The isomorphism.
    """
    return (ask_for_graph(player)).isomorphic_copy()


def oppon_turn(player):
    """
    Receives a request of the opponent and loads it with pickle.
    :param player: The player object.
    :return: The pickle load result of the request.
    """
    print 'Wait for opponents turn...'
    return pickle.loads(player.receive())


def calc_result(my_i, op_i):
    """
    Calculates the game result. Player 1 must be the own player object and player 2 the opponent.
    There are three possible results:
    - Player 1 has won
    - Player 2 has won
    - It's a draw
    The RES_ constants represents the three results.

    :param my_i: The graph index of player 1
    :param op_i: The graph index of player 2
    :return: The game result.
    """
    res = RES_LOOSE
    op_choice_txt = ""
    if my_i != op_i:
        if my_i == 0:
            # My choice was rock

            if op_i == 2:
                # Opponent choose scissor

                op_choice_txt = 'Scissor'
                res = RES_WIN
        elif my_i == 1:
            # My choice was paper

            if op_i == 0:
                # Opponent choose rock

                op_choice_txt = 'Rock'
                res = RES_WIN
        elif my_i == 2:
            # My choice was scissor

            if op_i == 1:
                # Opponent choose paper

                op_choice_txt = 'Paper'
                res = RES_WIN
    else:
        res = RES_DRAW

    print 'The opponent choose '+op_choice_txt

    return res


def finish_turn(player, my_i, op_graph):
    """
    Finish the current turn.
    :param player: The player object. If the given graph is not valid, the game will be exited.
    :param op_graph: The graph object of the opponent.
    """
    op_i = player.get_graph_index(op_graph)

    if op_i == -1:
        print 'The received graph is not correct. The game is exited.'
        sys.exit(1)
    else:
        game_result = calc_result(my_i, op_i)
        if game_result == RES_WIN:
            print 'You won!'
        elif game_result == RES_LOOSE:
            print 'You loose...'
        elif game_result == RES_DRAW:
            print "It's a draw"

    return game_result


def play(player):
    """
    Handles the game turns. This function should be invoked after init(), connect() and share_graphs().
    :param player: The player object.
    :return:
    """
    srv_req = player.receive()
    is_over = False
    game_result = None
    if srv_req == RPSNetwork.TURN_NEED:

        # Asks for rock, paper or scissor.
        choice = ask_for_graph(player)
        my_g = player.get_graph(choice)

        # A isomorphic copy of the chosen graph will be sent to the opponent.
        my_iso_g, iso = my_g.isomorphic_copy()
        dmp = pickle.dumps(my_iso_g)
        player.send(dmp)

        # Receives the opponents chosen graph.
        op_g = oppon_turn(player)

        # Send the isomorphism
        player.send(pickle.dumps(iso))

        # Check if the game is over and determine the winner.
        game_result = finish_turn(player, choice, op_g)

    elif srv_req == RPSNetwork.TURN_SEND:

        # Receives the opponents chosen graph.
        op_g = oppon_turn(player)

        # Asks for rock, paper or scissor.
        choice = ask_for_graph(player)
        my_g = player.get_graph(choice)
        dmp = pickle.dumps(my_g)
        player.send(dmp)

        # Receives the opponents isomorphism
        op_iso = oppon_turn(player)

        # Calculates the opponents graph back.
        inv_func = Graphs.inv_permut_function(op_iso)
        op_edges = Graphs.apply_isomorphism(op_g.edges, inv_func)
        op_g = Graphs.Graph(op_edges)

        # Check if the game is over and determine the winner.
        game_result = finish_turn(player, choice, op_g)

    if game_result != RES_DRAW:
        is_over = True

    player.send(str(game_result))

    return is_over


def play_again(player):
    """
    Handles a regame. Asks the given player if he want to play again.
    After that, it waits for the opponents answer.
    :param player: The player object.
    :return: True, if both players wants to play again.
    """
    print 'Type a to play again'
    again = input_handler(REQ_STRING, 'input: ')

    if again == 'a':
        player.send(RPSNetwork.PLAY_AGAIN_TRUE)

        print 'Wait for the opponents response'
        op_answer = player.receive()

        if op_answer == RPSNetwork.PLAY_AGAIN_TRUE:
            return True
    else:
        player.send(RPSNetwork.PLAY_AGAIN_FALSE)

    return False
