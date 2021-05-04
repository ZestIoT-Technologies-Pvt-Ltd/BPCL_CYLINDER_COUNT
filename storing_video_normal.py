import cv2
from threading import Thread
import darknet
from datetime import datetime
import time
import json

config = "BPCL_config.json"
with open(config) as json_data:
	try:
		info = json.load(json_data)
		cam1,cam2 = info["camera1"], info["camera2"]
		configPath_top,weightPath_top,metaPath_top= info["truck"]["configPath"],info["truck"]["weightPath"],info["truck"]["metaPath"]
	except Exception as e:
		print(str(e))

# class camera():
#
# 	def __init__(self, src=0):
# 		# Create a VideoCapture object
# 		self.capture = cv2.VideoCapture(src)
#
# 		# Take screenshot every x seconds
# 		self.screenshot_interval = 1
#
# 		# Default resolutions of the frame are obtained (system dependent)
# 		self.frame_width = int(self.capture.get(3))
# 		self.frame_height = int(self.capture.get(4))
#
# 		# Start the thread to read frames from the video stream
# 		self.thread = Thread(target=self.update, args=())
# 		self.thread.daemon = True
# 		self.thread.start()
#
# 	def update(self):
# 		# Read the next frame from the stream in a different thread
# 		while True:
# 			if self.capture.isOpened():
# 				(self.status, self.frame) = self.capture.read()
#
# 	def get_frame(self):
# 		# Display frames in main program
# 		if self.status:
# 			#self.frame = cv2.resize(self.frame, (640,480))
# 			return self.frame

# try:
# 	pp = str(datetime.now())[0:19].replace('-','') # Takes the system timestamp to name the videos
# 	pp = pp.replace(' ','')
# 	pp = pp.replace(':','')
# 	path1 = "cylinder_storage/side_view/"+pp +".mp4"
# 	#path2 = "cylinder_storage/top_view/"+pp+".mp4"
# 	print("pp",path1)
# 	out1=cv2.VideoWriter( path1, cv2.VideoWriter_fourcc(*'XVID'), 10, (1920,1080))
# 	#out2=cv2.VideoWriter( path2, cv2.VideoWriter_fourcc(*'MP4V'), 10, (1280,480))

# except Exception as e:
# 		print(str(e))

#saving videos

status = 0
entry_check = 0
exit_check = 0
entry_time = 0
exit_time = 0
truck_entry = None
truck_video = False
outwrite_flag = False
#cam1 = camera('rtsp://admin:bpcl1234@192.168.55.183:554')
cam1 = cv2.VideoCapture(cam1)
cam2 = cv2.VideoCapture(cam2)
#cam2 = camera(cam2)
network, class_names, class_colors = darknet.load_network(configPath_top,metaPath_top,weightPath_top,batch_size=1)
darknet_image = darknet.make_image(darknet.network_width(network),darknet.network_height(network),3)
try:
	while True:
		ret, img1 = cam1.read()
		ret1,img2 = cam2.read()
		#img2 = cam2.get_frame()


		if ret1 is True:
			img1 = cv2.resize(img1,(640,480))
			img2 = cv2.resize(img2,(1920,1080))
			#cv2.imshow('output',img1)
			frame_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
			frame_resized = cv2.resize(frame_rgb,(darknet.network_width(network),darknet.network_height(network)),interpolation=cv2.INTER_LINEAR)
			darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
			result=darknet.detect_image(network,class_names,darknet_image, thresh=0.25)
			#len(result) = 0
			# for i,j in enumerate(result):
			#     class_name = j[0]
			# if class_name == 'cap' or class_name == 'cylinder':
			#     continue
			# else:
			#     len(result) = len(result) + 1

			if status == 1 and len(result) > 0 :
				if exit_check == 100 :
					status = 0
					truck_entry = False
					truck_exit = True
					exit_time = datetime.now().time()
					entry_check = 0
				else :
					exit_check = exit_check+1
					truck_entry = False
			elif status == 0 and len(result) == 0 :

				if entry_check == 100 :
					status = 1
					truck_entry = True
					truck_video = True
					truck_exit = False
					entry_time = datetime.now().time()
					exit_check = 0
				else :
					entry_check = entry_check +1
					truck_exit = False
			elif status == 1 and len(result) == 0 :
				truck_entry = False
			elif status == 0 and len(result) > 0 :
				truck_exit = False

			if truck_video == True:
				pp = str(datetime.now())[0:19].replace('-','') # Takes the system timestamp to name the videos
				pp = pp.replace(' ','')
				pp = pp.replace(':','')
				path1 = "cylinder_storage/side_view/"+pp +".mp4"
				path2 = "cylinder_storage/top_view/"+pp+".mp4"
				#print("pp",path1)
				out1=cv2.VideoWriter( path1, cv2.VideoWriter_fourcc(*'XVID'), 10, (640,480))
				out2=cv2.VideoWriter( path2, cv2.VideoWriter_fourcc(*'XVID'), 10, (1920,1080))
				truck_video = False
				outwrite_flag = True

			if outwrite_flag == True:
			#if truck_entry == True:
				out1.write(img1)
				out2.write(img2)
				print("Saving")
				#out2.write(img2)

			if truck_exit == True:
			#elif truck_exit == True:
				#cam1.release()
				out1.release()
				out2.release()
				print("Saved")
				outwrite_flag = False
				#out2.release()
			if cv2.waitKey(1) & 0xff == ord('q'):
				break
		else:
			continue
	cam1.release()
	out1.release()
	cv2.destroyAllWindows()
except Exception as e:
	print("Error in Main File:",str(e))

#out2.release()
