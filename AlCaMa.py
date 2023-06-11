#!/usr/bin/env python
#! coding: utf-8
#! python3
# Guillaume Viravau 2020-2023
# A small script to generate caption and/or albums from json file

import os
import json
import copy
import argparse
from PIL import Image, ImageDraw, ImageFont


def parse_arguments():
	"""
	Parses the arguments
	"""
	
	parser = argparse.ArgumentParser( description="Creates album from JSON" )
	
	parser.add_argument( '-i', "--json", action="store", dest="input_json", help="Json to read", default=None )
	
	parser.add_argument( '-o', '--output-folder', action="store", dest="output_folder", help="Folder to save album to", default=None )
	parser.add_argument( '-v', '--verbose', action="store_true", dest="verbose", help="Verbose output", default=False )
	
	return parser.parse_args()


def colorOf( string=None ) :
	"""Convert a color from a string to an RGB"""
	color = (0,0,0)
	if string is not None :
		
		# '#' familly
		if string[0] == '#':
			# Format : "#17B"
			if len(string) == 4:
				# Convert "#17B" to "#1177BB"
				string = "#"+(string[1]*2)+(string[2]*2)+(string[3]*2)
			
			# Format : "#1278BC"
			if len(string) == 7:
				color = ( int(string[1:3], 16), int(string[3:5], 16), int(string[5:7], 16) )
			
		
		# 'rgb()' familly
		if string.startswith("rgb("):
			if (string[-1] == ")") and (string.count(",") == 2) :
				# Is it 'Pythonic' enought for you now?
				r,g,b = [int(a.strip()) for a in string[4:-1].split(",")]
				color = (r, g, b)
			else :
				print( "Malformed color : "+string )
		
		# 'hsl()' familly
	
	return color

def album_load_data( file=None ) :
	
	# Reading the file
	if file is not None :
		with open( file, "r" ) as rf :
			data = json.load( rf )
			
		
	
	# Default values
	if "name" not in data :
		data["name"] = "Unnamed"
	
	default = {
			"file-format":"webp",
			"size":[800,800],
			"padding":16,
			"style":"polaroid",
			"picture-style":"contain",
			"picture-align":"center",
			"font-size":20,
			"font-family":["Verdana", "sans-serif"],
			"color":"#111",
			"background-color":"#FAFAFA"
		}
	if "configuration" not in data :
		data["configuration"] = copy.deepcopy( default )
	else :
		for parameter in default :
			if parameter not in data["configuration"] :
				data["configuration"][parameter] = default[parameter]
				print("added "+parameter)
	
	return data


def album_generate( album=None ):
	index = 0
	for picture in album["pictures"] :
		print( picture+" : ", end="" )
		
		picturePath = os.path.join(albumFolder, picture)
		configuration = {}
		configuration = copy.deepcopy( album["configuration"] )
		configuration["album-name"] = album["name"]
		configuration["index"] = index
		configuration["file"] = picturePath
		
		for parameter in album["pictures"][picture] :
			configuration[parameter] = album["pictures"][picture][parameter]
		
		if os.path.exists(picturePath) :
			picture_process( configuration )
		else :
			print("File not found")
		index += 1
	

def picture_process( picture=None ) :
	
	if picture != None :
		print( picture )
		
		# Style Polaroid
		if  picture["style"] == "polaroid" :
			# Polaroid
			# Full   : 164*200 -> h   = w * 1.22
			# Pading : 10      -> pad = w * 0.06
			# Image  : 144*147 -> hp  = wp * 1.02
			# Text   : 144*23
			# coords={}
			# coords["image"] = (0,0, 164,200)
			# coords["picture"] = (10,10, 10+144,10+147)
			# coords["text"] = (10,167, 10+144,167+23)
			
			size = picture["size"]
			padding = picture["padding"]
			
			W = size[0]
			H = int(W * 1.22)
			pad = int(W * 0.06)
			
			# start, stop
			coords={}
			coords["image"] = (0,0, W,H)
			coords["picture"] = (pad,pad, W-pad,pad+int(W*0.89))
			coords["text"] = (pad,(2*pad)+int(W*0.89), W-pad,H-pad)
			
			img = Image.new( "RGB", coords["image"][2:4], color=colorOf(picture["background-color"]) )
			draw = ImageDraw.Draw( img )
			
			# Picture
			draw.rectangle( coords["picture"], fill=(200,200,200), outline=None )
			
			# Get image and infos
			im = Image.open( picture["file"] )
			ratio = "landscape"
			
			pictureStyle = "contain"
			if "picture-style" in picture : pictureStyle = picture["picture-style"]
			
			# contain : Aspect ration is kept, whole image is visible, even if showing background
			if pictureStyle == "contain" :
				x,y = coords["picture"][0:2]
				sw,sh = coords["picture"][2:4]
				sw -= x
				sh -= y
				
				if im.size[0] > im.size[1] :
					ratio = "horizontal"
					u = 1
					v = im.size[1] / im.size[0]
				else :
					ratio = "vertical"
					u = im.size[0] / im.size[1]
					v = 1
				
				w = int((sw*u))
				h = int((sh*v))
				
			# cover   : Aspect ration is kept, no more background is visible, even if part of the image is hidden
			elif pictureStyle == "cover" :
				x,y = coords["picture"][0:2]
				sw,sh = coords["picture"][2:4]
				sw -= x
				sh -= y
				
				if im.size[0] > im.size[1] :
					ratio = "vertical"
					u = im.size[0] / im.size[1]
					v = 1
				else :
					ratio = "horizontal"
					u = 1
					v = im.size[1] / im.size[0]
				
				w = int((sw*u))
				h = int((sh*v))
				
			# stretch : The image takes all the space, even if distorded
			else:
				x,y = coords["picture"][0:2]
				sw,sh = coords["picture"][2:4]
				w = sw-x
				h = sh-y
			
			# top middle bottom
			# left center right
			align = "center"
			if "picture-align" in picture : align = picture["picture-align"]
			print(align + " " + ratio)
			
			if ratio == "horizontal" :
				# top middle bottom
				if align == "center" :
					y = coords["picture"][1]+int((sh-(sh*v))/2)
				elif align == "bottom-right" :
					y = coords["picture"][3]-int(sh*v)
				else :
					y = coords["picture"][1]
			else :
				# left center right
				if align == "center" :
					x = coords["picture"][0]+int((sw-(sw*u))/2)
				elif align == "bottom-right" :
					x = coords["picture"][2]-int(sw*u)
				else :
					x = coords["picture"][0]
			
			print( f"{x} {y}, {w} {h}" )
			
			# TODO : .crop((x,y, x+w, y+h))
			img.paste( im.resize( (w,h) ), (x,y) )
			
			# Text
			draw.rectangle( coords["text"], fill=(200,200,200), outline=None )
			font = ImageFont.truetype( "tahoma.ttf", picture["font-size"], encoding="unic" )
			
			text = picture["caption"]
			draw.text( coords["text"][0:2], text, font=font, fill=colorOf(picture["color"]) )
			
		# Default is text
		else :
			print("No style found. Using 'text'")
			img = Image.open( picture["file"] )
			draw = ImageDraw.Draw( img )
			font = ImageFont.truetype( "tahoma.ttf", picture["font-size"], encoding="unic" )
			text = picture["caption"]
			draw.text( (0,0), text, font=font, fill=colorOf(picture["color"]) )
			
		
		filename = picture["album-name"]+"_"+str(picture["index"])+"."+picture["file-format"]
		print( filename )
		img.save( filename )
	


#===============================================================================
# Main

if __name__ == "__main__" :
	arguments = parse_arguments()
	print( "AlCaMa" )
	print( arguments )
	
	if arguments.input_json != None :
		file = arguments.input_json
		if os.path.exists( file ) :
			if os.path.isfile( file ) :
				file = os.path.abspath( file )
				
				albumFolder = os.path.dirname( file )
				print( albumFolder )
				album = album_load_data( file )
				
				album_generate( album )
			else:
				print( f"{file} is not a file" )
				
		else:
			print( f"{file} does not exists" )
			
		
	else:
		print( "No input file given" )
		
	

