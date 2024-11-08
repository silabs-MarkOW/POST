import serial
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--uart',help='WSTK VCOM UART',required=True)
parser.add_argument('--output','-o',help='File to save post_dump() output',required=True)
parser.add_argument('--debug',action='store_true',help='echo data to stdout')
args = parser.parse_args()
print(args)

s = serial.Serial(args.uart)
fh = open(args.output,'w')
while True :
    ch = s.read()
    if None != ch :
        if b'\04' == ch :
            break
        ch = ch.decode()
        fh.write(ch)
        if args.debug: print(ch,end='')

fh.close()
s.close()
