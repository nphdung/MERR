#!/usr/bin/python3
import networkx as nx
from itertools import islice
import sys
from read_network_function import read_graph
from timer import Timer

surfnet_graph = "Surfnet.graphml.xml"
uscarrier_graph = "UsCarrier.graphml"
lmax = 8

# reading graph by using default reading graph networkx type GRAPHML
# def read_graphml(filepath):
#     gr = nx.read_graphml(filepath)
#     return gr

# # transform from undirected to directed graph
# def undirected_to_directed(gru):
#     grd = gru.to_directed()
#     return grd

# list nodes and Edges
def print_graph_info(gr):
    print (len(gr.nodes))
    print (list(gr.nodes))
    print (len(gr.edges))
    print (list(gr.edges))

def read_demand(filepath):
    f = open(filepath, "r")
    lines = f.readlines()

    demands = []
    # Strips the newline character
    for line in lines:
        data=line.strip().split()
        demand = (int(data[0]), int(data[1]))
        demands.append(demand)
    
    return demands

def read_demand_new(filepath):
    f = open(filepath, "r")
    lines = f.readlines()
    l_demand = list()
    lines = lines[0].strip().split(' ')
    for i in lines:
        j = i.strip()
        j = j.replace('(','').replace(')','')
        j = j.split(',')
        l_demand.append((int(j[0]),int(j[1])))
    demands = l_demand
    return demands

def build_residual_graph(grd, path):
    for i in range(len(path) - 1) :
        grd.remove_edge(path[i], path[i+1])
        grd.remove_edge(path[i+1], path[i])
    return grd

def path_strategy_demand_order(grd, demands):
    print (len(demands), "demands:", demands)
   
    sh_pa_len = []
    for i in range(len(demands)):
        sh_pa_len.append(0)

    sh_pa_list = []
    for i in range(len(demands)):
        sh_pa_list.append(0)
        
    act_graph = grd
    i = 0
    while i < len(demands):
        try:
            # source = demands[len(demands)-i-1][0]
            # target = demands[len(demands)-i-1][1]
            source = demands[i][0]
            target = demands[i][1]
            sh_pa = nx.shortest_path(act_graph,source,target)
            sh_pa_len[i] = len(sh_pa)
            sh_pa_list[i] = sh_pa
            # print (sh_pa)
            act_graph = build_residual_graph(act_graph, sh_pa)
        except:
            sh_pa_len[i] = 0
            sh_pa_list[i] = 0
        #increase by 1
        i = i + 1

    return sh_pa_list, sh_pa_len

def path_strategy_shortest_path_length_order(DG, demands):
    print (len(demands), "demands:", demands)
   
    sh_pa_len = []
    sh_pa_list = []
    for i in range(len(demands)):
        sh_pa_len.append(0)
        sh_pa_list.append(0)

    sh_pa_len_lc = []
    sh_pa_list_lc = []
    act_graph = DG
   
    ful_dem = set()
    done = True

    # find all shortest path on each demand
    while ((len(ful_dem) < len(demands))):
        sel_ind = -1
        min_sh_path_len = sys.maxsize
        sh_pa_len_lc.clear()
        sh_pa_list_lc.clear()
        for i in range(len(demands)):
            sh_pa_len_lc.append(0)
            sh_pa_list_lc.append(0)
        
        i = 0
        while i < len(demands):
            if (i in ful_dem):
                i = i + 1
                continue
            
            source = demands[i][0]
            target = demands[i][1]
            try:
                sh_pa_list_lc[i] = nx.shortest_path(act_graph,source,target)
                #print ("sh_pa_list_lc: ", i, sh_pa_list_lc)
                sh_pa_len_lc[i] = len(sh_pa_list_lc[i])
                if (sh_pa_len_lc[i] > lmax + 1):
                    sh_pa_len_lc[i] = 0
                    ful_dem.add(i)
                    print ("ful_dem: ", ful_dem)
                    i = i + 1
                elif (min_sh_path_len > sh_pa_len_lc[i]):
                    min_sh_path_len = sh_pa_len_lc[i]
                    sel_ind = i
            
            except:
                sh_pa_len_lc[i] = 0
                ful_dem.add(i)
                print ("ful_dem: ", ful_dem)
                i = i + 1
            #increase by 1
            i = i + 1
        if sel_ind >= 0 :
            # Select index demand (sel_ind) with min_sh_path
            sh_pa_len[sel_ind] = sh_pa_len_lc[sel_ind]
            sh_pa_list[sel_ind] = sh_pa_list_lc[sel_ind]
            act_graph = build_residual_graph(act_graph, sh_pa_list_lc[sel_ind])
            ful_dem.add(sel_ind)
            print ("ful_dem: ", ful_dem)
           
    return sh_pa_list, sh_pa_len

#main function
def main():
    running_time = Timer()
    running_time.start()
    (DG,UG) = read_graph(surfnet_graph) # DG: directed graph, UG: undirected graph
    print("---Running with lmax: ", lmax)
    print (DG, UG)
    #(DG,UG) = read_graph(uscarrier_graph) # DG: directed graph, UG: undirected graph
    # print_graph_info(grd)

    # get demands
    # demands = read_demand("demand.txt")

    l_argv = sys.argv
    if len(l_argv) == 1:
        demands = read_demand_new("demand.txt")
    else: 
        l_argv.pop(0)
        l_demand = list()
        for i in l_argv:
            j = i.strip()
            j = j.replace('(','').replace(')','')
            j = j.split(',')
            l_demand.append((int(j[0]),int(j[1])))
        demands = l_demand
   
    # sh_pa_list, sh_pa_len = path_strategy_demand_order(grd, demands)
    # total_path = sum(i > 0 for i in sh_pa_len)
    # print ("List shortest path: ")
    # i = 0
    # for i in range(len(sh_pa_list)):
    #     print("Demands:" ,demands[i], "---", sh_pa_list[i])
    # print ("List shortest path length: ", sh_pa_len)
    # print ("Total path: ", total_path)
    # print ("maximum: ", max(sh_pa_len))

    sh_pa_list, sh_pa_len = path_strategy_shortest_path_length_order(DG, demands)
    total_path = sum(i > 0 for i in sh_pa_len)
    print ("List shortest path: ")
    
    for i in range(len(sh_pa_list)):
        print("Demands:" , i, ":", demands[i], "---", sh_pa_list[i])
    print ("List shortest path length: ", sh_pa_len)
    print ("maxmum: ", max(sh_pa_len))
    print ("Total path: ", total_path)
    print ("Maximum: ", max(sh_pa_len))
    running_time.stop()
    return total_path

if __name__ == "__main__":
    main()