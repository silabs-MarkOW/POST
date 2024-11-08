import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--project',help='Project root folder',required=True)
parser.add_argument('--xref',help='File containing UART output',required=True)
parser.add_argument('--saleae',default='digital.csv',help='CSV from saleae',required=True)
parser.add_argument('--above',type=float,default=0,help='Lower limit (s)')
parser.add_argument('--current',help='AEM current data file')
parser.add_argument('--duration',type=float,help='Plot duration (ms)')
parser.add_argument('--offset',type=float,default=.63,help='Plot offset (ms)')
parser.add_argument('--em4wake',action='store_true',help='Saleae Ch8 is connected to EM4wake button, t=0 at falling edge, default is t=0 at rising edge of RESET')
parser.add_argument('--debug',action='store_true',help='print random internals')
args = parser.parse_args()

def get_lines(file) :
    fh = open(file,'r')
    text = fh.read()
    fh.close()
    return text.split('\n')

def get_functions(lines) :
    db = {}
    functions = []
    for line in lines :
        tokens = line.split(':')
        if len(tokens) != 3 : continue
        index = int(tokens[0])
        line = int(tokens[1])
        if '../' != tokens[2][:3] :
            raise RuntimeError(line)
        path = tokens[2][3:]
        source_lines = db.get(path)
        if None == source_lines :
            if '/' == args.project[-1] :
                source_file = args.project + path
            else :
                source_file = args.project + '/' + path
            source_lines = get_lines(source_file)
            db[path] = source_lines
        function = source_lines[line].strip()
        if len(function) > 0 and ';' == function[-1] :
            function = function[:-1]
        if args.debug: print(index,function)
        functions.append(function)
    return functions

def extract(line) :
    tokens = line.split(',')
    time = float(tokens[0])
    acc = 0
    for index in range(7) :
        value = int(tokens[1+index])
        acc += (value << index)
    reset = '0' == tokens[8]
    if args.em4wake :
        reset = not reset
    return time,acc,reset

def pretty(t) :
    if t < 1e-6 :
        return '%.0f ns'%(1e9*t)
    if t < 1e-3 :
        return '%.1f us'%(1e6*t)
    if t < 1 :
        return '%.1f ms'%(1e3*t)
    return '%.1f'%(t)

start_stop = {}
labels = get_functions(get_lines(args.xref))
previous_state = -1
label = {}

def push(state, start, stop) :
    if state < previous_state :
        raise RuntimeError('state %d < previous %d'%(state,previous_state))
    delta = stop - start
    if args.debug: print("push:",state,start,stop,delta)
    if delta < 10e-9 :
        if args.debug: print('Ignore')
        return
    start_stop[state] = (start,stop)
    label[state] = '%d %s'%(state,pretty(delta))

lines = get_lines(args.saleae)
start_time,state,reset = extract(lines[1])
offset = 0
got_zero = False
for line in lines[2:] :
    if 0 == len(line) : continue
    now,next_state,reset = extract(line)
    if reset :
        offset = now + 1.4e-3
        if args.debug: print('offset: %f'%(offset*1e3))
        continue
    if args.em4wake and not got_zero :
        if 0 == next_state :
            got_zero = True
            state = 0
            print("got zero")
        continue
    if state != next_state :
        push(state,start_time-offset,now-offset)
        state = next_state
    start_time = now
def max_length(lines) :
    max = 0
    for line in lines :
        l = len(line)
        if l > max :
            max = l
    return max

fh = None
if None != args.current :
    fh = open('graph.gnu','w')
    fh.write('ya(i) = 22-2*i\nyl(i) = ya(i+.3)\n')
    fh.write('set xlabel "Time (ms)"\n')
    fh.write('set ylabel "Current (mA)"\n')

format = '%%%ds: %%s'%(max_length(labels))
index = 0
for i in start_stop :
    start,stop = start_stop[i]
    delta = stop-start
    if delta > args.above :
        print(format%(labels[i],pretty(delta)))
        if None != fh :
            start -= 1e-3*args.offset
            stop -= 1e-3*args.offset
            mid = (start + stop)/2
            label = '%s: %s'%(labels[i],pretty(delta))
            label = label.replace('_','\\\\_')
            fh.write('set arrow from %f,ya(%d) to %f,ya(%d) heads\n'%(1e3*start,index,1e3*stop,index))
            fh.write('set label "%s" at %f,yl(%d) center\n'%(label,1e3*mid,index))
            index += 1

if None != fh :
    if None != args.duration :
        stop = 1e-3*args.duration
    fh.write('plot [0:%d] "current.data" with line'%(1e3*stop))
    fh.close()
    os.system('gnuplot -persist graph.gnu')
