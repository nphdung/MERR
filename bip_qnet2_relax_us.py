#!/usr/bin/python3
# Appoximation Approach using Randomized Rounding
import pulp
from random import random
import numpy as np
from read_network_function import read_graph
import sys

def rounding(demands,edges,flow,lp_vars):
    for d in demands:
        for e in edges:
            #if random() <= lp_vars[d,e].value(): flow[d,e] = 1
            #else: flow[d,e] = 0
            flow[d,e] = np.random.binomial(size=1,n=1,p=lp_vars[d,e].value())[0]
    return flow

graph = "UsCarrier.graphml"
lmax = 8
max_rounding = 500

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

fptr = open("log.txt",'w')
flow = dict()
for d in demands:
    for e in edges: flow[d,e] = 0
# Begin rounding and check
#flow = rounding(demands,edges,flow,lp_vars)
#for d in demands:
#    for e in edges: fptr.write(f"Flow {d}, edge {e}: {lp_vars[d,e].value()}\t\t{flow[d,e]}\n")
cnt = 0
tmp_demands = demands
tmp_edges = edges
while True:
    cnt = cnt+1
    if (cnt >= max_rounding):
        demands.pop()
        cnt = 0
        continue
    #print(f"The number of loop: {cnt}")
    #if cnt == 10: break
    fptr.write("***** RANDOMIZED ROUNDING *****\n")
    # Stage: Rounding
    flow = rounding(tmp_demands,tmp_edges,flow,lp_vars)
    for d in demands:
        for e in edges:
            if lp_vars[d,e].value() != 0: fptr.write(f"Demand: {d}, edge: {e}, flow: {lp_vars[d,e].value()}, rounding: {flow[d,e]}\n")
 
    flag = 0    # reset flag, which inform the violation
    
    # Stage: verification
    # Check the first constraint
    tmp_demands = list()
    tmp_edges = list()
    for (u,v) in u_edges:
        temp = 0
        temp = sum([flow[d,(u,v)] for d in demands]) + sum([flow[d,(v,u)] for d in demands])
        if temp > 1:
            #print(f"Edge ({u},{v}) is not ok")
            tmp_demands = demands
            tmp_edges.append((u,v))
            tmp_edges.append((v,u))
            flag = 1
            break
        #else: print(f"Edge ({u},{v}) is ok")
    if flag == 1: continue

    # Check the second constraint
    for v in nodes:
        for d in demands:
            if v not in d:
                temp_1 = list()
                temp_2 = list()
                temp = 0
                tmp_edges = list()
                for (u,w) in edges:
                    if (u == v):
                        temp_1.append(flow[d,(u,w)])
                        temp_2.append(flow[d,(w,u)])
                        tmp_edges.append((u,w))
                        tmp_edges.append((w,u))
                temp = sum(temp_1) - sum(temp_2)
                if temp != 0:
                    #print(f"Demand: {d}, Node: {v} is not ok")
                    flag = 1
                    tmp_demands.append(d)
                    break
                #else: print(f"Demand: {d}, Node: {v} is ok")
        if flag == 1: break
    if flag == 1: continue

    # Check the third constraint
    for (u,v) in demands:
        tmp_edges = list()
        temp_1 = list()
        temp = 0
        for e in edges:
            if e[0] == u:
                tmp_edges.append(e)
                temp_1.append(flow[(u,v),e])
        temp = sum(temp_1)
        if temp > 1:
            tmp_demands.append((u,v))
            flag = 1
            break
    if flag == 1: continue

    # Check the forth constraint: Not need to check due to assigning directly
    # Check the fifth constraint
    for d in demands:
        temp = sum([flow[d,e] for e in edges])
        if temp > lmax:
            tmp_edges = edges
            tmp_demands.append(d)
            flag = 1
            break
    if flag == 1: continue
    break
fptr.close()

m_demands = list()  # list of met demand
for (s,t) in demands:
    d = (s,t)
    #print(f"\nDemand {d}: ",end="")
    temp = s
    temp_list = list()
    path = list()
    for e in edges:
        if flow[d,e] == 1:
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
        else:
            print(f"\nERROR: The sink is not right")
            fptr.write("SOMETHING WRONG WITH THIS DEMAND\n")
    else:
        if temp == t:
            print(f"{temp}")
            path.append(temp)
        print("\nWARNING: There exist cycles") # The cycles do not affect the solutions
        print(f"\nThe remain edges in the list: ",end="")
        for e in temp_list:
            print(f"{e} ",end="")

    #fptr.write(f"Demand: {d}\tlength: {len(path)-1}\tpath: {path}\n")
    m_demands.append(d)
print(f"The number of satisfied demands: {len(m_demands)}")
rptr = open("result.txt",'a')
rptr.write(f"{len(m_demands)}\n")
rptr.close()