import cv2
import numpy as np
from pyzbar.pyzbar import decode
from winsound import Beep

# set up the camera and the window that the camera input is displayed in
# '1' links to a secondary camera (either network or webcam) used
# change '1' to '0' if the default system camera should be used instead
cap = cv2.VideoCapture(0)
# sets the resolution
cap.set(3, 640)
cap.set(4, 480)

# list for storing the isbns that have been scanned
my_codes = []

while True:
    try:
        success, img = cap.read()

        for barcode in decode(img):
            # limits barcode type to EAN13 (used for books)
            # this prevents other barcodes and QR codes being scanned
            if barcode.type == "EAN13":
                if not barcode.data.decode("UTF-8") in my_codes:
                    my_codes.append(barcode.data.decode("UTF-8"))
                    Beep(2000, 250)
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (255, 0, 255), 5)
                pts2 = barcode.rect
                cv2.putText(img, barcode.data.decode("UTF-8"), (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, (255, 0, 255), 2)

        cv2.imshow("Results", img)
        cv2.waitKey(5)
    except KeyboardInterrupt:
        break

print(my_codes)
