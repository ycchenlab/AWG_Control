'''
Atom array
1. create a list of atom array to simulate the atom loading
2. rearrangement
'''
import random


def sim_array(n=100, p=0.6):
    # n: number of traps, p: probability of having an atom in a trap
    # return: a list of atom array
    l = []
    for i in range(n):
        l.append(1 if random.random() < p else 0)
    return l


