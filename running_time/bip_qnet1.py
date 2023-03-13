#!/usr/bin/python3
import pulp
from read_network_function import read_graph
import sys
import time

graph = "Surfnet.graphml.xml"
lmax = 8

(DG,UG) = read_graph(graph) # DG: directed graph, UG: undirected graph
nodes = list(DG.nodes)
edges = list(DG.edges)
u_edges = list(UG.edges)

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
#demands = demands = [(42,25), (6,9), (8,20), (25,30), (22,10), (45,42), (14,37), (32,47), (29,20), (12,25), (32,2), (30,38), (9,45), (6,42), (27,35), (26,37), (45,38), (17,9), (47,46), (26,45)]
#demands = demands = [(42,25), (6,9)]
start_time = time.time()
# define the LP problem
prob = pulp.LpProblem("Find the maximum number of satisfied demands",pulp.LpMaximize)

# define the variables of the problem
vars = list()
for d in demands:
    for e in edges:
        vars.append((d,e))  # should be a list of tuple

#lp_vars = pulp.LpVariable.dicts("Flow",vars,0,1,cat="Integer")
lp_vars = pulp.LpVariable.dicts("Flow",vars,cat="Binary")
#lp_vars = pulp.LpVariable.dicts("Flow",vars,lowBound=0,upBound=1,cat="Continous")   # for relaxation

# the objective function
temp = list()
for d in demands:
    for n in nodes:
        if (d[0],n) in edges: temp.append((lp_vars[(d,(d[0],n))],1))

prob += pulp.LpAffineExpression(temp)

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
    prob += pulp.lpSum([lp_vars[d,e] for e in edges if (e[0] == d[0])]) <= 1

# the forth constraint (the constraint of the inflow at the sources)
for d in demands:
    for (u,v) in edges:
        if u == d[0]: prob += lp_vars[d,(v,u)] == 0

# the fifth constraint (the constraint of the path length)
for d in demands:
    prob += pulp.lpSum([lp_vars[d,e] for e in edges]) <= lmax

#prob.writeLP("bip_qnet1.txt")   # log file (use to record the linear program)
prob.solve()    # begin to solve the linear programming
#rptr = open("result.txt",'a')
#rptr.write(f"{int(pulp.value(prob.objective))}\n")
#rptr.close()
# separate the paths of the demands
#fptr = open("history.txt","a")
#fptr.write("***** New set of demands *****\n")
#fptr.write(f"Set of demands: {demands}\n")
m_demands = list()  # list of met demands
for (s,t) in demands:
    d = (s,t)
    #print(f"\nDemand {d}: ",end="")
    temp = s
    temp_list = list()
    path = list()
    for e in edges:
        if lp_vars[d,e].value() == 1:
            if e[0] == temp:
                #print(f"{temp} ",end="")
                path.append(temp)
                temp = e[1]
            else: temp_list.append(e)
    
    #if len(temp_list) == 0 and temp == s:
    if temp == s:
        #print("Cannot satisfy")
        continue
    
    while len(temp_list) > 0:
        list_length = len(temp_list)
        for (i,j) in temp_list:
            if temp == i:
                id = temp_list.index((i,j))
                #print(f"{temp} ",end="")
                path.append(temp)
                temp = j
                temp_list.pop(id)
        if temp == t or list_length == len(temp_list): break

    if len(temp_list) == 0:
        if temp == t:
            #print(f"{temp}")
            path.append(temp)
        #else:
            #print(f"\nERROR: The sink is not right")
            #fptr.write("SOMETHING WRONG WITH THIS DEMAND\n")
    else:
        if temp == t:
            #print(f"{temp}")
            path.append(temp)
        #print("\nWARNING: There exist cycles") # The cycles do not affect the solutions
        #print(f"\nThe remain edges in the list: ",end="")
        #for e in temp_list:
            #print(f"{e} ",end="")

    #fptr.write(f"Demand: {d}\tlength: {len(path)-1}\tpath: {path}\n")
    m_demands.append(d)

#fptr.write(f"Satisfied demands: {m_demands}\n")
#fptr.close()
end_time = time.time()
elapsed_time = end_time - start_time
rptr = open("result.txt",'a')
rptr.write(f"{elapsed_time}\n")
rptr.close()
#print(f"Time:{elapsed_time}")
