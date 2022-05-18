

import serial
import math
import socket
import buzzer

previousFl = 0
previousBr = 0

#socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket.bind(('',8669))
ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)
ser.reset_input_buffer()

pallier = 6

def decrypt(string):
    if string is not None:
        if len(string) == 2:
            pallier = int(string[1])
            klaxon = int(string[0])
            if klaxon == 1:
                buzzer.bip()
            return 1, [pallier, klaxon]
        elif string[0] == "[" :
            response = string.split(",")
            x = int(float(response[0][1:]))
            y = int(float(response[1][:-1]))
	    signX = 1
	    signY = 1
            if x > 180 :
		x = x - 360
		signX = -1
       	    if y > 180 :
		y = y - 360
		signY = -1
            x = x*4
            y = y*4
	    if abs(x)>180:
  		x = 180*signX
 	    if abs(y)>180:
		y = 180*signY
            print(x)
	    print(y)
            return 0,[x,y]
        elif string[0] == "?" :
            angle = float(string[1:])*math.pi/180
            y = int(math.sin(angle) * 180)
            x = int(math.cos(angle) * 180)
            return 0, [x,y]
        else :
            return 2,"nothing"
    else :
        return 3, "nothing"

def speedmotor(list,pallier,previousFl,previousBr):
    angleX = list[0]
    angleY = list[1]

    if 20 >= angleX >= -20:
        angleX = 0
    if 20 >= angleY >= -20:
        angleY = 0

    signX = 1
    if angleX >= 0:
        signX = -1

    signY = -1
    if angleY >= 0:
        signY = 1

    if angleX != 0 and angleY != 0:
        angle = math.atan(abs(angleX)/abs(angleY))
        vectorIntensity = math.sqrt((angleX**2) + (angleY ** 2))
        if vectorIntensity > 180:
            vectorIntensity = 180
        speedX = math.sin(angle) * vectorIntensity * 255/180
        speedY = math.cos(angle) * vectorIntensity * 255/180
        while speedY + speedX > 255:
            speedX = speedX * 0.98
            speedY = speedY * 0.98
    else :
        speedX = abs(angleX) * 255/180
        speedY = abs(angleY) * 255/180
    dico = { 0:0,1:0.7,2:1}
    speedX = speedX * signX * dico[(pallier//3)]
    speedY = speedY * signY * dico[(pallier//3)]
    fl = int(((speedX - speedY)))#+previousFl)/2)
    br = int(((speedX + speedY)))#+previousBr)/2)
    previousFl = fl
    previousBr = br
    return "["+str(fl)+","+str(br)+","+str(br)+","+str(fl)+"]", previousFl, previousBr

while True:
    ser.reset_input_buffer()
    #socket.listen(5)
    #client, adress = socket.accept()
    response = input("entrer")
    if response != "":
        command = response #.decode()
	print(command)
        state, data = decrypt(command)
        if state == 0:
            speed,newpreviousFl, newpreviousBr = speedmotor(data,pallier,previousFl, previousBr)
            if newpreviousFl == previousFl and newpreviousBr == previousFl:
                pass
            else:
                previousFl = newpreviousFl
                previousBr = newpreviousBr
                ser.write(speed.encode())
        elif state == 1:
            pallier = data[0]
            if pallier == 0:
                speed = "[0,0,0,0]"
                ser.write(speed.encode())
        elif state == 3:
            ser.write(speed.encode())
        else :
            pass

client.close()
socket.close()
