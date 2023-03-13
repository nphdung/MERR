#!/usr/bin/python3
run_num = 100
fptr = open("result.txt",'r')
aptr = open("aggregation.txt",'w')
result = fptr.read()
result = result.split('\n')
result.pop()
result_num = [float(i) for i in result]
if len(result_num) != run_num: print("The number of running is mismatched")
else:
    avr = sum(result_num)/run_num

    aptr.write(f"{avr}\n")
#i = 0
#for r in range(2,21):
#    temp_sum = 0
#    for j in range (run_num):
#        temp_sum = temp_sum + int(result[run_num*i+j])
#    avr = temp_sum/(r*run_num)
#    i = i+1
#    aptr.write(f"{r}\t{avr}\n")
aptr.close()
fptr.close()
#for i,j in enumerate(result):
#    print(f"{i}\t{j}\n")
#fptr.close()
