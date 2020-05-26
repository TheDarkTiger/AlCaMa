#! coding: utf-8
#! python3
# Guillaume Viravau 2020
# A small cript to generate caption and/or albums from simple json file


import os
import json
from PIL import Image, ImageDraw, ImageFont

file = r"test\album.json"
album = None

def load_album_data( file=None ) :
	global album
	
	# Default values
	album = {
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
			"size":[320,320],
			"style":"text",
			"font-family":["Verdana", "sans-serif"],
			"color":"#000",
			"background-color":"#FFF"
		}
	}
	
	# Reading the file
	if file is not None :
		with open( file, "r" ) as rf :
			data = json.load( rf )
			
		print( data )
	

def picture_process( picture=None ) :
	global album
	
	print( picture )
	img = Image.new( "RGB", album["configuration"]["size"], color=(255,255,255) )
	
	draw = ImageDraw.Draw( img )
	font = ImageFont.truetype( "tahoma.ttf", 12, encoding="unic" )
	
	text = picture["data"]["caption"]
	draw.text( (0,0), text, font=font, fill=(0,0,0) )
	
	filename = album["name"]+"_"+os.path.split(picture["file"])[1]
	print( filename )
	img.save( filename )
	


#===============================================================================
# Main

print( "plop" )
print( album )

file = os.path.abspath( file )
albumFolder = os.path.dirname( file )
print( albumFolder )
load_album_data( file )


index = 0
for picture in album["pictures"] :
	print( picture+" :" )
	picture_process( {"file":os.path.join(albumFolder, picture), "index":index, "data":album["pictures"][picture]} )
	index += 1
	


