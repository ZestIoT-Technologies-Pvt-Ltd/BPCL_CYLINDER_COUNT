from time import sleep, strftime, time
import matplotlib.pyplot as plt
from pyspectator.processor import Cpu
import imageio
import time
from time import sleep
import os
import cv2
import numpy as np
import glob
import matplotlib.dates as mdates

import matplotlib
#matplotlib.use('Agg')

cpu = Cpu(monitoring_latency=1) #changed here
from csv import DictReader
plt.ion()
#x = []
#y = []
filenames = []
pres_value = 0
prev_value = 0


def graph(temp,count):
    global x,y, pres_value,prev_value
    y.append(count)
    #send_time = strftime("%Y-%m-%d %H:%M:%S")
    #print("send_time",send_time)
    x.append(temp)



    #plt.savefig('plot.png', dpi=300, bbox_inches='tight')
    #pres_value = count
    #diff = pres_value - prev_value
    #if diff == 30:
    	#x = []
    	#y = []
    	#filename = f'{count}.png'
    	#filenames.append(filename)
    	#plt.savefig(filename)
    	#prev_value = pres_value
    #plt.show()



count = 0

while True:
    files = os.listdir("graph_plots")

    #print(files)

    sorted_files = sorted(files)
    #print(sorted_files)
    print(sorted_files[0])
    first_file = sorted_files[0]
    file_sorted = "graph_plots/"+str(first_file)
    split_file = first_file.split(".")
    with open(file_sorted, 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        x = []
        y = []
        print(x,y)
        for row in csv_dict_reader:
            #print(row['Time'], row['x-Coordinates'])
            x.append(row['Time'])
            y.append(row['x-Coordinates'])
        	#cpu = Cpu(monitoring_latency=1) #changed here
        	#temp = cpu.temperature
        	#print(temp)
        	#write_temp(temp)
            #graph(time_stamp,x_centroid)
            #plt.pause(0.1)
            #print("h1")
            #count = count+1
            #print("count",count)
    plt.cla()
    plt.clf()
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=25))
    plt.scatter(x,y)
    plt.plot(x,y)
    #plt.ylim(2021-03-01 19:42:37,2021-03-01 19:57:37)
    #plt.draw()
    plt.xlabel('Time')
    plt.ylabel('x-Coordinates')
    plt.title('Time vs x-Coordinates')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plot_img_save = "plotted_graphs/"+str(split_file[0])+".png" 
    plt.savefig(plot_img_save, dpi=300, bbox_inches='tight')
    plt.close()
    try:
        os.remove(file_sorted)
    except:
        pass
#with imageio.get_writer('mygif.gif', mode='I') as writer:
    #for filename in filenames:
        #image = imageio.imread(filename)
        #writer.append_data(image)

#img_array = []
#for filename in filenames:
    #img = cv2.imread(filename)
    #height, width, layers = img.shape
    #size = (width,height)
    #img_array.append(img)

#out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 10, size)

#for i in range(len(img_array)):
    #out.write(img_array[i])
#out.release()

#for filename in set(filenames):
    #os.remove(filename)
#print('DONE')
