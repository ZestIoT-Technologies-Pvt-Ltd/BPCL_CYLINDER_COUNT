#   Copyright (C) 2020 by ZestIOT. All rights reserved. The information in this 
#   document is the property of ZestIOT. Except as specifically authorized in 
#   writing by ZestIOT, the receiver of this document shall keep the information
#   contained herein confidential and shall protect the same in whole or in part from
#   disclosure and dissemination to third parties. Disclosure and disseminations to 
#   the receiver's employees shall only be made on a strict need to know basis.
"""
Input: image from camera, darknet image object, loaded network (darknet object), class_name 
       (darknet object), truck entry flag.

Output: Processed image with detection vehicle arrival or exit, truck entry and truck exit flags.

User Requirement:
1) getting the timestamp for vehicle arrival and departure at the unloading points.


Requirements:
1) This function takes the darknet image object, loaded network(darknet object), class name(darknet onject)
2) The image from the camera will be corpped cropped into Region of inetrest(ROI) and then it is converted to 
   the darknet image object which is passed to the loaded model with class names. The result is the detection 
   of cylinder in each ROI, which basically provides the central coordinates of the bounding box detection of 
   the respective object.
2) We increase the Cylinder count and cap count of the cylinders whenever they cross the three lines as mentioned.
3) Depeding upon the cap count lines and cylinder count lines crossing.We increment the counts.
"""

import darknet
import cv2
from datetime import datetime, timedelta
import traceback
import numpy as np

status = 0
entry_check = 0
exit_check = 0
exit_time,entry_time = 0,0
truck_entry = False
truck_exit = False

def truck_model(img,className):

  global status, entry_check, exit_check,exit_time,entry_time,truck_entry,truck_exit

  try:
    truck_entry = False
    truck_exit = False
    print("TruckEntry", className)    
    """
    Status will be zero initiallly. If any truck arrives then the darkent object with class name will be detected as the door
    of the vehicle is arrived at the point.

    if any vehicle is detected then it will check the vehicle presence for 30 seconds by incrementing the counter of entry_check 
    for arrival and exit check for departure. 

    if Entry check is 540(i.e 18fps*30seconds = 540) then, we note that as vehicle arrival by setting the flag of truck_entry to True
    if Exit check is 540(i.e 18fps*30seconds = 540) then, we note that as vehicle departure by setting the flag of truck_exit to True.

    Remaining all the cases will set to false for truck_entry and truck_exit variables.
    """
      
    if status == 1 and className == 'No_truck' :
      if exit_check == 100 :
        status = 0
        truck_entry = False
        truck_exit = True
        exit_time = datetime.now().time()
        entry_check = 0
        print("Truck Departed")
      else :
        exit_check = exit_check+1
        truck_entry = False
    elif status == 0 and className != 'No_truck' :
      if entry_check == 100 :
        status = 1
        truck_entry = True
        truck_exit = False
        entry_time = datetime.now().time()
        exit_check = 0
        print("Truck Entered")
      else :
        entry_check = entry_check +1 
        truck_exit = False
    elif status == 1 and className != 'No_truck' :
      truck_entry = False
    elif status == 0 and className == 'No_truck':
      truck_exit = False

    shape = img.shape
    img = cv2.resize(img,(640,480))

    if status == 1 :
      cv2.putText(img, "truck arrived: " + str(entry_time.hour) + ":"+ str(entry_time.minute), (390,100), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0, 0, 0), 1, cv2.LINE_AA)
    elif status == 0 and exit_time != 0 and entry_time != 0 :
      cv2.putText(img, "truck arrived: " + str(entry_time.hour) + ":"+ str(entry_time.minute), (390,100), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0, 0, 0), 1, cv2.LINE_AA)
      cv2.putText(img, "truck departed: " + str(exit_time.hour) + ":"+ str(exit_time.minute), (390,130), cv2.FONT_HERSHEY_COMPLEX, 0.65, (0, 0, 0), 1, cv2.LINE_AA)
    
    img = cv2.resize(img,(shape[1],shape[0]))
  except Exception as e:
    print("Error in Truck Model:",str(e))
    
  return img, truck_entry, truck_exit

