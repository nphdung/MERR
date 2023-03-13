#!/usr/bin/python3
import pulp
from read_network_function import read_graph
import sys

graph = "Surfnet.graphml.xml"
lmax = 8

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
#demands = [(38,23),(33,11),(5,44),(0,14),(1,32),(9,39),(17,24),(24,9),(31,16),(35,8)]
#demands = [(13, 30), (8, 49), (25, 26), (4, 37), (42, 41), (22, 2), (43, 23)]
#demands = [(10, 36), (15, 17), (39, 49), (31, 30), (48, 12), (24, 20), (30, 15), (18, 33), (4, 37), (5, 45), (0, 1)]

# define the LP problem
prob = pulp.LpProblem("Minimax the path length",pulp.LpMinimize)

# define the variables of the problem
vars = list()
for d in demands:
    for e in edges:
        vars.append((d,e))  # should be a list of tuple

#print(f"list of variables: {vars}")
#lp_vars = pulp.LpVariable.dicts("Flow",vars,0,1,cat="Integer")
lp_vars = pulp.LpVariable.dicts("Flow",vars,cat="Binary")
length = pulp.LpVariable("l_max")
#lp_vars = pulp.LpVariable.dicts("Flow",vars,lowBound=0,upBound=1,cat="Continous")   # for relaxation
#print(f"Variables: {lp_vars}")

# the objective function
#temp = list()
#for d in demands:
#    for n in nodes:
#        if (d[0],n) in edges: temp.append((lp_vars[(d,(d[0],n))],1))

#print(f"Objective variables: {temp}")
# Objective function
prob += length

# the first constraint
for (u,v) in u_edges:
    prob += pulp.lpSum([lp_vars[d,(u,v)] for d in demands]) + \
            pulp.lpSum([lp_vars[d,(v,u)] for d in demands]) <= 1

# the second constraint
for v in nodes:
    for d in demands:
        if v not in d:
            temp_1 = list()
            temp_2 = list()
            for (u,w) in edges:
                if (u == v):
                    temp_1.append(lp_vars[d,(u,w)])
                    temp_2.append(lp_vars[d,(w,u)])
            prob += pulp.lpSum(temp_1) - pulp.lpSum(temp_2) == 0

# the third constraint (the constraint at the sources)
for d in demands:
    prob += pulp.lpSum([lp_vars[d,e] for e in edges if (e[0] == d[0])]) == 1

# the forth constraint (the constraint of the inflow at the sources)
for d in demands:
    for (u,v) in edges:
        if u == d[0]: prob += lp_vars[d,(v,u)] == 0

# the fifth constraint (the constraint of the path length)
#for d in demands:
#    prob += pulp.lpSum([lp_vars[d,e] for e in edges]) <= lmax

# the sixth constraint
for d in demands:
    prob += length - pulp.lpSum([lp_vars[d,e] for e in edges]) >= 0

#prob.writeLP("bip_qnet1_maxmin_length.txt")   # log file (use to record the linear program)
prob.solve()    # begin to solve the linear programming
lptr = open("length_min.txt",'a')
lptr.write(f"{int(pulp.value(prob.objective))}")
lptr.write("\n")
lptr.close()
#print("The maximum number of paths: ",pulp.value(prob.objective))
# separate the paths of the demands
#for (s,t) in demands:
#    d = (s,t)
#    print(f"\nDemand {d}: ",end="")
#    temp = s
#    temp_list = list()
#    for e in edges:
#        if lp_vars[d,e].value() == 1:
#            if e[0] == temp:
#                print(f"{temp} ",end="")
#                temp = e[1]
#            else: temp_list.append(e)
#    
#    #if len(temp_list) == 0 and temp == s:
#    if temp == s:
#        print("Cannot satisfy")
#        continue
#    
#    while len(temp_list) > 0:
#        list_length = len(temp_list)
#        for (i,j) in temp_list:
#            if temp == i:
#                id = temp_list.index((i,j))
#                print(f"{temp} ",end="")
#                temp = j
#                temp_list.pop(id)
#        if temp == t or list_length == len(temp_list): break
#
#    if len(temp_list) == 0:
#        if temp == t: print(f"{temp}")
#        else: print(f"\nERROR: The sink is not right")
#    else:
#        if temp == t: print(f"{temp}")
#        print("\nWARNING: There exist cycles") # The cycles do not affect the solutions
#        print(f"\nThe remain edges in the list: ",end="")
#        for e in temp_list:
#            print(f"{e} ",end="")