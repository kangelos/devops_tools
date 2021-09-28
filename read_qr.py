#!/usr/bin/python3

"""
angelos@unix.gr
pylint --disable=I1101 readQR.py
"""
import sys
from time import sleep
from selenium import webdriver
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

# globals suck
DEBUG = True
TITLE = "angelos@unix.gr rocks the QR scanners "
# milliseconds to wait for video update on non important stuff
WAITKEY = 13
# milliseconds to wait on successful scan
WAITKEY_LONG = 1300
# how long to wait until the browser returns to the home page
BROWSER_WAIT = 3


def display(im, decoded_objects):
    """
    Draw the containing polygon
    """
    # Loop over all decoded objects
    for decoded_object in decoded_objects:
        points = decoded_object.polygon
        n = len(points)
        for j in range(0, n):
            cv2.line(im, points[j], points[(j+1) % n], (255, 0, 0), 3)

    # Display results
    cv2.imshow(TITLE, im)
    cv2.waitKey(WAITKEY)


def qr_scan(device=0):
    """
    Main QR reader
    """
    chrome = webdriver.Chrome()  # create browser
    chrome.set_window_position(0, 0)
    chrome.execute_script("document.title = '%s'" % TITLE)

    # set up camera object
    cap = cv2.VideoCapture(int(device))
    cv2.namedWindow(TITLE)
    cv2.moveWindow(TITLE, 1000, 200)

    while True:
        url = None
        # get the image
        _, img = cap.read()
        decoded_objects = pyzbar.decode(img)
        for obj in decoded_objects:
            if str(obj.type) == "QRCODE":
                url = str(obj.data.decode("utf-8"))
        display(img, decoded_objects)

        # nothing to see here move on
        if url is None:
            continue
        # did we get a proper URL ?
        if str(url) == '':
            # nothing to see here move on
            continue

        # fresh scanned
        print("SCANNED DATA:%s" % url)

        cv2.putText(img, str(url),
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 80, 0), 2)
        cv2.imshow(TITLE, img)

        chrome.get(url)
        chrome.execute_script("document.title = '%s'" % TITLE)

        # work until a q is pressed
        if cv2.waitKey(WAITKEY_LONG) == ord("q"):
            break

    # free camera object and exit
    sleep(1)  # give the chrome thread time to exit
    cap.release()
    cv2.destroyAllWindows()


# select the video camera
if __name__ == "__main__":
    if len(sys.argv) == 2:
        qr_scan(sys.argv[1])
    else:
        qr_scan(0)
