#!/usr/bin/python3
import sys
run_num = 100
r_file = sys.argv
r_file.pop(0)
fptr = open(r_file[0],'r')
aptr = open("aggregation_"+r_file[0],'w')
result = fptr.read()
result = result.split('\n')
result.pop()
i = 0
for r in range(2,21):
    temp_sum = 0
    for j in range (run_num):
        temp_sum = temp_sum + int(result[run_num*i+j])
    avr = temp_sum/(run_num)
    i = i+1
    aptr.write(f"{r}\t{avr}\n")
aptr.close()
fptr.close()
#for i,j in enumerate(result):
#    print(f"{i}\t{j}\n")
#fptr.close()
