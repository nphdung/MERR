#!/usr/bin/python3
from read_network_function import read_graph
from itertools import permutations
import networkx as nx
import random

graph = "UsCarrier.graphml"
mpl = 8
num_per_case = 100

(DG,UG) = read_graph(graph)
nodes = list(DG.nodes)
demand_list = list(permutations(nodes,2))
fptr = open("Sample_uscarrier.txt",'w')

for num_demands in range(2,21):
    for num in range(num_per_case):
        d_list = list()
        i = 0
        while (i < num_demands):
            (s,t) = demand_list[random.randrange(len(demand_list))]
            if (s,t) not in d_list and (t,s) not in d_list and len(nx.dijkstra_path(DG,s,t)) <= mpl:
                d_list.append((s,t))
                fptr.write("({},{})".format(s,t))
                i = i + 1
                if i < num_demands: fptr.write(" ")
            else: continue
        fptr.write("\n")
fptr.close()
