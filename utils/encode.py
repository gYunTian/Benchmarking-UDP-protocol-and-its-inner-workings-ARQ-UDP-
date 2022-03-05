# https://www.youtube.com/watch?v=nr3bZdL0aCs

# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames
import cv2

vid = cv2.VideoCapture("../data/video.mp4")

while (vid.isOpened()):
  ret, frame = vid.read()
  cv2.imshow('frame', frame)
