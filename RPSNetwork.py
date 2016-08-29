import socket
import struct
import threading
import datetime
from thread import *

#
# Broadcast message of the client.
#
REQ_HELLO = 'HELLO_SERVER'

#
# Answer message of the server for a udp request.
#
ANS_HELLO = 'RPS_SERVER'

#
# Message to request graphs
#
GRAPHS_NEED = 'NEED_GRAPHS'

#
# Message to initiate graph sending
#
GRAPHS_SEND_START = 'START_SENDING_GRAPHS'

#
# Message to stop graph sending
#
GRAPHS_SEND_END = 'END_SENDING_GRAPHS'

#
# Message to request a turn
#
TURN_NEED = 'NEED_TURN'

#
# Message to inform the client, that the next message contains a graph
#
TURN_SEND = 'SEND_TURN'

#
# Request of a client when he want's a regame.
#
PLAY_AGAIN_TRUE = 'PL_TRUE'

#
# Request of a client when he don't want to play again.
#
PLAY_AGAIN_FALSE = 'PL_FALSE'


#
# Helper functions
#
def send_msg(sock, msg):
    """
    Sends the given message with the given socket. This function appends four bytes at the begin of msg.
    These four bytes contains the length of the origin msg.
    :param sock: Socket object to send.
    :param msg: String message.
    """

    # Stores the length of message in big-endian order
    msg = struct.pack('>I', len(msg)) + msg

    # Writes all bytes to the stream
    sock.sendall(msg)


def recv_msg(sock):
    """
    Receives a message from the given socket. This function reads the first four bytes from the stream
    to determine the byte-length of the message. Afterwards it reads exactly so many bytes from
    the stream.
    :param sock: Socket object to receive.
    """

    # Reads message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]

    # Reads the whole message
    return recvall(sock, msglen)


def recvall(sock, n):
    """
    Reads bytes from the given socket stream as long as the received data length is lower than n.
    :param sock: Socket object to receive data.
    :param n: The target length of the message.
    """

    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def out(msg):
    """
    Prints out the given message with a timestamp. This function is for debugging purposes.
    :param msg:
    :return:
    """
    now = datetime.datetime.now()
    #print (now.__str__() + ' - ' + msg)


class RPSServer:
    """
    This class represents the server side of the RPS network.
    """

    def __init__(self):
        """
        Creates a new RPSServer object.
        """
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.p1 = None
        self.p2 = None

    def udp_listener(self):
        """
        Listen for messages on the servers udp port and sends an answer for each incoming request.
        """
        while self.running:
            m = self.sock_udp.recvfrom(1024)
            self.sock_udp.sendto(ANS_HELLO, m[1])

    def start(self, tcp_port, udp_port):
        """
        Starts listening on udp and tcp sockets.
        :param tcp_port: The port to listen with the tcp socket.
        :param udp_port: The port to listen with the udp socket.
        """
        self.running = True

        try:
            self.sock.bind(('', tcp_port))
            self.sock_udp.bind(('', udp_port))
            self.sock.listen(2)

            start_new_thread(self.udp_listener, ())

            out('Server listen on port '+str(tcp_port)+'/tcp')
            out('Server listen on port '+str(udp_port)+'/udp')

        except socket.error, msg:
            self.sock.close()
            self.sock = None
            self.running = False
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

        if self.sock is not None:
            gt = None
            while self.running:
                conn, addr = self.sock.accept()

                if self.p1 is None:
                    self.p1 = conn
                    out('Player 1 is connected')
                elif self.p2 is None:
                    self.p2 = conn
                    out('Player 2 is connected')
                else:
                    conn.close()
                    out('rps is already running')

                # If both players are connected, start the game
                if gt is None and self.p1 is not None and self.p2 is not None:
                    gt = RPSThread(self.p1, self.p2)
                    gt.start()


class RPSThread(threading.Thread):
    """
    This class represents a thread to handle a game.
    """
    def __init__(self, p1, p2):
        """
        Creates a new RPSThread object.
        :param p1: Socket of player 1.
        :param p2: Socket of player 2.
        """
        threading.Thread.__init__(self)
        self.p1 = p1
        self.p2 = p2

    def run(self):
        is_over = False

        proto = RPSProtocol()

        out('New rps game started')

        # Loop to process the protocol.
        while not is_over:
            is_over = proto.next_step(self.p1, self.p2)

        out('The current rps is over')

        self.p1.close()
        self.p2.close()


class RPSClient:
    """
    This class represents the client side of the RPS network
    """
    def __init__(self, timeout=5):
        """
        Creates a new RPSClient object.
        :param timeout: The timeout of the diagram socket in seconds. The default value are 5 seconds.
        """
        self.sock = None
        self.timeout = timeout

    def discover(self, srv_port):
        """
        Sends a broadcast to look for a RPSServer on the given port.
        :param srv_port: The port number of the RPSServer.
        :return: The address tuple of the RPSServer or None, if it can't find a server.
        """
        addr = None
        answ = None

        # Creates a new datagram socket to broadcast
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(self.timeout)
        s.sendto(REQ_HELLO, ('255.255.255.255', srv_port))

        # Wait for a server answer
        try:
            answ = s.recvfrom(1024)
        except socket.timeout:
            print 'Timeout exceeded...'

        # Close the diagram socket.
        s.close()

        # Saves the address if the server answer was correct.
        if answ is not None and answ[0] == ANS_HELLO:
            addr = answ[1]
        return addr

    def connect(self, addr):
        """
        Connects the tcp socket to the given address.
        :param addr: Address tuple of the server.
        :return: Whether the connect was successfully or not.
        """
        result = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect(addr)
            result = True
        except socket.error, msg:
            self.sock = None
            print 'Connect failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

        return result

    def send(self, msg):
        """
        Sends the given message with the tcp socket of self. This function invokes the
        send_msg function of that module.
        :param msg: String message to send.
        """
        if self.sock is not None:
            send_msg(self.sock, msg)

    def receive(self):
        """
        Receives a message and returns it. This function invokes the recv_msg function
        of that module.
        :return: The received message or None if the socket of self is None.
        """
        if self.sock is not None:
            return recv_msg(self.sock)
        return None


def prepare(p1, p2):
    """
    First protocol step. Exchanges the player names.
    :param p1: Socket of player 1.
    :param p2: Socket of player 2.
    :return:
    """
    n1 = recv_msg(p1)
    n2 = recv_msg(p2)

    out('The name of player 1 is ' + n1)
    out('The name of player 2 is ' + n2)

    send_msg(p1, n2)
    send_msg(p2, n1)

    return False


def share_graphs(p1, p2):
    """
    Second protocol step. Initializes the graphs and sends them to both players.
    :param p1: Socket of player 1.
    :param p2: Socket of player 2.
    :return:
    """

    # Send a message to player 1, so that this player creates the graphs and send
    # them to this server.
    send_msg(p1, GRAPHS_NEED)

    e1 = recv_msg(p1)
    e2 = recv_msg(p1)
    e3 = recv_msg(p1)

    send_msg(p2, GRAPHS_SEND_START)
    send_msg(p2, e1)
    send_msg(p2, e2)
    send_msg(p2, e3)
    send_msg(p2, GRAPHS_SEND_END)

    return False


def turn(p1, p2):
    """
    Third protocol step. This function handles a turn.
    :param p1: Socket of player 1.
    :param p2: Socket of player 2.
    :return: Whether the game is over or not.
    """
    send_msg(p1, TURN_NEED)
    send_msg(p2, TURN_SEND)
    t1 = recv_msg(p1)
    send_msg(p2, t1)
    t2 = recv_msg(p2)
    send_msg(p1, t2)
    t3 = recv_msg(p1)
    send_msg(p2, t3)

    res_p1 = int(recv_msg(p1))
    res_p2 = int(recv_msg(p2))

    if res_p1 == res_p2:
        # If the results aren't equals, the game will be interrupted

        if res_p1 == -1:
            return False

    return True


def play_again(p1, p2):
    p1_again = recv_msg(p1)
    p2_again = recv_msg(p2)

    send_msg(p1, p2_again)
    send_msg(p2, p1_again)

    return p1_again == PLAY_AGAIN_TRUE and p2_again == PLAY_AGAIN_TRUE


class RPSProtocol:
    """
    This class represents a protocol to organize the network requests
    between clients and server.
    """
    def __init__(self):
        """
        Creates a new RPSProtocol object.
        """
        self.index = 0

    def next_step(self, p1, p2):
        """
        Proceeds the next protocol step and returns the result.
        :param p1: Socket of player 1.
        :param p2: Socket of player 2.
        :return:
        """

        self.index += 1
        out('Protocol step' + str(self.index))

        if self.index == 1:
            return prepare(p1, p2)

        elif self.index == 2:
            return share_graphs(p1, p2)

        elif self.index == 3:
            if turn(p1, p2):
                # The game is over

                return False
            else:
                # It's a draw. The game needs a new turn
                self.index -= 1
                return False

        elif self.index == 4:
            if play_again(p1, p2):
                self.index = 2
                return False
            else:
                return True
