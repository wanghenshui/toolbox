import csv
import sys

CPU_METRIC=int(sys.argv[2])
file=sys.argv[1]

with open(file, "r") as csvFile:
    reader = csv.reader(csvFile)
    count=usr=per=0
    cpudata = ['Date,Time,CPU,%user,%nice,%system,%iowait,%steal,%irq,%soft%,guest%,%gnice,%idle\n']
    for item in reader:
        count=count+1
        if reader.line_num == 1:
            continue

        if float(item[3]) >= CPU_METRIC:
            usr=usr+1
            cpudata=cpudata+list(','.join(item))+['\n']
    per = (float) (usr) / count
    if per > 0.0:
        with open(file+'_cpu_metric_abnormal.txt',"w") as f:
            f.write(file+" cpu.csv metric is "+ str(per)+'\n')
            for s in cpudata:
                f.write(s)

