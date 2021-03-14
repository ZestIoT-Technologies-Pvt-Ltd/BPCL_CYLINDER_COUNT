#   Copyright (C) 2020 by ZestIOT. All rights reserved. The information in this 
#   document is the property of ZestIOT. Except as specifically authorized in 
#   writing by ZestIOT, the receiver of this document shall keep the information
#   contained herein confidential and shall protect the same in whole or in part from
#   disclosure and dissemination to third parties. Disclosure and disseminations to 
#   the receiver's employees shall only be made on a strict need to know basis.
"""
Input: image from camera, darknet image object, loaded network (darknet object), class_name 
       (darknet object), truck entry flag.

Output: Processed image with detection of cylinders in ROI in side view along with cylinder count 

User Requirement:
1) Counting the number of cylinders from the truck arrived and seggregating them into 14.2kgs, 19kgs and 5kgs as per their size and shape.


Requirements:
1) This function takes the darknet image object, loaded network(darknet object), class name(darknet onject)
2) The image from the camera will be corpped cropped into Region of inetrest(ROI) and then it is converted to 
   the darknet image object which is passed to the loaded model with class names. The result is the detection 
   of cylinder in each ROI, which basically provides the central coordinates of the bounding box detection of 
   the respective object.
3) We draw three lines as point of reference for the cylinder count.
2) We increase the count of the cylinders whenever they cross the three lines as mentioned.
3) Depeding upon the sizes we seggregate the cylinders into 19kg, 14kg and 5kg and increase count respectively.
"""

import darknet
import cv2
from datetime import datetime, timedelta
import traceback
import numpy as np
import csv
import random
import time

fieldnames = ["Time", "x-Coordinates",]


font = cv2.FONT_HERSHEY_SIMPLEX
is_first = 1                            
current_dict = {}                    
prev_dict = {}
current_len, prev_len = 0,0        #  Current dictionary and previous dictonary lenghts
total_count = 0                    #  Total Count of the cylinders 
cyl_19_count = 0                    
cyl_14_count = 0
cyl_5_count = 0
count_miss = 0                    
className = 'None'
#line1 = 240
#line2 = 250
#line3 = 255
line1 = 290
line2 = 300
line3 = 305
plot_path = "graph_plots/default_path.csv"
"""Sorting function.

Taking the least value and return from the list 
"""
def sortSecond(val): 
  return val[1]

def csv_live_data(x_value):
    with open(plot_path, 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("in csv live data")

        info = {
            "Time": now,
            "x-Coordinates": x_value
        }

        csv_writer.writerow(info)

"""Getting the central coorindates for bounding box detection of the respective object.

Input: Result(the darknet image object which is passed to the loaded model with class names) and img(image from the camera).

Output: list1(Updated xm,ym of the particular cylinder in ROI) and count.
"""  
def get_input_data(result,img):
  global className
  list1 = {}
  cyl = 0
  cyl_dict={}
  result.sort(key = sortSecond, reverse = True)

  try:
    for i,j in enumerate(result):
      if float(j[1]) < 55 :
        continue
      className = j[0]
      cord=j[2]
      xm=int((cord[0]) * float(x_res/416))                 # center coordinate of x-axis
      ym=int((cord[1]) * float(y_res/416))                 # Center coordinate of y-axis
      xco=int(float(cord[0]-cord[2]/2) * float(x_res/416)) # bounding box coordinates of x-axis
      yco=int(float(cord[1]-cord[3]/2) * float(y_res/416)) # bounding box coordinates of y-axis
      xExt=int(float(cord[2]) * float(x_res/416))
      yExt=int(float(cord[3]) * float(y_res/416)) 
      img=cv2.rectangle(img,(xco,yco),(xco+xExt,yco+yExt),(0,0,255),2)
      
      """
      Taking the central coodintes of x, y axis and comparing them. If they are in between line1 and line2 coordinates.
      Note them and add it into the list for further processing.
      """
      if (xm >= line1) and (xm <=line3+5): 
        if (xExt <= yExt): #width < height
          if (xExt <= (line3-line1+30)):
            print("valus",xco,yco,xExt,yExt) 
            print("xm, ym",xm,ym)
            state = "Initialized"        
            cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
            list1.update(cyl_dict)
            cyl=cyl+1
            csv_live_data(xm)
            break
        else:#width > height
          print("valus",xco,yco,xExt,yExt) 
          print("xm, ym",xm,ym)
          state = "Initialized"   
          cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
          list1.update(cyl_dict)
          cyl=cyl+1
          csv_live_data(xm)
          break
  except Exception as e:
    print("Error in Get input data:",str(e))  
  return list1,cyl 


"""Updating the cylinder counter.

Input: Current list(Current dict with state and xco) and Prev dict (Previous dictonary with state and pevious xco)

Comparing the current dict "xco" and previous dictonary "xco" values and previous dictonary state to increment the counter.

If Current dictory xco value is greater than line2 value and previous dictonary xco value is less than or equal to line2 value
and prev dictonary stated should not be greater than line 3. Then it tells us that particular cylinder is being crossed the line2 
for the first time and it is less than the line3. So we increment the counter only once after crossing the second line.

Based on the className we got from darknet image with real time image. We take reference of that and increment the counter with respect to
Specific class Names.
"""  
def update_counter(current_list,prev_dict):
  global total_count
  global cyl_14_count
  global cyl_19_count
  try:
    for key in current_dict:
      if current_dict[key]['state'] == 'moving right':
        if current_dict[key]['xco'] > line2 and prev_dict[key]['xco'] <= line2 and prev_dict[key]['state'] != 'counted':
          total_count = total_count + 1
          if className == 'Cylinder_14':
            cyl_14_count = cyl_14_count+1
          if className == 'Cylinder_19':
            cyl_19_count = cyl_19_count + 1
          break
  except Exception as e:
    print("Error in Side viewUpdate counter:",str(e))

"""Updating the list for moving ,not moving and moving left.

Input: Current list(Current dict with state and xco),Prev dict (Previous dictonary with state.

Comparing the current dict xco and previous dictonary xco for knowing the moving right, left and stationary.

If current dictonary xco is greater than previous dictonary xco and current dictornary is less than line 3. We consider 
as moving right else not considered. If current dict and previous dict is equal, then it is considered as stationery.
or else moving left, if previous is greater current dict we copy the previous dict values to current dict values to minimise
the left movements.

if current dict is greater than line3, then current dict value will be written with line1 value.

Copying the current dict values to previous dictonary values
"""  
def update_list(current_dict,prev_dict):
  global prev_len
  try:
    for key in current_dict:
      if int(current_dict[key]['xco']) > int(prev_dict[key]['xco']):
        if(current_dict[key]['xco'] < line3):
          current_dict[key]['state']='moving right'
        else:
          current_dict[key]['state']='counted'

      elif int(current_dict[key]['xco']) == int(prev_dict[key]['xco']):
        current_dict[key]['state']='non moving'
      else:
        current_dict[key]['xco']=prev_dict[key]['xco']
        current_dict[key]['yco']=prev_dict[key]['yco']
        current_dict[key]['state']='moving left'
      
    update_counter(current_dict,prev_dict)
    
    for key in current_dict:
      if int(current_dict[key]['xco']) >= line3:
          prev_dict[key]['xco']= line1
      else:
          prev_dict[key]['xco'] = current_dict[key]['xco']

      prev_dict[key]['state'] = current_dict[key]['state']
      prev_dict[key]['yco'] = current_dict[key]['yco']
    prev_len = len(current_dict)
  except Exception as e:
    print("Error in Side update list:",str(e))  


def side_model(img,darknet_image,network,class_names,truck_entry):

    global x_res,y_res,total_count,cyl_19_count,cyl_14_count,className,line1,line2,line3
    global font, is_first,current_dict,prev_dict,current_len,prev_len,count_miss
    global plot_path

    try:
      if truck_entry == True :
        total_count,cyl_19_count,cyl_14_count = 0,0,0
        pp = str(datetime.now())[0:19].replace('-','') # Takes the system timestamp to name the videos
        pp = pp.replace(' ','')
        pp = pp.replace(':','')
        plot_path = "graph_plots/"+pp +".csv"

        with open(plot_path, 'wb') as csvfile:
              filewriter = csv.writer(csvfile, delimiter=',',
                                      quotechar='|', quoting=csv.QUOTE_MINIMAL)

        with open(plot_path, 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
          #print("pp",path)
      
      x_res=int(img.shape[1])
      y_res=int(img.shape[0])
      img=cv2.rectangle(img,(260,350),(335,465),(0,255,255),2)
 
      pts = np.array([[260,345],[260,460],[325,460],[325,345]])
      mask1 = np.zeros(img.shape[:2], np.uint8)
      cv2.drawContours(mask1, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
      img1 = cv2.bitwise_and(img, img, mask=mask1)


      pts = np.array([[231,385],[231,460],[345,460],[345,390]]) 
      mask2 = np.zeros(img.shape[:2], np.uint8)
      cv2.drawContours(mask2, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
      img2 = cv2.bitwise_and(img, img, mask=mask2)
    

      #mask = mask1 | mask2
      img3 = cv2.bitwise_or(img1,img2,mask= None)
      frame_rgb = cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)

      frame_resized = cv2.resize(frame_rgb,(darknet.network_width(network),darknet.network_height(network)),interpolation=cv2.INTER_LINEAR)
      darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
      result=darknet.detect_image(network,class_names,darknet_image, thresh=0.25)

      current_dict,current_len = get_input_data(result,img)

      img = cv2.line(img, (line1,355), (line1,460), (0, 255, 0),2)
      img = cv2.line(img, (line3,460), (line3,355), (0, 255, 0), 2)
      img = cv2.line(img, (line2,460), (line2,355), (255, 0, 0),2)

      """

      For the first time depending upon the classname we update the prev dict with current and
      prev dict length with current dict lenght and will exut from the loop. So, that from next time 
      we will have prev dict to compare with current dictonary values and lengths.
      """
      if is_first == 1:
        prev_dict = current_dict
        prev_len  = current_len
        if (current_len != 0):
          is_first = 0
      else:
        if (prev_len == current_len):
          update_list(current_dict,prev_dict)
        else:
          count_miss = count_miss + 1

      cv2.putText(img, "Count of cylinders : "+str(total_count), (330,40), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "Segregated count ", (330,70), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "5 KGS Count : "+str(cyl_5_count), (330,100), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "14 KGS Count : "+str(cyl_14_count), (330,130), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "19 KGS Count : "+str(cyl_19_count), (330,160), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      print("Total count",total_count,count_miss,cyl_14_count,cyl_19_count)
    except Exception as e:
      print("Error in Side model:",str(e))
    return img,cyl_14_count,cyl_19_count,cyl_5_count,total_count



