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
import time
from csv import DictWriter 

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
	print("pp",path)
	out=cv2.VideoWriter( path, cv2.VideoWriter_fourcc(*'MP4V'), 10, (1280,480))
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

if __name__ == '__main__':
		try:
			#darknet_image_L,network_L,class_names_L=tracker_model.load_model_truck()
			darknet_image_S,network_S,class_names_S=tracker_model.load_model_side()
			darknet_image_T,network_T,class_names_T=tracker_model.load_model_top()
			#cam1 = camera(cam1)
			#time.sleep(1)
			#cam2 = camera(cam2)
			#time.sleep(1)
			cam1 = cv2.VideoCapture('rtsp://admin:bpcl1234@192.168.55.183:554')
			time.sleep(1)
			cam2 = cv2.VideoCapture('rtsp://admin:bpcl1234@192.168.55.182:554/ch01_265')
			time.sleep(1)
			#cam1 = cv2.VideoCapture("Side.mp4")
			#cam2 = cv2.VideoCapture("Top.mp4")
			cyl_14,cyl_19,cyl_5,total_cyl,total_cap = 0,0,0,0,0
			cyl_14_exit,cyl_19_exit,cyl_5_exit,total_cyl_exit,total_cap_exit = 0,0,0,0,0
			arrival_timestamp = datetime.now()
			departure_timestamp = datetime.now()
			outWrite_flag = False
			truck_entry = False
			truck_exit = False
			while True:
					try:
						loop_start_time = datetime.now()
						#frame_count1+=1
						ret1,img1 = cam1.read()
						#if((frame_count1 % 2) != 0):
							#continue
						#frame_count1 = 0

						img1 = cv2.resize(img1,(640,480))
						frame_count2+=1
						ret2,img2 = cam2.read()
						if((frame_count2 % 2) != 0):
							continue

						frame_count2 = 0

						img2 = cv2.resize(img2,(1920,1080))
						#img22 = cv2.resize(img22,(1280,720))
						#if ret1 and ret2 is True:
						print("Start_time",time.localtime())

						if truck_entry == True:
							cyl_14_exit = cyl_14
							cyl_19_exit = cyl_19
							cyl_5_exit = cyl_5
							total_cyl_exit = total_cyl
							total_cap_exit = total_cap
						side_img,cyl_14,cyl_19,cyl_5,total_cyl = side.side_model(img1,darknet_image_S,network_S,class_names_S,truck_entry)
						top_img,total_cap, truck_entry, truck_exit = top.top_model(img2,darknet_image_T,network_T,class_names_T,truck_entry)
						side_img = cv2.resize(side_img, (640,480))
						top_img = cv2.resize(top_img, (640,480))
						concat_img = cv2.hconcat([side_img, top_img])
						cv2.imshow('output',concat_img)
						#web_image = concat_img
						if truck_entry == True:
							print("truck_entry",truck_entry)
							pp = str(datetime.now())[0:19].replace('-','')
							pp = pp.replace(' ','')
							pp = pp.replace(':','')
							path = "cyl_output_videos/"+pp +".mp4"
							print("pp",path)
							out=cv2.VideoWriter( path, cv2.VideoWriter_fourcc(*'MP4V'), 10, (1280,480))
							print('new_video')
							Truck_Number = "TS08FM0002"
							dict = {'Vehicle Number':Truck_Number,'Arrival Timestamp':arrival_timestamp,'Departure Timestamp':departure_timestamp,'14Kg Cylinders':cyl_14_exit,'19Kg Cylinders':cyl_19_exit,'5kg Cylinders':cyl_5_exit,'Total Caps':total_cap_exit,'Total Cylinders':total_cyl_exit}
							write_data_csv(dict)
							arrival_timestamp = datetime.now()
							outWrite_flag = True
						if outWrite_flag == True:
							out.write(concat_img)
						if truck_exit == True :
							out.release()
							print('video_end')
							departure_timestamp = datetime.now()
							outWrite_flag = False
							
						loop_end_time = datetime.now()

						#while(int((loop_end_time - loop_start_time).total_seconds()*1000) < 100 ):
							#loop_end_time = datetime.now()
						if cv2.waitKey(1) & 0xff == ord('q'):
							break
					except Exception as e:
						print("Error in Main loop:",str(e))
					
			#cam1.release()
			#cam2.release()
			out.release()
		except Exception as e:
			print("Error in Main File:",str(e))

