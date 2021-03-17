#! coding: utf-8
#! python3
# Guillaume Viravau 2020-2021
# A small script to generate caption and/or albums from json file

import os
import json
from PIL import Image, ImageDraw, ImageFont


def album_load_data( file=None ) :
	
	# Default values
	data = {
		"name":"Hollidays",
		"pictures":
		{
			"scotland.jpg":{"caption":"Shigiddy whoo!"},
			"japan.jpg":{"caption":"Zen"},
			"london.jpg":{"caption":"Fish and chips!"},
			"paris.jpg":{"caption":"Loveliest town in the world."}
		},
		"configuration":
		{
			"size":[800,800],
			"padding":16,
			"style":"text",
			"font-size":20,
			"font-family":["Verdana", "sans-serif"],
			"color":"#000",
			"background-color":"#FFF"
		}
	}
	
	# Reading the file
	if file is not None :
		with open( file, "r" ) as rf :
			data = json.load( rf )
			
		
	
	return data


def album_generate( album=None):
	index = 0
	for picture in album["pictures"] :
		print( picture+" :" )
		picture_process( {"file":os.path.join(albumFolder, picture), "index":index, "data":album["pictures"][picture]} )
		index += 1
	

def picture_process( picture=None ) :
	global album
	
	if picture != None :
		print( picture )
		
		size = album["configuration"]["size"]
		padding = album["configuration"]["padding"]
		
		im = Image.open( picture["file"] )
		x = padding
		y = padding
		sw = size[0] -(2*padding)
		sh = size[1] -(2*padding)
		
		if im.size[0] > im.size[1] :
			u = 1
			v = im.size[1] / im.size[0]
		else :
			u = im.size[0] / im.size[1]
			v = 1
		
		w = int((sw*u))
		h = int((sh*v))
		
		size[1] += 2*int( album["configuration"]["font-size"] )
		
		
		
		print( f"{u} {v}, {w} {h}" )
		
		img = Image.new( "RGB", size, color=(250,250,250) )
		img.paste( im.resize( (w,h) ), (x,y) )
		
		draw = ImageDraw.Draw( img )
		font = ImageFont.truetype( "tahoma.ttf", album["configuration"]["font-size"], encoding="unic" )
		
		text = picture["data"]["caption"]
		draw.text( (padding, h+(2*padding)), text, font=font, fill=(0,0,0) )
		
		filename = album["name"]+"_"+os.path.split(picture["file"])[1]
		print( filename )
		img.save( filename )
	


#===============================================================================
# Main

if __name__ == "__main__" :
	print( "AlCaMa" )
	
	file = r"test\album.json"
	file = os.path.abspath( file )
	
	albumFolder = os.path.dirname( file )
	print( albumFolder )
	album = album_load_data( file )
	
	album_generate( album )
	

