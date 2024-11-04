import serial
import sys

s = serial.Serial(sys.argv[1])
fh = open('post.dump','w')
while True :
    ch = s.read()
    if None != ch :
        if b'\04' == ch :
            break
        ch = ch.decode()
        fh.write(ch)
        print(ch,end='')

fh.close()
s.close()
