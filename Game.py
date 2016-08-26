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

RES_WIN = 1

RES_LOOSE = 0

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
    print 'Type the server port to start broadcast'
    inp = input_handler(REQ_INTEGER, 'Port number:')

    # Discover the network for a RPS server.
    srv_addr = player.look_for_server(inp)

    # Start own server if no server can be found.
    if srv_addr is None:
        print 'No RPS Server found, start own server'
        print 'On which port should your server listen?'

        inp = input_handler(REQ_INTEGER, 'Port number:')
        server = RPSNetwork.RPSServer()
        start_new_thread(server.start, (inp, inp))
        time.sleep(2)
        if not server.running:
            print 'Unable to start server'
            sys.exit(0)
        else:
            srv_addr = ('localhost', inp)

    return player, srv_addr


def connect(player, srv_addr):
    # Connects this player with the server and send the player name.
    player.connect(srv_addr)
    player.send(player.name)

    print 'The RPS Server is running'
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
                g = Graphs.random_graph(10, 2)
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
    return pickle.loads(player.receive())


def get_graph_index(player, g):
    for i in range(0, len(player.graphs)):
        if (player.graphs[i]).edges == g.edges:
            return i
    return -1


def calc_result(my_i, op_i):
    res = RES_LOOSE
    if my_i != op_i:
        if my_i == 0:
            # Rock
            if op_i == 2:
                # Opponent choose scissor
                res = RES_WIN
        elif my_i == 1:
            # Paper
            if op_i == 0:
                # Opponent choose rock
                res = RES_WIN
        elif my_i == 2:
            # Scissor
            if op_i == 1:
                # Opponent choose paper
                res = RES_WIN
    else:
        res = RES_DRAW
    return res


def check_graphs(player, my_graph, op_graph):
    res = False

    print 'My_Graph: '+str(my_graph.edges)
    print 'Op_Graph: '+str(op_graph.edges)

    my_i = get_graph_index(player, my_graph)
    op_i = get_graph_index(player, op_graph)

    if my_i != -1 and op_i != -1:
        return calc_result(my_i, op_i)
    else:
        print 'there was a problem'


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
        game_result = check_graphs(player, my_g, op_g)
        print 'The result is '+str(game_result)

    elif srv_req == RPSNetwork.TURN_SEND:

        # Receives the opponents chosen graph.
        op_g = oppon_turn(player)

        # Asks for rock, paper or scissor.
        my_g = player.get_graph(ask_for_graph(player))
        dmp = pickle.dumps(my_g)
        player.send(dmp)

        # Receives the opponents isomorphism
        op_iso = oppon_turn(player)

        # Calculates the opponents graph back.
        inv_func = Graphs.inv_permut_function(op_iso)
        op_edges = Graphs.apply_isomorphism(op_g.edges, inv_func)
        op_g = Graphs.Graph(op_edges)

        # Check if the game is over and determine the winner.
        game_result = check_graphs(player, my_g, op_g)
        print 'The result is ' + str(game_result)

    if game_result != -1:
        is_over = True

    player.send(str(game_result))

    return is_over
