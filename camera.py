import cv2
import numpy as np
import time
import datetime
import imutils
import os
import settings
import communication

video_stream = cv2.VideoCapture(0)
video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

frame_count = 0
previous_frame = None


def initialize_video_stream():
    pass
    # global video_stream
    # video_stream = cv2.VideoCapture(0)


def detect_motion():
    global previous_frame
    global frame_count
    while True:
        if settings.operation_mode == "auto":
            # Check phone-related functionality in the future
            pass

        while settings.operation_mode == "disable":
            time.sleep(5)

        ret, current_frame = video_stream.read()
        if previous_frame is None:
            previous_frame = current_frame

        gray_diff = cv2.absdiff(cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY),
                                cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY))
        threshold_img = cv2.threshold(gray_diff, 25, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(threshold_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < 10000:
                continue
            if cv2.contourArea(contour) >= (current_frame.shape[0] - 10) * (current_frame.shape[1] - 10):
                print("Area too large")
                continue
            print("MOTION DETECTED")
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(current_frame, (x, y), (x + w, y + h), (0, 255, 0))
            motion_detected = True

        if motion_detected:
            print("Motion detected")
            filename = "drive/" + str(datetime.datetime.now()) + "_MOTION.jpg"
            cv2.imwrite(filename, current_frame)
            communication.transmit(["MotionChannel", "image", filename])
            frame_count = 0

        if frame_count > settings.LogInterval:
            print("Saving frame")
            filename = "drive/" + str(datetime.datetime.now()) + "_MOTION.jpg"
            cv2.imwrite(filename, current_frame)
            communication.transmit(["GeneralChannel", "image", filename])
            frame_count = 0

        frame_count += settings.PictureInterval
        time.sleep(settings.PictureInterval)
        previous_frame = current_frame


def capture_image():
    ret, snapshot = video_stream.read()
    cv2.imwrite("/dev/shm/snapshot.png", snapshot)
    return "/dev/shm/snapshot.png"
