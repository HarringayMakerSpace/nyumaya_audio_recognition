import time
import os
import argparse
import sys
import datetime

from libnyumaya import AudioRecognition
from record import AudiostreamSource
from record import RingBuffer

libpath = "../lib/linux/libnyumaya.so"
hotword_graph="../models/Hotword/marvin_small.tflite"
hotword_labels="../models/Hotword/marvin_labels.txt"

numbers_graph="../models/Command/numbers_small.tfile"
numbers_labels="../models/Command/numbers_labels.txt"

action_graph="../models/Command/subset_small.tflite"
action_labels="../models/Command/subset_labels.txt"



def label_stream():

	hotword_detected = False
	countdown = 0

	audio_stream = AudiostreamSource()

	action_detector = AudioRecognition(libpath,action_graph,action_labels)
	hotword_detector = AudioRecognition(libpath,hotword_graph,hotword_labels)
	#
	#action_detector = hotword_detector

	hotword_detector.SetSensitivity(0.5)
	action_detector.SetSensitivity(0.55)
	bufsize = hotword_detector.GetInputDataSize()
	audio_stream.start()

	print("Audio Recognition Version: " + hotword_detector.GetVersionString())
	try:
		while(True):
			frame = audio_stream.read(bufsize,bufsize)
 
			if(not frame):
				time.sleep(0.01)
				continue


			if(countdown > 0):
				countdown -= 1
				if(countdown == 0):
					hotword_detected = False
					print("Stopped Listening")

			if(not hotword_detected):
				prediction = hotword_detector.RunDetection(frame)
				if(prediction):
					hotword_detected = True
					countdown = 20
					now = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
					print("Listening")
			else:
				prediction = action_detector.RunDetection(frame)
				if(prediction):
					print("Got Action: " + action_detector.GetPredictionLabel(prediction))
					countdown = 0
					hotword_detected = False



	except KeyboardInterrupt:
		print("Terminating")
		audio_stream.stop()
		sys.exit(0)

if __name__ == '__main__':
	label_stream()

