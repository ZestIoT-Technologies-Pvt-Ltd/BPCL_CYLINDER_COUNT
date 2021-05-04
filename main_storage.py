#   Copyright (C) 2020 by ZestIOT. All rights reserved. The information in this 
#   document is the property of ZestIOT. Except as specifically authorized in 
#   writing by ZestIOT, the receiver of this document shall keep the information
#   contained herein confidential and shall protect the same in whole or in part from
#   disclosure and dissemination to third parties. Disclosure and disseminations to 
#   the receiver's employees shall only be made on a strict need to know basis.
"""
User Requirement:
1) Counting the number of cylinders from the truck arrived and seggregating them into 14.2kgs, 19kgs and 5kgs as per their size and shape.

Requirements:
1) This function loads the darknet image object, loaded network(darknet object), class name(darknet onject)
2) It also takes the live feed from the respective cameras of top and side view.
3) it will take the frames of the live video and pass it to the top,side and truck entry methods for further processing.
4) upon the arrival of every new truck at unloading point, a new video storage starts and once the truck is left we will close and save the video
   with the start timestamp,

"""

import cv2
import os
import json
from threading import Thread
import side
import top
import truck
import tracker_model
import csv
from datetime import datetime
from datetime import timedelta
import time
from csv import DictWriter 

import copy
import socket
import sys
import pika
from PIL import Image
import io
import numpy as np

"""

Read the camera url stored in BPCL_config.json file

Cam1(Camera1) gives us the side view and Cam2(Camer2) gives the top view.
"""

field_names = ['Vehicle Number','Arrival Timestamp','Departure Timestamp','14Kg Cylinders','19Kg Cylinders','5kg Cylinders','Total Caps','Total Cylinders'] 
config="BPCL_config.json"
with open(config) as json_data:
	try:
		info=json.load(json_data)
		cam1,cam2= info["camera1"],info["camera2"] 
	except Exception as e:
		print(str(e))

class camera():

	def __init__(self, src=0):
		# Create a VideoCapture object
		self.capture = cv2.VideoCapture(src)

		# Take screenshot every x seconds
		self.screenshot_interval = 1

		# Default resolutions of the frame are obtained (system dependent)
		self.frame_width = int(self.capture.get(3))
		self.frame_height = int(self.capture.get(4))

		# Start the thread to read frames from the video stream
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True
		self.thread.start()

	def update(self):
		# Read the next frame from the stream in a different thread
		while True:
			if self.capture.isOpened():
				(self.status, self.frame) = self.capture.read()

	def get_frame(self):
		# Display frames in main program
		if self.status:
			#self.frame = cv2.resize(self.frame, (640,480))
			return self.frame


#loc= "side_output.mp4"
#out=cv2.VideoWriter( loc, cv2.VideoWriter_fourcc(*'XVID'), 10, (1280,480))

try:
	pp = str(datetime.now())[0:19].replace('-','') # Takes the system timestamp to name the videos
	pp = pp.replace(' ','')
	pp = pp.replace(':','')
	path = "cyl_output_videos/"+pp +".mp4"
	#print("pp",path)
	out=cv2.VideoWriter( path, cv2.VideoWriter_fourcc(*'MP4V'), 20, (1280,480))
except Exception as e:
		print(str(e))

write_path ="cyl_csv_files/"+pp+".csv"

with open(write_path, 'wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)


field_names = ['Vehicle Number','Arrival Timestamp','Departure Timestamp','14Kg Cylinders','19Kg Cylinders','5kg Cylinders','Total Caps','Total Cylinders']
with open(write_path, 'w') as f_object:
    dictwriter_object = csv.DictWriter(f_object, fieldnames=field_names)
    dictwriter_object.writeheader()


web_image = 0

def webBrowser_frame():
	global web_image
	try:
		print("h1l0")
		ret, jpeg = cv2.imencode('.jpg', web_image)
		return jpeg.tobytes()

	except:
		return None



def write_data_csv(dict):
	with open(write_path, 'a') as f_object: 
		dictwriter_object = csv.DictWriter(f_object, fieldnames=field_names) 
		dictwriter_object.writerow(dict)
		f_object.close()


frame_count1 = 0
frame_count2 = 0

def arrival_depart(departure_mins,split_file):

	split_file = str(split_file)

	year = str(split_file[0:4])
	month = str(split_file[4:6])
	date = str(split_file[6:8])
	hour = str(split_file[8:10])
	mins = str(split_file[10:12])
	secs = str(split_file[12:14])

	#print(year,month,date,hour,mins,secs)
	#print("h1")
	arrival_timestamp = year+"-"+month+"-"+date+" "+hour+":"+mins+":"+secs
	#print(arrival_timestamp)
	#print("h2")
	pattern = '%Y-%m-%d %H:%M:%S'
	epoch = int(time.mktime(time.strptime(arrival_timestamp, pattern)))
	#print(epoch)

	departure_mins = departure_mins * 60
	#print(departure_mins)
	#print("h3")

	ts_epoch = epoch+departure_mins
	#print("h4")
	depart_timestamp = datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d %H:%M:%S')
	#print(depart_timestamp)
	#print(arrival_timestamp)
	return arrival_timestamp,depart_timestamp


def send_image(conn):
	img1 = Image.open('image1.jpg', mode='r')
	imgByteArr = io.BytesIO()
	#print(type(img1))
	img1.save(imgByteArr, format=img1.format)
	imgByteArr = imgByteArr.getvalue()
	#print(imgByteArr)
	conn.send(imgByteArr)
	ack = conn.recv(50 * 1024)
	#print(ack,'1')


if __name__ == '__main__':
		try:
			#darknet_image_L,network_L,class_names_L=tracker_model.load_model_truck()
			darknet_image_S,network_S,class_names_S=tracker_model.load_model_side()
			darknet_image_T,network_T,class_names_T=tracker_model.load_model_top()

			
			arrival_timestamp = datetime.now()
			departure_timestamp = datetime.now()
			outWrite_flag = False
			truck_entry = False
			truck_exit = False

			try:
				TCP_HOST, TCP_PORT = 'localhost', 10001
				bpcl_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				bpcl_server.bind((TCP_HOST, TCP_PORT))
				bpcl_server.listen(5)
				(connection, (client_address, port)) = bpcl_server.accept()
				#send(connection)
			except Exception as e_:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				print("except in pika " + str(e_) + ' ' + str(exc_tb.tb_lineno))



			while  True:
				try:
					files = os.listdir("cylinder_storage/top_view")
					#print(files)
					sorted_files = sorted(files)
					#print(sorted_files)
					#print(sorted_files[0])
					first_file = sorted_files[0]
					top_file = "cylinder_storage/top_view"+"/"+first_file
					#print("h1") 
					side_file = "cylinder_storage/side_view"+"/"+first_file
					#print("h2") 
	    			#file_sorted = "graph_plots/"+str(first_file)
					split_file = first_file.split(".")
					split_file = split_file[0]
					cam1 = cv2.VideoCapture(side_file)
					time.sleep(1)
					cam2 = cv2.VideoCapture(top_file)
					time.sleep(1)

					frames = cam2.get(cv2.CAP_PROP_FRAME_COUNT)
					fps = int(cam2.get(cv2.CAP_PROP_FPS))
  
					# calculate dusration of the video
					seconds = int(frames / fps)
					video_time = str(timedelta(seconds=seconds))
					#print("duration in seconds:", seconds)
					#print("video time:", video_time)
					secs_to_mins = float(seconds/60)
					arrival_timestamp,departure_timestamp = arrival_depart(secs_to_mins,split_file)
					#print("arrival and departure",arrival_timestamp,departure_timestamp)
					#print("truck_entry",truck_entry)
					#print(split_file)
					path = "cyl_output_videos/"+split_file +".mp4"
					#print("pp",path)
					out=cv2.VideoWriter( path, cv2.VideoWriter_fourcc(*'MP4V'), 20, (1280,480))
					#print('new_video')
					cyl_14,cyl_19,cyl_5,total_cyl,total_cap = 0,0,0,0,0
					cyl_14_exit,cyl_19_exit,cyl_5_exit,total_cyl_exit,total_cap_exit = 0,0,0,0,0
					truck_entry = True
					while True:
							try:
								loop_start_time = datetime.now()

								ret1,img1 = cam1.read()
								ret2,img2 = cam2.read()
								#print("Start_time",time.localtime())

								if ret1 == True and ret2 == True:
									img1 = cv2.resize(img1,(640,480))
									img2 = cv2.resize(img2,(1920,1080))

									side_img,cyl_14,cyl_19,cyl_5,total_cyl = side.side_model(img1,darknet_image_S,network_S,class_names_S,truck_entry)
									top_img,total_cap, truck_entry, truck_exit = top.top_model(img2,darknet_image_T,network_T,class_names_T,truck_entry)
									side_img = cv2.resize(side_img, (640,480))
									top_img = cv2.resize(top_img, (640,480))
									concat_img = cv2.hconcat([side_img, top_img])
									#cv2.imshow('output',concat_img)
									#web_image = concat_img
									out.write(concat_img)
									output_image = "image1"+".jpg"
									cv2.imwrite(output_image, concat_img)
									send_image(connection)
									truck_entry = False
										
									loop_end_time = datetime.now()
									if cv2.waitKey(1) & 0xff == ord('q'):
										break
								else:
									break
							except Exception as e:
								print("Error in Main loop:",str(e))
							
					
					cyl_14_exit = cyl_14
					cyl_19_exit = cyl_19
					cyl_5_exit = cyl_5
					total_cyl_exit = total_cyl
					total_cap_exit = total_cap
					Truck_Number = "TS08FM0002"
					dict = {'Vehicle Number':Truck_Number,'Arrival Timestamp':arrival_timestamp,'Departure Timestamp':departure_timestamp,'14Kg Cylinders':cyl_14_exit,'19Kg Cylinders':cyl_19_exit,'5kg Cylinders':cyl_5_exit,'Total Caps':total_cap_exit,'Total Cylinders':total_cyl_exit}
					write_data_csv(dict)
					cam1.release()
					cam2.release()
					out.release()
					try:
						os.remove(top_file)
						os.remove(side_file)
						#print("removed files")
					except:
						pass
				except Exception as e:
					print("Error in Main1 File:",str(e))
					try:
						os.remove(top_file)
						os.remove(side_file)
						#print("removed files")
					except:
						continue
		except Exception as e:
			print("Error in Main File:",str(e))

