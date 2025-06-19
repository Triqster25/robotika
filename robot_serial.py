# robot_serial.py
import serial
ser = serial.Serial("COM7", 115200, timeout=0.1)
def act(cmd):
    ser.write(cmd.encode())   # kirim satu huruf
