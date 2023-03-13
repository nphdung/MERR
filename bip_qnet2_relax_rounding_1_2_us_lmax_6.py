#!/usr/bin/python3
# Appoximation Approach using Randomized Rounding
import pulp
from random import random
import numpy as np
from read_network_function import read_graph
import networkx as nx
import sys

def rounding(demands,edges,lp_vars):
    flow = dict()
    for d in demands:
        for e in edges:
            #print(f"Rounding: Demand {d}, Edge {e}, prob: {lp_vars[d,e].value()}")
            #if random() <= lp_vars[d,e].value(): flow[d,e] = 1
            #else: flow[d,e] = 0
            #flow[d,e] = np.random.binomial(size=1,n=1,p=abs(lp_vars[d,e].value()))[0]
            if lp_vars[d,e].value() >= 0.5: flow[d,e] = 1
            else: flow[d,e] = 0
    return flow

def seperate_path(demand,edges):
    path = list()
    (u,v) = demand
    temp = u
    while True:
        for e in edges:
            if e[0] == temp:
                path.append(e)
                temp = e[1]
        if temp == u or temp == v: break
    return path

graph = "UsCarrier.graphml"
lmax = 6

(DG,UG) = read_graph(graph) # DG: directed graph, UG: undirected graph
nodes = list(DG.nodes)
edges = list(DG.edges)
u_edges = list(UG.edges)
#print(f"Nodes of the graph: {nodes}")
#print(f"Edges of the graph: {edges}")

# The set of demands
l_argv = sys.argv
l_argv.pop(0)
l_demand = list()
for i in l_argv:
    j = i.strip()
    j = j.replace('(','').replace(')','')
    j = j.split(',')
    l_demand.append((int(j[0]),int(j[1])))
demands = l_demand
#demands = [(47,15),(7,45),(43,0)]
#demands = [(29,18),(13,24)]
#demands = [(7,35),(31,7),(19,18),(41,38),(48,35),(37,26),(16,18),(19,21),(19,3),(44,1),(13,44),(41,15),(42,34),(0,24),(5,23),(46,17),(22,17),(0,43),(13,25),(28,38)]
#demands = [(42,25), (6,9), (8,20), (25,30), (22,10), (45,42), (14,37), (32,47), (29,20), (12,25), (32,2), (30,38), (9,45), (6,42), (27,35), (26,37), (45,38), (17,9), (47,46), (26,45)]
#demands = [(68,47), (106,91), (78,51), (150,73), (83,37), (10,16), (130,36), (74,110), (109,30), (33,98), (133,47), (18,107), (20,70), (21,69), (135,106)]
#demands = [(97,0), (37,31), (109,105), (108,90), (132,133), (56,54), (152,151), (127,122), (5,7), (80,20), (118,97), (67,17), (13,51), (110,115), (12,131)]

# define the LP problem
prob = pulp.LpProblem("Find the maximum number of satisfied demands",pulp.LpMaximize)

# define the variables of the problem
vars = list()
for d in demands:
    for e in edges:
        vars.append((d,e))  # should be a list of tuple

#print(f"list of variables: {vars}")
#lp_vars = pulp.LpVariable.dicts("Flow",vars,cat="Binary")
lp_vars = pulp.LpVariable.dicts("Flow",vars,lowBound=0,upBound=1,cat="Continous")   # for relaxation
#print(f"Variables: {lp_vars}")

# the objective function
temp = list()
for d in demands:
    for n in nodes:
        if (d[0],n) in edges: temp.append((lp_vars[(d,(d[0],n))],1))

#print(f"Objective variables: {temp}")
prob += pulp.LpAffineExpression(temp)

# the first constraint
for (u,v) in u_edges:
    prob += pulp.lpSum([lp_vars[d,(u,v)] for d in demands]) + \
            pulp.lpSum([lp_vars[d,(v,u)] for d in demands]) <= 1

# the second constraint
for v in nodes:
    for d in demands:
        if v not in d:  # examine all vertices but the source and sink of the demand
            temp_1 = list()
            temp_2 = list()
            for (u,w) in edges:
                if (u == v):
                    temp_1.append(lp_vars[d,(u,w)])
                    temp_2.append(lp_vars[d,(w,u)])
            prob += pulp.lpSum(temp_1) - pulp.lpSum(temp_2) == 0

# the third constraint
for d in demands:
    prob += pulp.lpSum([lp_vars[d,e] for e in edges if (e[0] == d[0])]) <= 1

# the forth constraint
for d in demands:
    for (u,v) in edges:
        if u == d[0]: prob += lp_vars[d,(v,u)] == 0

# the fifth constraint (the constraint of the path length)
for d in demands:
    prob += pulp.lpSum([lp_vars[d,e] for e in edges]) <= lmax

prob.writeLP("bip_qnet2_relax.txt")   # log file (use to record the linear program)
prob.solve()    # begin to solve the linear programming

for (s,t) in demands:
    d = (s,t)
    for e in edges:
        if lp_vars[d,e].value() != 0: print(f"Demand: {d}, edge: {e}, value: {lp_vars[d,e].value()}")

final_demand = dict()
temp_demand = list()
for (u,v) in demands:
    edge_1 = list()
    edge_01 = list()
    d = (u,v)
    for e in edges:
        if lp_vars[d,e].value() == 1: edge_1.append(e)
        elif lp_vars[d,e].value() > 0:
            edge_01.append(e)
    if len(edge_1) > 0 and len(edge_01) == 0:   # all LP variables of the demands are equal to 1
        #print(f"Demand {d}: edge_1 length: {len(edge_1)}, edge_01 length: {len(edge_01)}")
        final_demand[d] = edge_1
    else: temp_demand.append(d)

#print(f"Final demand: {final_demand}")
lptr = open("log.txt",'a')
try:
	path = dict()
	for d in final_demand:
	    path[d] = seperate_path(d,final_demand[d])
	    
	for d in path:
	    #print(path[d])
	    for (u,v) in path[d]:
	        edges.pop(edges.index((u,v)))
	        edges.pop(edges.index((v,u)))
	
	flow = rounding(temp_demand,edges,lp_vars)  # After this step a flow is 0 or 1
	for (u,v) in temp_demand:
	    d = (u,v)
	    print(f"Dealing with demand: {d}")
	    temp_edges = list()
	    for e in edges:
	        if flow[d,e] == 1: temp_edges.append(e)
	    temp_graph = nx.Graph()
	    temp_graph.add_edges_from(temp_edges)
	    if (u in list(temp_graph.nodes())) and (v in list(temp_graph.nodes())):
	        try:
	            temp_path = nx.shortest_path(temp_graph,u,v)
	            #print(f"Demand: {d}, path: {temp_path}")
	            if len(temp_path) <= lmax:
	                path[d] = temp_path
	                for i,j in enumerate(temp_path):
	                    if i < len(temp_path)-1:
	                        edges.pop(edges.index((temp_path[i],temp_path[i+1])))
	                        edges.pop(edges.index((temp_path[i+1],temp_path[i])))
	        except:
	            print("Cannot find the shortest path")
except:
    lptr.write(f"Problem with demand: {d} in set: {demands}")
lptr.close()

print("All the path:")
for d in path:
    print(f"{path[d]}")
rptr = open("result.txt",'a')
rptr.write(f"{len(path)}\n")
rptr.close()