#   Copyright (C) 2020 by ZestIOT. All rights reserved. The information in this 
#   document is the property of ZestIOT. Except as specifically authorized in 
#   writing by ZestIOT, the receiver of this document shall keep the information
#   contained herein confidential and shall protect the same in whole or in part from
#   disclosure and dissemination to third parties. Disclosure and disseminations to 
#   the receiver's employees shall only be made on a strict need to know basis.
"""
Input: image from camera, darknet image object, loaded network (darknet object), class_name 
       (darknet object), truck entry flag.

Output: Processed image with detection of cylinders in ROI in side view along with cylinder count and Cylinder cap Count

User Requirement:
1) Counting the number of cylinders and caps for then, from the truck arrived.


Requirements:
1) This function takes the darknet image object, loaded network(darknet object), class name(darknet onject)
2) The image from the camera will be corpped cropped into Region of inetrest(ROI) and then it is converted to 
   the darknet image object which is passed to the loaded model with class names. The result is the detection 
   of cylinder in each ROI, which basically provides the central coordinates of the bounding box detection of 
   the respective object.
3) We draw three lines as point of reference for the cylinder count and cap count.
2) We increase the Cylinder count and cap count of the cylinders whenever they cross the three lines as mentioned.
3) Depeding upon the cap count lines and cylinder count lines crossing.We increment the counts.
"""

import darknet
import cv2
from datetime import datetime, timedelta
import traceback
import numpy as np

is_first = 1
is_first_cap = 1 
current_dict = {}
prev_dict = {}
prev_dict_cap ={}
current_cap_dict = {}
prev_cap_dict = {}
current_len, prev_len = 0,0
current_cap_len, prev_cap_len = 0,0
className = 'None'
total_count = 0
total_cap_count = 0

line1 = 170
line2 = 130
line3 = 115
#line1_cap = 240
#line2_cap = 210
#line3_cap = 180

line1_cap = 265
line2_cap = 250
line3_cap = 200

count_miss = 0


"""Updating the list for moving up,not moving, moving down and moving left.

Input: Current list(Current dict with state and xco),Prev dict (Previous dictonary with state.

Comparing the current dict xco and previous dictonary xco for knowing the moving up, down and stationary.

If current dictonary xco is greater than previous dictonary xco and current dictornary is less than line 3. We consider 
as moving up else not considered. If current dict and previous dict is equal, then it is considered as stationary.
or else moving left. if previous dict is greater current dict we copy the previous dict values to current dict values to minimise
the down movements.

if current dict is greater than line3, then current dict value will be written with line1 value.

Copying the current dict values to previous dictonary values for next set of loop
"""  

def update_list(current_dict,prev_dict):

	global prev_len
	try:
		for key in current_dict:
			if int(current_dict[key]['yco']) < int(prev_dict[key]['yco']):
				if(current_dict[key]['yco'] > line3):
					current_dict[key]['state']='moving up'
				else:
					current_dict[key]['state']='counted'
			elif int(current_dict[key]['yco']) == int(prev_dict[key]['yco']):
				current_dict[key]['state']='non moving'
			else:
				current_dict[key]['state']='moving down'
			
		update_counter(current_dict,prev_dict)

		for key in current_dict:
			if int(current_dict[key]['yco']) <= line3:
					prev_dict[key]['yco']= line1
			else:
					prev_dict[key]['yco'] = current_dict[key]['yco']

			prev_dict[key]['state'] = current_dict[key]['state']
			prev_dict[key]['xco'] = current_dict[key]['xco']
		prev_len = len(current_dict)
	except Exception as e:
		print("Error in TOP View Update list:",str(e))
	 

"""Getting the central coorindates for bounding box detection of the respective object.

Input: Result(the darknet image object which is passed to the loaded model with class names) and img(image from the camera).

Output: list1(Updated xm,ym of the particular cylinder in ROI) and count.

We differentitate the Cylinder and caps depending upon the className we enumerate from the result and return them accordingly for 
further processing
"""  
def get_input_data(result,img,x_res,y_res):

	global className
	list1 = {}
	cyl = 0
	cyl_cap = 0
	cyl_count = 0
	cyl_dict={}
	try:
		for i,j in enumerate(result):
			if float(j[1]) < 55 :
				continue  
			className = j[0]
			cord=j[2]
			xm=int((cord[0]) * float(x_res/416)) # cent coordinates
			ym=int((cord[1]) * float(y_res/416))
			xco=int(float(cord[0]-cord[2]/2) * float(x_res/416)) # bounding box coordinates
			yco=int(float(cord[1]-cord[3]/2) * float(y_res/416))
			xExt=int(float(cord[2]) * float(x_res/416))
			yExt=int(float(cord[3]) * float(y_res/416)) 
			#img=cv2.rectangle(img,(xco,yco),(xco+xExt,yco+yExt),(0,0,255),2)

			if className == 'cap':
				if (ym <= line1_cap) and (ym >=line3_cap) :
					state = "Initialized"		
					cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
					list1.update(cyl_dict)
					cyl_cap = cyl_cap+1
					cyl_count = cyl_cap
					break

			if className == 'cylinder':
				if (ym <= line1) and (ym >=line3-5) :
					state = "Initialized"		
					cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
					list1.update(cyl_dict)
					cyl=cyl+1
					cyl_count = cyl
					break
	except Exception as e:
		print("Error in TOP View Get input data:",str(e))
	return list1,cyl_count    


"""Updating the cylinder counter.

Input: Current list(Current dict with state and xco) and Prev dict (Previous dictonary with state and pevious xco)

Comparing the current dict "xco" and previous dictonary "xco" values and previous dictonary state to increment the counter.

If Current dictory xco value is less than line2 value and previous dictonary xco value is greater than or equal to line2 value
Then it tells us that particular cylinder is being crossed the line2 for the first time and it is less than the line3. 
So we increment the counter only once if central coordinate of the bounding box has crossed the second line.
"""  
def update_counter(current_list,prev_dict):

	global total_count
	try:
		for key in current_dict:
			if current_dict[key]['state'] == 'moving up':
				if current_dict[key]['yco'] < line2 and prev_dict[key]['yco'] >= line2 and prev_dict[key]['state'] != 'counted':
					total_count = total_count + 1
					break
	except Exception as e:
		print("Errorin Top view update counter:",str(e))

"""Updating the list for moving up ,stationary and moving down for the caps count..

Input: Current list(Current dict with state and xco),Prev dict (Previous dictonary with state and pevious xco).

Comparing the current dict xco and previous dictonary xco for knowing the moving up, down and stationary.

If current dictonary xco is less than previous dictonary xco value and current dictornary is greater than line 3. We consider 
as moving right else not considered. If current dict and previous dict is equal, then it is considered as stationery.
or else moving left, if previous dict is less than current dict, state will changed to moving down.

if current dict is less than or equal to line3, then current dict value will be written with line1 value.

Copying the current dict values to previous dictonary values and current dict len to prev dict len
"""  
def update_cap_list(current_cap_dict,prev_cap_dict):

	global prev_cap_len
	try:
		for key in current_dict:
			if int(current_cap_dict[key]['yco']) < int(prev_cap_dict[key]['yco']): 
				if(current_cap_dict[key]['yco'] > line3):
					current_cap_dict[key]['state']='moving up'
				else:
					current_cap_dict[key]['state']='counted'
			elif int(current_cap_dict[key]['yco']) == int(prev_cap_dict[key]['yco']):
				current_cap_dict[key]['state']='non moving'
			else:
				current_cap_dict[key]['state']='moving down'
			
		update_cap_counter(current_cap_dict,prev_cap_dict)
				
		for key in current_cap_dict:
			if int(current_cap_dict[key]['yco']) <= line3:
					prev_cap_dict[key]['yco']= line1
			else:
					prev_cap_dict[key]['yco'] = current_cap_dict[key]['yco']

			prev_cap_dict[key]['state'] = current_cap_dict[key]['state']
			prev_cap_dict[key]['xco'] = current_cap_dict[key]['xco']
		prev_cap_len = len(current_cap_dict)
	except Exception as e:
		print("Error in Update Cap list:",str(e))
		
		 

"""Updating the Cap counter.

Input: Current list(Current dict with state and xco) and Prev dict (Previous dictonary with state and pevious xco)

Comparing the current dict "xco" and previous dictonary "xco" values and previous dictonary state to increment the counter.

To increment the counter cylinder should be moving up as compared with previous state.

If Current dictory xco value is less than line2 value and previous dictonary xco value is greater than or equal to line2 value
Then it tells us that particular cylinder is being crossed the line2 for the first time and it is less than the line3. 
So we increment the counter only once if central coordinate of the bounding box has crossed the second line.
"""
def update_cap_counter(current_cap_dict,prev_cap_dict):

	global total_cap_count
	try:
		for key in current_cap_dict:
			if current_cap_dict[key]['state'] == 'moving up':
				if current_cap_dict[key]['yco'] < line2_cap and prev_cap_dict[key]['yco'] >= line2_cap and prev_cap_dict[key]['state'] != 'counted':
					total_cap_count = total_cap_count + 1
					break
	except Exception as e:
		print("Error in Update cap counter:",str(e))


def top_model(img,darknet_image,network,class_names,truck_entry):

	global is_first, is_first_cap, current_dict, prev_dict, current_cap_dict, prev_cap_dict, current_len, prev_len, current_cap_len, prev_cap_len 
	global className, total_count, total_cap_count, line1, line2, line3, line1_cap, line2_cap, line3_cap, count_miss,prev_dict_cap

	# if new truck is arrived, then the previous values will be initialized to zero.

	try:
		if truck_entry == True:
			total_count,total_cap_count = 0,0

		x_res=int(img.shape[1])
		y_res=int(img.shape[0])
		pts = np.array([[[788,20],[1073,20],[1087,450],[757,450]]])
		poly = np.array([[788,20],[1073,20],[1087,450],[757,450]], np.int32)
		poly = poly.reshape((-1,1,2))
		#cv2.polylines(img,[poly],True,(0,255,255),3)

		mask = np.zeros(img.shape[:2], np.uint8)
		cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
		dst = cv2.bitwise_and(img, img, mask=mask)
		frame_rgb = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)
		frame_resized = cv2.resize(frame_rgb,(darknet.network_width(network),darknet.network_height(network)),interpolation=cv2.INTER_LINEAR)
		darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
		result=darknet.detect_image(network,class_names,darknet_image, thresh=0.25)

		#function to get the current dictonary values of bounding box.
		current_dict,current_len = get_input_data(result,img,x_res,y_res)

		# Drawing the lines on the video frames.
		#img = cv2.line(img, (788,line1), (1087,line1), (0, 255, 0),2)
		#img = cv2.line(img, (788,line2), (1087,line2), (0, 255, 0),2)
		#img = cv2.line(img, (788,line3), (1087,line3), (0, 255, 0),2)
		#img = cv2.line(img, (788,line1_cap), (1087,line1_cap), (0, 255, 255),2)
		#img = cv2.line(img, (788,line2_cap), (1087,line2_cap), (0, 255, 255),2)
		#img = cv2.line(img, (788,line3_cap), (1087,line3_cap), (0, 255, 255),2)


		"""

		For the first time depending upon the classname we update the prev dict with current and
		prev dict length with current dict lenght and will exut from the loop. So, that from next time 
		we will have prev dict to compare with current dictonary values and lengths.
		"""
		
		if className == 'cylinder':
			if is_first == 1:
				prev_dict = current_dict
				prev_len  = current_len
				if (current_len != 0):
					is_first = 0
			else :
				if (prev_len == current_len):
					update_list(current_dict,prev_dict)
				else:
					count_miss = 0

		if className == 'cap':
			if is_first_cap == 1:
				prev_dict_cap = current_dict
				prev_cap_len  = current_len
				if (current_len != 0):
					is_first_cap = 0
			else:
				if (prev_cap_len == current_len):
					update_cap_list(current_dict,prev_dict_cap)
				else:
					count_miss = 0

		img = cv2.resize(img,(640,480))
		cv2.putText(img, "Cylinder Count: "+str(total_count), (390,40), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0, 0, 0), 1, cv2.LINE_AA)
		cv2.putText(img, "Cylinder Caps: "+str(total_cap_count), (390,70), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0, 0, 0), 1, cv2.LINE_AA)
		print("Total count:",total_count,"cap_count:",total_cap_count,img.shape)

	except Exception as e:
		print("Error in Top View Model:",str(e))
	return img,total_cap_count


