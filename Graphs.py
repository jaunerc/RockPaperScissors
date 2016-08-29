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
import random


class Graph:
    """
    This class represents an simple, undirected and unweighted graph.
    """
    def __init__(self, edges):
        """
        Creates a new Graph object. This method skips multiple edges between two vertices.
        :param edges: A list of tuples.
        """
        self.edges = []

        for edge in edges:
            skip = False
            for e in self.edges:
                if edge[0] in e and edge[1] in e:
                    skip = True

            if not skip:
                self.edges.append(edge)

    def deg(self, vertex):
        """
        Calculates the degree of the given vertex. This method returns 0 if the given vertex is not included
        in an edge or in the entire edges list.
        :param vertex: The vertex to calculate the degree.
        :return: The degree or 0.
        """
        num = 0
        for edge in self.edges:
            if vertex in edge:
                num += 1
        return num

    def vertices(self):
        """
        Returns a list of vertices.
        :return: The list of vertices.
        """
        vertices = []
        for edge in self.edges:
            for vertex in edge:
                if vertex not in vertices:
                    vertices.append(vertex)
        return vertices

    def max_deg(self):
        """
        Returns the highest degree in this graph.
        :return: The highest degree in this graph.
        """
        vertices = self.vertices()
        max_d = self.deg(vertices[0])
        for i in range(1, len(vertices)):
            max_d = max(max_d, self.deg(vertices[0]))
        return max_d

    def num_vertices(self):
        """
        Returns the number of vertices in this graph. This method invokes self.vertices() to
        create a list of all vertices.
        :return: The number of vertices in this graph.
        """
        return len(self.vertices())

    def isomorphic_copy(self):
        """
        Creates a random graph, that is isomorphic to self.
        :return: The isomorphic graph, The isomorphism.
        """
        L = list(range(self.num_vertices()))
        random.shuffle(L)
        f = permut_function(L)
        e = apply_isomorphism(self.edges, f)
        return Graph(e), L


def permut_function(L):
    """
    The lambda function returns the isomorphic vertex value for the given vertex.
    :param L: The isomorphism list.
    :return: A function to apply an isomorphism.
    """
    return lambda i: L[i - 1] + 1


def inv_permut_function(L):
    """
    The lambda function returns the inverse vertex value for the given isomorphic vertex.
    :param L: The isomorphism list.
    :return: A function to inverse an isomorphism.
    """
    return lambda i: 1 + L.index(i - 1)


def apply_isomorphism(G, f):
    """
    Creates a function to apply the given isomorphism f to the given graph G.
    :param G: Graph to apply the isomorphism.
    :param f: The isomorphism function.
    :return: A list of isomorphic tuples.
    """
    return [(f(i), f(j)) for (i, j) in G]


def random_adjacency_mat(vertices, degree):
    """
    Creates a random adjacency matrix. The algorithm creates a valid square matrix
    where each vertex has the given degree. The edges were built randomly. It is
    possible that the random distribution is not valid. In that case, the algorithm
    aborts the matrix and starts new.
    :param vertices: The number of vertices.
    :param degree: The degree for each vertex.
    :return: A random adjacency matrix.
    """
    M = None
    valid = False

    # Creates a new adjacency matrix until the matrix is valid.
    while not valid:
        M = []

        # A list that contains the sum of edges for each row of the matrix.
        # The init value is 0 for each row
        edges_per_row = []

        # Initializes the matrix with zeros.
        for i in range(0, vertices):
            row = []
            edges_per_row.append(0)
            for j in range(0, vertices):
                row.append(0)
            M.append(row)

        # Creates random entries for the matrix.
        # Iterates through each row
        for i in range(0, vertices):

            # The number of edges, who contains the current vertex.
            # The init value is zero.
            count_edges = 0

            # A list with column numbers of possible vertices to build an edge with the current vertex.
            # This list will be refilled in the column for-loop for each row.
            possible_indexes = []

            # Iterates through each column of the matrix.
            for j in range(0, vertices):

                if j < i:
                    # Lower triangular matrix
                    # Counts all edges who contains this vertex
                    if M[i][j] == 1:
                        count_edges += 1

                elif j == i:
                    # Main diagonal
                    # All values of the main diagonal must be zero.
                    # Determines how many edges must be added to reach the degree
                    edges_needed = degree - count_edges

                else:
                    # Upper triangular matrix
                    # Appends all vertex indexes to the list, who are valid to connect.
                    if count_edges < degree:
                        if edges_per_row[j] < degree:
                            possible_indexes.append(j)

            # Try to build new edges, as many as needed.
            for a in range(0, edges_needed):

                # Checks if there are vertices to connect
                if len(possible_indexes) > 0:

                    # Chooses a random vertex to build a new edge
                    index = random.randint(0, len(possible_indexes) - 1)
                    vertex = possible_indexes.pop(index)

                    # Sets the edge in the upper and lower triangular matrix
                    M[i][vertex] = 1
                    M[vertex][i] = 1

                    # Increments the edge counters
                    edges_per_row[vertex] += 1
                    edges_per_row[i] += 1

            # Checks if the current row has the correct number of edges.
            # Aborts this matrix, if the row is not valid.
            if edges_per_row[i] != degree:
                valid = False
                break
            else:
                valid = True

    return M


def print_mat(m):
    """
    Prints the given matrix. This method prints all values for each row in one line.
    :param m: The matrix to print out.
    """
    for x in range(0, len(m)):
        row = ''
        for y in range(0, len(m)):
            row += str(m[x][y])
        print row


def edges_from_adjacency_mat(M):
    """
    Creates edges from the given adjacency matrix. This method aborts, if the given
    matrix is not a square matrix. Each edge is stored in a tuple.
    :param M: The adjacency matrix to build the edges.
    :return: A list with tuples.
    """
    edges = []
    if len(M) == len(M[0]):
        for i in range(0, len(M)):
            for j in range(0, len(M)):
                if j > i:
                    if M[i][j] != 0:
                        edges.append((i+1, j+1))

    else:
        print 'The given matrix is not a square matrix.'

    return edges


def random_graph(vertices, degree):
    """
    Creates a random graph. Each vertex of the graph has the same degree.
    The resulted graph is simple, undirected and unweighted.
    :param vertices: The number of vertices.
    :param degree: The degree for each vertex.
    :return: A random created graph.
    """
    M = random_adjacency_mat(vertices, degree)
    edges = edges_from_adjacency_mat(M)
    #print ('The resulted graph has '+str(vertices)+' vertices and '+str(len(edges))+' edges.')
    return Graph(edges)

