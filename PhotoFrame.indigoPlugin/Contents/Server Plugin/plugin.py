#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2014, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

import indigo
import os, os.path
import sys
import time

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL.ExifTags import TAGS

from shutil import copyfile
from random import randint
from time import sleep
import datetime as dt


########################################
#Custom procedures
########################################

####Get exif information from file
def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

####Get sorted list of files
def getSortedDir(path, srch, start, finish):

	filter_list = []

	name_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	full_list = [os.path.join(path,i) for i in name_list]
	time_sorted_list = sorted(full_list, key=os.path.getmtime, reverse=True)
	for file in time_sorted_list:
		if file.find(srch) != -1:
			filter_list.append(file) 
	
	if start < 0:
		start = 0

	if finish > len(filter_list):
		finish = len(filter_list)	

	final_list = filter_list[start:finish]
	return final_list

########################################
class Plugin(indigo.PluginBase):
########################################

	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = False

	#########################################
	# Plugin startup and shutdown
	#########################################
	def startup(self):
		self.debugLog(u"startup called")

	def shutdown(self):
		self.debugLog(u"shutdown called")

	#########################################
	# Main Loop
	#########################################
	def runConcurrentThread(self):
		try:
			while True:
				for device in indigo.devices.iter("self"):
					#########################################
					# Variable Setup
					#########################################
					try:						
						PathFrom = device.pluginProps["directory"]
						PathTo = device.pluginProps["destination"]
						PhotoDelay = device.pluginProps["delay"]		
						PhotoGrouping = device.pluginProps["grouping"]

					except:
						pass
					PictureList = []
					
					#########################################
					# Get next photo
					#########################################
					
					PhotoDirectoryTest = os.path.isdir(PathFrom)
					if PhotoDirectoryTest is True:
						FileCount = int(os.popen("ls '" + PathFrom + "'| wc -l").read())
						#indigo.server.log(str(FileCount))
						
						RandFile = randint(0,FileCount)
						if PhotoGrouping:
							RandFileTo = RandFile ++ 10
						else:
							RandFileTo = RandFile ++ 1
						#indigo.server.log(str(PhotoGrouping) + ":" + str(RandFile) + ":" + str(RandFileTo))
						PictureList = getSortedDir(PathFrom, ".jpg", RandFile, RandFileTo)
					else:
						indigo.server.log("Photo directory not found")
					
					#########################################
					# Picture Loop
					#########################################

					#indigo.server.log(str(len(PictureList)))
					for FileFrom in PictureList:
						
						#########################################
						# Pause Photo
						#########################################
						device.refreshFromServer()
						PhotoState = device.states["state"]		
						while PhotoState == "Paused":
							self.sleep(.5)
							device.refreshFromServer()
							PhotoState = device.states["state"]

						Filename, file_extension = os.path.splitext(FileFrom)
					
						#########################################
						# Adjust Image Size
						#########################################
					
						img = Image.open(FileFrom)
						old_size = img.size

						new_size = (600, 400)
						new_img = Image.new("RGB", new_size, "black")

						border_size = (604, 404)
						border_img = Image.new("RGB", border_size, "white")

						if (old_size[0] > new_size[0]) or (old_size[1] > new_size[1]):
							per_dem = (float(new_size[0])/float(old_size[0]), float(new_size[1])/float(old_size[1]))
						else:
 							per_dem = (float(old_size[0])/float(new_size[0]), float(old_size[1])/float(new_size[1]))

						if per_dem[0] > per_dem[1]:
							percent = per_dem[1]
						else:
							percent = per_dem[0]

						recalc_size = (int(old_size[0]*percent),int(old_size[1]*percent))
						img = img.resize(recalc_size)

						final_size  = img.size 
						
						#########################################
						# Create Black Border
						#########################################
					
						BorderWidth = int((new_size[0] - final_size[0])/2)
						BorderHeight = int((new_size[1] - final_size[1])/2)
						new_img.paste(img, (BorderWidth,BorderHeight))

						#########################################
						# Create White Border
						#########################################
					
						BorderWidth = 2
						BorderHeight = 2
						border_img.paste(new_img, (BorderWidth,BorderHeight))
						
						#########################################
						# Set Name and Date
						#########################################
						device.refreshFromServer()
						PhotoState = device.states["state"]
						if PhotoState:
							try:
								PictureData = get_exif(FileFrom)
								PictureDate = PictureData["DateTime"]
								device.updateStateOnServer("date", value=PictureDate)
							except:
								device.updateStateOnServer("date", value="Unknown")

							border_img.save(PathTo,optimize=True,quality=75)
							#PictureDate = os.path.getmtime(FileFrom)
							PicturePath, PictureName = os.path.split(FileFrom)
							device.updateStateOnServer("name", value=PictureName)
							
						self.sleep(6)
					
					#########################################
					# End device loop
					#########################################		
					#self.sleep(6)
					
		except self.StopThread:
			indigo.server.log("thread stopped")
			pass
	
	################################################################################
	# Plugin menus
	################################################################################
	
	#########################################
	# Plugin Actions object callbacks
	#########################################
	def PhotoToggle(self, pluginAction):
		dev = indigo.devices[pluginAction.deviceId]
		state = dev.states["state"]
		
		if state == "Playing":
			indigo.server.log("Pause Photo Album")
			dev.updateStateOnServer("state", value="Paused")
		else:
			indigo.server.log("Play photo album")
			dev.updateStateOnServer("state", value="Playing")


