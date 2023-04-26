#!/usr/bin/env python
'''
**********************************************************************
* Source code taken from SunFounder, whose credentials are below. This
is for academic and educational purposes only to show what was changed 
during a semester-long class project where I worked with the PiCar-S Smart Car.
* Filename    : line_obsavoidance.py
* Description : An example for sensor car kit to follow lines with obs avoidance
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-10-08    New release
**********************************************************************
'''
from SunFounder_Line_Follower import Line_Follower
from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
from picar import front_wheels
from picar import back_wheels
import time
import picar

picar.setup()

ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
lf = Line_Follower.Line_Follower()
fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')

REFERENCES = [225, 225, 225, 225, 225]
#calibrate = True
calibrate = False
forward_speed = 60
backward_speed = 70
turning_angle = 45

delay = 0.0005

lf.references = REFERENCES
fw.ready()
bw.ready()
fw.turning_max = 45

turning_angle = 30
forward_speed = 40
backward_speed = 50

back_distance = 15
turn_distance = 24

def cali():
	references = [0, 0, 0, 0, 0]
	print("cali for module:\n  first put all sensors on white, then put all sensors on black")
	mount = 100
	fw.turn(70)
	print("\n cali white")
	time.sleep(4)
	fw.turn(90)
	white_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	fw.turn(110)
	print("\n cali black")
	time.sleep(4)
	fw.turn(90)
	black_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	for i in range(0, 5):
		references[i] = (white_references[i] + black_references[i]) / 2
	lf.references = references
	print("Middle references =", references)
	time.sleep(1)

def state_line():
	#print("start_follow")
	global turning_angle
   	global step
	bw.speed = forward_speed

	a_step = 5
	b_step = 12
	c_step = 35
	d_step = 45
	bw.forward()

	while True:
		lt_status_now = lf.read_digtal()
		print(lt_status_now)
		# Angle calculate
		if	lt_status_now == [0,0,1,0,0]:
			step = 0	
		elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
			step = a_step
		elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
			step = b_step
		elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
			step = c_step
		elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
			step = d_step

		# Direction calculate
		If lt_status_now == [0,0,1,0,0]:
			line_flag = 0
			return line_flag
            
		# turn right
		elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
			line_flag = 1
			return line_flag
            
		# turn left
		elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
			line_flag = 2
			return line_flag
            
		# all on white surface
		elif lt_status_now == [0,0,0,0,0]:
			line_flag = 3
			return line_flag
		
def state_sonic():
	#print("start_avoidance")
	distance = ua.get_distance()
	if 0<=distance<back_distance: # backward
		avoid_flag = 2
	elif back_distance<distance<turn_distance : # turn
		avoid_flag = 1
	else:						# forward
		avoid_flag = 0

	print('distance = ',distance)
	return avoid_flag

def stop():
	bw.stop()
	fw.turn_straight()

def main():
	cali()
	while True:
		line_flag = state_line()
		avoid_flag = state_sonic()

		# touch obstruction, backward
		if avoid_flag == 2:	
			bw.backward()
			bw.speed = backward_speed
			print(" touch obstruction")
			time.sleep(1)
			bw.stop()

		# near obstruction, turn
		elif avoid_flag == 1: 
			fw.turn(90 + turning_angle)
			bw.forward()
			bw.speed = forward_speed
			print("  near obstruction")
			time.sleep(1)
			bw.stop()

		# no obstruction, track line
		else:	
			print("   no obstruction, line_flag = ",line_flag)
			if line_flag == 0:		# direction
				fw.turn(90)
				bw.forward()
				bw.speed = forward_speed
			elif line_flag == 1:	# turn right
				fw.turn(90 - step)
				bw.forward()
				bw.speed = forward_speed
			elif line_flag == 2:	# turn left
				fw.turn(90 + step)
				bw.forward()
				bw.speed = forward_speed
			elif line_flag == 3:	# on white 
				if off_track_count > max_off_track_count:
				#tmp_angle = -(turning_angle - 90) + 90
				tmp_angle = (turning_angle-90)/abs(90-turning_angle)
				tmp_angle *= fw.turning_max
				bw.speed = backward_speed
				bw.backward()
				fw.turn(tmp_angle)
				
				lf.wait_tile_center()
				bw.stop()

				fw.turn(turning_angle)
				time.sleep(0.2)
				bw.speed = forward_speed
				bw.forward()
				time.sleep(0.2)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		stop()
