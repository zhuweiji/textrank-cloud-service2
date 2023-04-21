import logging
from typing import Union

import numpy as np

log = logging.getLogger(__name__)

## Non-iterative version
def noniterative_pr(A: list[list[Union[int, float]]], 
                    c1: float) -> list:
    '''
    Demonstrates slide 54 of cloud computing pagerank notes.

    A: adjacency matrix of the node graph
    c1: probability that the next node will be one of the nodes in the current node graph
    returns: 1d array that ranks each node based on how important they are in the graph
    '''
    c2 = 1- c1

    def normalization(arr):
        ans = []
        for row in arr:
            row_sum = sum(row)
            if row_sum != 1:
                curr = []
                for num in row:
                    curr.append(num/row_sum)
                ans.append(curr)
            else:
                ans.append(row)
        return ans


    def teleportation(arr):
        ans = []
        num_of_nodes = len(arr[0])
        for i in range(num_of_nodes):
            row = []
            for j in range(num_of_nodes):
                row.append(1/num_of_nodes)
            ans.append(row)

        return ans

    def transition(norm_A, teleport_A, alpha, alpha_star):
        ans = []
        num_of_nodes = len(norm_A[0])
        for i in range(num_of_nodes):
            row = []
            for j in range(num_of_nodes):
                row.append(norm_A[i][j] * alpha + teleport_A[i][j]*alpha_star)
            ans.append(row)

        return ans



    norm_A = normalization(A)
    # print("After normalizing: A is \n",np.array(norm_A))

    teleport_A = teleportation(A)
    # print("For random teleporting, teleport_A is \n",np.array(teleport_A))

    trans_prob_matrix = transition(norm_A, teleport_A, c1, c2)
    # print("trans_prob_matrix is \n",np.array(trans_prob_matrix))
    return trans_prob_matrix


# A = [[0, 1, 0],
#     [1, 0, 1],
#     [0, 1, 0]]

# # c1 = 0.5
# prob_A_matrix = noniterative_pr(A, 0.5)

## Iterative version
def iterative_pr(M: list[list[Union[int, float]]], 
                 c1: float, 
                 converge_val: float,
                 ) -> list:
    '''
    Calculates the pagerank of a given node graph M (2d array of either int or float type).
    
    M:  2d array of either int or float type
    c1: probability of going back to a node in the same graph
    converge_val:  difference between previous iteration and current iteration should not have a difference of more than this value, if not continue iterating
    returns: ranking of each node (in terms of its probability) after the final iteration.

    The inital guess for the importance of each node will be 1/(number of nodes in the graph).
    The iteration should be big enough such that there is no more difference between the current 
    and preivous iteration. 
    '''


    c2 = 1- c1

    num_of_pages = len(M[0])
    # first guess of the ranking of each page
    x =               [(1/num_of_pages) for i in range(num_of_pages)]
    random_jump_arr = [(1/num_of_pages) for i in range(num_of_pages)]
    
    curr_converge = float("inf")
    iterate_num = 1
    
    # print("Initial guess for x is \n", np.array(x))

    # for i in range(NUM_OF_ITERATIONS):
    while curr_converge >= converge_val:
        Mx = []
        for row in M:
            val = 0
            for page in range(num_of_pages):
                val += row[page] * x[page] * c1
            Mx.append(val)
        
        # Mx + random_prob
        for page in range(num_of_pages):
            Mx[page] += random_jump_arr[page] * c2
            
        # calculate convergence
        curr_converge = 0
        for word in range(len(x)):
            curr_converge += abs(x[word] - Mx[word])
            
        x = Mx
        
        # print("After iteration number " + str(i)+":")
        # print("x is \n", np.array(x))
        # print()

    return x

M = [[0.5, 0.5, 0],
    [0.5, 0, 0],
    [0, 0.5, 1]]

# M = [[0, 1, 0], [0.5, 0.0, 0.5], [0, 1, 0]]

# final_pr = iterative_pr(M, 0.8, 50)
# print("Pagerank is \n", np.array(M))
# print(final_pr)
