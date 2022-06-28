import mss
import mss.tools
import cv2
import numpy as np
import time
import win32gui
import win32con
from tkinter import *


def showImg(img):
	cv2.imshow("image", img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def crop(img, x, y, width, height):
	imgWidth = len(img[0])
	imgHeight = len(img)
	return img[
		int(y*imgHeight):int(y*imgHeight+height*imgHeight),
		int(x*imgWidth):int(x*imgWidth+width*imgWidth),
		:
	]

def screenshot(x, y, width, height):

	# Use the 1st monitor
	monitor = sct.monitors[0]

	bbox = (
		int(monitor["width"] * x),
		int(monitor["height"] * y),
		int(monitor["width"] * x + monitor["width"] * width),
		int(monitor["height"] * y + monitor["height"] * height),
	)

	img = np.array(sct.grab(bbox))[:,:,:3]

	# showImg(img)

	return img


def pixelMatch(img, match, precision):
	avg = [0, 0, 0]
	total = 0
	for row in img:
		for pixel in row:
			avg += pixel
			total += 1
	imgAvg = avg/total
	similarity = np.sum(np.abs(imgAvg-match))
	# print(imgAvg)
	# print(similarity)
	return similarity <= precision

buffMarker = [29.22517, 54.64408, 62.39501]
emptyBuff = [40, 55, 52]
spawnTimer = 145

WIDTH = 370
HEIGHT = 370

RED = '#FCC'
BLUE = '#8EF'

buffs = [
	{
		'name': 'Blue Gromp',
		'color': BLUE,
		'mapPosition': [0, 0.39, 0.05, 0.045],
		'spawned': False,
		'timer': 97,
		'killed': time.time(),
		'overlayPos': [0.16,0.48],
	},
	{
		'name': 'Blue Wolves',
		'color': BLUE,
		'mapPosition': [0.143, 0.575, 0.05, 0.045],
		'spawned': False,
		'timer': 90,
		'killed': time.time(),
		'overlayPos': [0.25,0.6],
	},
	{
		'name': 'Blue Raptors',
		'color': BLUE,
		'mapPosition': [0.445, 0.69, 0.05, 0.045],
		'spawned': False,
		'timer': 90,
		'killed': time.time(),
		'overlayPos': [0.42,0.65],
	},
	{
		'name': 'Blue Krugs',
		'color': BLUE,
		'mapPosition': [0.564, 0.96, 0.05, 0.045],
		'spawned': False,
		'timer': 97,
		'killed': time.time(),
		'overlayPos': [0.49,0.83],
	},
	{
		'name': 'Red Gromp',
		'color': RED,
		'mapPosition': [0.945, 0.585, 0.05, 0.045],
		'spawned': False,
		'timer': 97,
		'killed': time.time(),
		'overlayPos': [0.85,0.51],
	},
	{
		'name': 'Red Wolves',
		'color': RED,
		'mapPosition': [0.805, 0.395, 0.05, 0.045],
		'spawned': False,
		'timer': 90,
		'killed': time.time(),
		'overlayPos': [0.74,0.37],
	},
	{
		'name': 'Red Raptors',
		'color': RED,
		'mapPosition': [0.503, 0.275, 0.05, 0.045],
		'spawned': False,
		'timer': 90,
		'killed': time.time(),
		'overlayPos': [0.59,0.35],
	},
	{
		'name': 'Red Krugs',
		'color': RED,
		'mapPosition': [0.385, 0.01, 0.05, 0.045],
		'spawned': False,
		'timer': 97,
		'killed': time.time(),
		'overlayPos': [0.51,0.15],
	},
]

def campExists(img):
	return pixelMatch(img, buffMarker, 5)

def campMissing(img):
	return pixelMatch(img, emptyBuff, 5)



root = Tk()
root.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, 2560-WIDTH, 1440-HEIGHT))
root.wait_visibility(root)
root.wm_attributes('-topmost', True)
root.wm_attributes("-disabled", True)
root.wm_attributes("-transparentcolor", "silver")
root.overrideredirect(True)

canvas = Canvas(root, width=WIDTH, height=HEIGHT, bd=0, highlightthickness=0)
canvas.pack()
canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="silver", outline="silver")

for buff in buffs:
	buff['canvasText'] = canvas.create_text(WIDTH*buff['overlayPos'][0], HEIGHT*buff['overlayPos'][1], text=buff['timer'], fill=buff['color'], font=("Candara", "14"))

hwnd = win32gui.FindWindow(None, "tk")
lExStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
lExStyle |=  win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE , lExStyle )


with mss.mss() as sct:
	while True:
		print('~~~~~~~~~~~~~~')
		time.sleep(1)
		img = screenshot(0.879, 0.788, 0.10, 0.165)
		# img = cv2.imread("screenshot.png")[...,::-1]
		for buff in buffs:
			buffPic = crop(img, *buff['mapPosition'])
			if campMissing(buffPic):
				if buff['spawned']:
					buff['spawned'] = False
					buff['timer'] = spawnTimer
					buff['killed'] = time.time()
					print('detected camp death')
				else:
					buff['timer'] = int(spawnTimer - (time.time() - buff['killed']))
			elif campExists(buffPic):
				buff['spawned'] = True
				buff['timer'] = 0
			else:
				if not buff['spawned']:
					buff['timer'] = int(spawnTimer - (time.time() - buff['killed']))

			if buff['timer'] <= 0:
				buff['spawned'] = True

			print(buff['name'] + ': ' + str(round(buff['timer'])))

			text = buff['timer'] if buff['timer'] > 0 else ''
			canvas.itemconfigure(buff['canvasText'], text=text)
		root.update()
