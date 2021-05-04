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
import side
fieldnames = ["Time", "x-Coordinates",]


font = cv2.FONT_HERSHEY_SIMPLEX
is_first1 = 1                            
is_first2 = 1
current_dict1 = {}                    
prev_dict1 = {}
current_len1, prev_len1 = 0,0        #  Current dictionary and previous dictonary lenghts
total_count1 = 0                    #  Total Count of the cylinders 
cyl_19_count1 = 0                    
cyl_14_count1 = 0
cyl_5_count1= 0
count_miss1 = 0                    

current_dict2 = {}                    
prev_dict2 = {}
current_len2, prev_len2 = 0,0        #  Current dictionary and previous dictonary lenghts
total_count2 = 0                    #  Total Count of the cylinders 
cyl_19_count2 = 0                    
cyl_14_count2 = 0
cyl_5_count2 = 0
count_miss2 = 0                    


total_count = 0                    #  Total Count of the cylinders 
cyl_19_count = 0                    
cyl_14_count = 0
cyl_5_count = 0

className = 'None'
#line1 = 240
#line2 = 250
#line3 = 255

#line1 = 250
#line2 = 260
#line3 = 265

line1 = 245
line2 = 255
line3 = 265

line4 = 335
line5 = 345
line6 = 355


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
        #print("in csv live data")

        info = {
            "Time": now,
            "x-Coordinates": x_value
        }

        csv_writer.writerow(info)

"""Getting the central coorindates for bounding box detection of the respective object.

Input: Result(the darknet image object which is passed to the loaded model with class names) and img(image from the camera).

Output: list1(Updated xm,ym of the particular cylinder in ROI) and count.
"""  
def get_input_data1(result,img):
  global className1
  list1 = {}
  cyl = 0
  cyl_dict={}
  result.sort(key = sortSecond, reverse = True)

  try:

    for i,j in enumerate(result):
      if float(j[1]) < 55 :
        continue
      className1 = j[0]
      cord=j[2]
      xm=int((cord[0]) * float(x_res/416))                 # center coordinate of x-axis
      ym=int((cord[1]) * float(y_res/416))                 # Center coordinate of y-axis
      xco=int(float(cord[0]-cord[2]/2) * float(x_res/416)) # bounding box coordinates of x-axis
      yco=int(float(cord[1]-cord[3]/2) * float(y_res/416)) # bounding box coordinates of y-axis
      xExt=int(float(cord[2]) * float(x_res/416))
      yExt=int(float(cord[3]) * float(y_res/416)) 
      
      """
      Taking the central coodintes of x, y axis and comparing them. If they are in between line1 and line2 coordinates.
      Note them and add it into the list for further processing.
      """
      if (xm >= line1) and (xm <=line3+5): 
        #img=cv2.rectangle(img,(xco,yco),(xco+xExt,yco+yExt),(0,0,255),2)
      
        if (xExt <= yExt): #width < height
          if (xExt <= (line3-line1+30)):
           #print("valus1",xco,yco,xExt,yExt) 
            #print("xm1, ym1",xm,ym)
            state = "Initialized"        
            cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
            list1.update(cyl_dict)
            cyl=cyl+1
            #csv_live_data(xm)
            break
        else:#width > height
          #print("valus1",xco,yco,xExt,yExt) 
          #print("xm1, ym1",xm,ym)
          state = "Initialized"   
          cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
          list1.update(cyl_dict)
          cyl=cyl+1
          #csv_live_data(xm)
          break


  except Exception as e:
    print("Error in Get input data:",str(e))  
  return list1,cyl 


def get_input_data2(result,img):
  global className2
  list1 = {}
  cyl = 0
  cyl_dict={}
  result.sort(key = sortSecond, reverse = True)

  try:

    for i,j in enumerate(result):
      if float(j[1]) < 55 :
        continue
      className2 = j[0]
      cord=j[2]
      xm=int((cord[0]) * float(x_res/416))                 # center coordinate of x-axis
      ym=int((cord[1]) * float(y_res/416))                 # Center coordinate of y-axis
      xco=int(float(cord[0]-cord[2]/2) * float(x_res/416)) # bounding box coordinates of x-axis
      yco=int(float(cord[1]-cord[3]/2) * float(y_res/416)) # bounding box coordinates of y-axis
      xExt=int(float(cord[2]) * float(x_res/416))
      yExt=int(float(cord[3]) * float(y_res/416)) 
      
      """
      Taking the central coodintes of x, y axis and comparing them. If they are in between line1 and line2 coordinates.
      Note them and add it into the list for further processing.
      """
      if (xm >= line4) and (xm <=line6+5): 
        #img=cv2.rectangle(img,(xco,yco),(xco+xExt,yco+yExt),(0,0,255),2)
      
        if (xExt <= yExt): #width < height
          if (xExt <= (line6-line4+30)):
            #print("valus2",xco,yco,xExt,yExt) 
            #print("xm2, ym2",xm,ym)
            state = "Initialized"        
            cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
            list1.update(cyl_dict)
            cyl=cyl+1
            #csv_live_data(xm)
            break
        else:#width > height
          #print("valus2",xco,yco,xExt,yExt) 
          #print("xm2, ym2",xm,ym)
          state = "Initialized"   
          cyl_dict[cyl]={'xco':xm,'yco':ym,'state':"Initialized"}
          list1.update(cyl_dict)
          cyl=cyl+1
          #csv_live_data(xm)
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
def update_counter1(current_dict1,prev_dict1):
  global total_count1
  global cyl_14_count1
  global cyl_19_count1
  try:
    for key in current_dict1:
      if current_dict1[key]['state'] == 'moving right':
        if current_dict1[key]['xco'] > line2 and prev_dict1[key]['xco'] <= line2 and prev_dict1[key]['state'] != 'counted':
          total_count1 = total_count1 + 1
          if className1 == 'Cylinder_14':
            cyl_14_count1 = cyl_14_count1+1
          if className1 == 'Cylinder_19':
            cyl_19_count1 = cyl_19_count1 + 1
          break
  except Exception as e:
    print("Error in Side viewUpdate counter:",str(e))


def update_counter2(current_dict2,prev_dict2):
  global total_count2
  global cyl_14_count2
  global cyl_19_count2
  try:
    for key in current_dict2:
      if current_dict2[key]['state'] == 'moving right':
        if current_dict2[key]['xco'] > line5 and prev_dict2[key]['xco'] <= line5 and prev_dict2[key]['state'] != 'counted':
          total_count2 = total_count2 + 1
          if className2 == 'Cylinder_14':
            cyl_14_count2 = cyl_14_count2+1
          if className2 == 'Cylinder_19':
            cyl_19_count2 = cyl_19_count2 + 1
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
def update_list1(current_dict1,prev_dict1):
  global prev_len1
  #print("current_dict1",current_dict1)
  #print("prev_dict1",prev_dict1) 
  try:
    for key in current_dict1:
      if int(current_dict1[key]['xco']) > int(prev_dict1[key]['xco']):
        if(current_dict1[key]['xco'] < line3):
          current_dict1[key]['state']='moving right'
        else:
          current_dict1[key]['state']='counted'

      elif int(current_dict1[key]['xco']) == int(prev_dict1[key]['xco']):
        current_dict1[key]['state']='non moving'
      else:
        current_dict1[key]['xco']=prev_dict1[key]['xco']
        current_dict1[key]['yco']=prev_dict1[key]['yco']
        current_dict1[key]['state']='moving left'
      
    #print("current_dict1",current_dict1)
    #print("prev_dict1",prev_dict1) 
    update_counter1(current_dict1,prev_dict1)
    
    for key in current_dict1:
      if int(current_dict1[key]['xco']) >= line3:
          prev_dict1[key]['xco']= line1
      else:
          prev_dict1[key]['xco'] = current_dict1[key]['xco']

      prev_dict1[key]['state'] = current_dict1[key]['state']
      prev_dict1[key]['yco'] = current_dict1[key]['yco']
    prev_len1 = len(current_dict1)
  except Exception as e:
    print("Error in Side update list:",str(e))

def update_list2(current_dict2,prev_dict2):
  global prev_len2
  #print("current_dict2",current_dict2)
  #print("prev_dict2",prev_dict2) 
  try:
    for key in current_dict2:
      if int(current_dict2[key]['xco']) > int(prev_dict2[key]['xco']):
        if(current_dict2[key]['xco'] < line6):
          current_dict2[key]['state']='moving right'
        else:
          current_dict2[key]['state']='counted'

      elif int(current_dict2[key]['xco']) == int(prev_dict2[key]['xco']):
        current_dict2[key]['state']='non moving'
      else:
        current_dict2[key]['xco']=prev_dict2[key]['xco']
        current_dict2[key]['yco']=prev_dict2[key]['yco']
        current_dict2[key]['state']='moving left'
    #print("current_dict2",current_dict2)
    #print("prev_dict2",prev_dict2)  
    update_counter2(current_dict2,prev_dict2)
    
    for key in current_dict2:
      if int(current_dict2[key]['xco']) >= line6:
          prev_dict2[key]['xco']= line4
      else:
          prev_dict2[key]['xco'] = current_dict2[key]['xco']

      prev_dict2[key]['state'] = current_dict2[key]['state']
      prev_dict2[key]['yco'] = current_dict2[key]['yco']
    prev_len2 = len(current_dict2)
  except Exception as e:
    print("Error in Side update list:",str(e))    


def compare_countValues():

  global total_count, cyl_14_count, cyl_19_count, cyl_5_count
  global total_count1, cyl_14_count1, cyl_19_count1, cyl_5_count1
  global total_count2, cyl_14_count2, cyl_19_count2, cyl_5_count2

  if (cyl_14_count1 >= cyl_14_count2):
    cyl_14_count = cyl_14_count1
  else:
    cyl_14_count = cyl_14_count2

  if (cyl_19_count1 >= cyl_19_count2):
    cyl_19_count = cyl_19_count1
  else:
    cyl_19_count = cyl_19_count2

  if (cyl_5_count1 >= cyl_5_count2):
    cyl_5_count = cyl_5_count1
  else:
    cyl_5_count = cyl_5_count2

  total_count = cyl_14_count+cyl_19_count+cyl_5_count


def side_model(img,darknet_image,network,class_names,truck_entry):

    global x_res,y_res,total_count1,cyl_19_count1,cyl_14_count1,className1,line1,line2,line3
    global font, is_first1,is_first2,current_dict1,prev_dict1,current_len1,prev_len1,count_miss1
    global plot_path
    global total_count, cyl_14_count, cyl_19_count, cyl_5_count

    global x_res,y_res,total_count2,cyl_19_count2,cyl_14_count2,className2,line4,line5,line6
    global font,current_dict2,prev_dict2,current_len2,prev_len2,count_miss2

    try:
      if truck_entry == True :
        total_count,cyl_19_count,cyl_14_count = 0,0,0
        total_count1,cyl_19_count1,cyl_14_count1 = 0,0,0
        total_count2,cyl_19_count2,cyl_14_count2 = 0,0,0
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
      #pts = np.array([[231,345],[231,460],[345,460],[345,345]]) # coordinate of Region of Interest
      #pts = np.array([[231,355],[231,460],[345,460],[345,355]]) # coordinate of Region of Interest
      #img=cv2.rectangle(img,(231,345),(345,460),(0,255,255),2)
      #pts = np.array([[231,345],[231,460],[345,460],[345,345]]) # coordinate of Region of Interest ROI1
      #img=cv2.rectangle(img,(231,345),(345,460),(0,255,255),2)  # ROI1
      #mask = np.zeros(img.shape[:2], np.uint8)
      #cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
      #dst = cv2.bitwise_and(img, img, mask=mask)

      #mask = np.zeros(img.shape[:2], np.uint8)
      #cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
      #dst = cv2.bitwise_and(img, img, mask=mask)
      #frame_rgb = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

      #img=cv2.rectangle(img,(210,345),(295,460),(0,255,255),2)
      #img=cv2.rectangle(img,(300,345),(395,470),(0,255,255),2)

      pts = np.array([[210,345],[210,460],[295,460],[295,345]])
      mask1 = np.zeros(img.shape[:2], np.uint8)
      cv2.drawContours(mask1, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
      img1 = cv2.bitwise_and(img, img, mask=mask1)


      pts = np.array([[210,400],[210,460],[395,470],[395,400]]) 
      mask2 = np.zeros(img.shape[:2], np.uint8)
      cv2.drawContours(mask2, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
      img2 = cv2.bitwise_and(img, img, mask=mask2)
    
  
      pts = np.array([[300,345],[300,460],[395,470],[395,345]])
      mask3 = np.zeros(img.shape[:2], np.uint8)
      cv2.drawContours(mask3, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
      img3 = cv2.bitwise_and(img, img, mask=mask3)

 
      img4 = cv2.bitwise_or(img1,img2,mask= None)
      img5 = cv2.bitwise_or(img3,img4,mask= None)
      frame_rgb = cv2.cvtColor(img5, cv2.COLOR_BGR2RGB)


      frame_resized = cv2.resize(frame_rgb,(darknet.network_width(network),darknet.network_height(network)),interpolation=cv2.INTER_LINEAR)
      darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
      result=darknet.detect_image(network,class_names,darknet_image, thresh=0.25)

      current_dict1,current_len1 = get_input_data1(result,img)
      current_dict2,current_len2 = get_input_data2(result,img)

      #img = cv2.line(img, (line1,355), (line1,460), (0, 255, 0),2)
      #img = cv2.line(img, (line3,460), (line3,355), (0, 255, 0), 2)
      #img = cv2.line(img, (line2,460), (line2,355), (255, 0, 0),2)


      #img = cv2.line(img, (line1,355), (line1,460), (0, 255, 0),2)
      #img = cv2.line(img, (line3,460), (line3,355), (0, 255, 0), 2)
      #img = cv2.line(img, (line2,460), (line2,355), (255, 0, 0),2)

      #img = cv2.line(img, (line4,355), (line4,460), (0, 255, 0),2)
      #img = cv2.line(img, (line6,460), (line6,355), (0, 255, 0), 2)
      #img = cv2.line(img, (line5,460), (line5,355), (255, 0, 0),2)

      """
      For the first time depending upon the classname we update the prev dict with current and
      prev dict length with current dict lenght and will exut from the loop. So, that from next time 
      we will have prev dict to compare with current dictonary values and lengths.
      """
      
      if is_first1 == 1:
        prev_dict1 = current_dict1
        prev_len1  = current_len1
        
        #prev_dict2 = current_dict2
        #prev_len2  = current_len2
        
        if (current_len1 != 0):
          is_first1 = 0
      else:
        if (prev_len1 == current_len1):
          update_list1(current_dict1,prev_dict1)
          #update_list2(current_dict2,prev_dict2)

        else:
          count_miss1 = count_miss1 + 1
          #count_miss2 = count_miss2 + 1



      if is_first2 == 1:
         #prev_dict1 = current_dict1
         #prev_len1  = current_len1

         prev_dict2 = current_dict2
         prev_len2  = current_len2

         if (current_len2 != 0):
           is_first2 = 0
      else:
         if (prev_len2 == current_len2):
           #update_list1(current_dict1,prev_dict1)
           update_list2(current_dict2,prev_dict2)

         else:
           #count_miss1 = count_miss1 + 1
           count_miss2 = count_miss2 + 1



      cv2.putText(img, "Count of cylinders1 : "+str(total_count1), (40,40), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "Segregated count1 ", (40,70), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "5 KGS Count1 : "+str(cyl_5_count1), (40,100), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "14 KGS Count1 : "+str(cyl_14_count1), (40,130), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "19 KGS Count1: "+str(cyl_19_count1), (40,160), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)

      cv2.putText(img, "Count of cylinders2 : "+str(total_count2), (330,40), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "Segregated count2 ", (330,70), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "5 KGS Count2 : "+str(cyl_5_count2), (330,100), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "14 KGS Count2 : "+str(cyl_14_count2), (330,130), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      cv2.putText(img, "19 KGS Count2 : "+str(cyl_19_count2), (330,160), cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
      #print("Total count1",total_count1,count_miss1,cyl_14_count1,cyl_19_count1)
      #print("Total count2",total_count2,count_miss2,cyl_14_count2,cyl_19_count2)
    except Exception as e:
      print("Error in Side model:",str(e))
    compare_countValues()


    #side_img_roi2 = side_roi2.side_model(img,darknet_image,network,class_names)	
    return img,cyl_14_count,cyl_19_count,cyl_5_count,total_count


