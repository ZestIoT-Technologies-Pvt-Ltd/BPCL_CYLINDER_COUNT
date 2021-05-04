#   Copyright (C) 2020 by ZestIOT. All rights reserved. The information in this 
#   document is the property of ZestIOT. Except as specifically authorized in 
#   writing by ZestIOT, the receiver of this document shall keep the information
#   contained herein confidential and shall protect the same in whole or in part from
#   disclosure and dissemination to third parties. Disclosure and disseminations to 
#   the receiver's employees shall only be made on a strict need to know basis.
"""
Input: Configuration file path, Weight file path and meta file path of the cylinder model
Output: Image object, network and Class names, all of them are Darknet objects

User Requirement:
1) Loads Cylinder detection model for side view, top view and truck door view.

Requirements:
1) This function loads the cylinder detection model with the given configuration file,
   Weight file and meta file
2 Returns the Darknet image, network and Class name objects which are inturn to make 
  cylinder detection."""


import darknet
import json
config="BPCL_config.json"
with open(config) as json_data:
	try:
		info= json.load(json_data)
		configPath_side,weightPath_side,metaPath_side= info["side"]["configPath"],info["side"]["weightPath"],info["side"]["metaPath"]
		configPath_top,weightPath_top,metaPath_top= info["top"]["configPath"],info["top"]["weightPath"],info["top"]["metaPath"]
		configPath_truck,weightPath_truck,metaPath_truck= info["truck"]["configPath"],info["truck"]["weightPath"],info["truck"]["metaPath"]
	except Exception as e:
		print("Error in Tracker model:",str(e))

def load_model_side():
	try:
		network, class_names, class_colors = darknet.load_network(configPath_side,metaPath_side,weightPath_side,batch_size=1)
		darknet_image = darknet.make_image(darknet.network_width(network),darknet.network_height(network),3)
	except Exception as e:
		print("Error in Load side model:",str(e))
	return(darknet_image,network,class_names)

def load_model_top():
	try:
		network, class_names, class_colors = darknet.load_network(configPath_top,metaPath_top,weightPath_top,batch_size=1)
		darknet_image = darknet.make_image(darknet.network_width(network),darknet.network_height(network),3)
	except Exception as e:
		print("Error in load top model:",str(e))
	return(darknet_image,network,class_names)

def load_model_truck():
	try:
		network, class_names, class_colors = darknet.load_network(configPath_truck,metaPath_truck,weightPath_truck,batch_size=1)
		darknet_image = darknet.make_image(darknet.network_width(network),darknet.network_height(network),3)
	except Exception as e:
		print("Error in load truck model:",str(e))
	return(darknet_image,network,class_names)
