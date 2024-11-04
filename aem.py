import argparse
import os
import numpy
import matplotlib.pyplot as pyplot

parser = argparse.ArgumentParser()
parser.add_argument('--project',help='Project root folder')
parser.add_argument('--wstk',help='Serial number of WSTK to perform AEM')
parser.add_argument('--csv',default='aem.csv',help='Datafile')
parser.add_argument('--duration',type=float,default=0.1,help='Duration of AEM sampling (s)')
parser.add_argument('--trigger',type=float,default=0,help='Trigger level (mA)')
args = parser.parse_args()

def get_lines(file) :
    fh = open(file,'r')
    text = fh.read()
    fh.close()
    return text.split('\n')

def smooth(value,width) :
    x = numpy.linspace(-5,5,10*width)
    y = numpy.exp(-x*x)
    y /= y.sum()
    r = numpy.convolve(value,y)
    print(len(r),len(y),len(value))
    return r[5*width:][:len(value)]
    
command = 'commander aem dump -s %s -o %s --duration %.1f'%(args.wstk,args.csv,args.duration)
if args.trigger > 0 :
    command += ' --triggerabove %.3f'%(args.trigger) 
print('Running "%s"'%(command))
os.system(command)
lines = get_lines(args.csv)

us = []
V = []
mA = []
got_header = False
for line in lines :
    if 0 == len(line) : continue
    tokens = line.split(',')
    if 3 != len(tokens) :
        raise RuntimeError(line)
    if 'Timestamp' == tokens[0][:9] :
        got_header = True
        continue
    us.append(int(tokens[0]))
    mA.append(float(tokens[1]))
    V.append(float(tokens[2]))

us = numpy.array(us)
mA = numpy.array(mA)
V = numpy.array(V)

if 0 == args.trigger :
    print('Mean: %.3f mA'%(mA.mean()))
    print('Range: %.1f - %.1f mA'%(mA.min(),mA.max()))
    quit()

ms = 1e-3*(us-us[0])
pyplot.plot(ms,mA)
pyplot.show()

fh = open('current.data','w')
for i in range(len(ms)) :
    fh.write('%f\t%f\n'%(ms[i],mA[i]))
fh.close()
