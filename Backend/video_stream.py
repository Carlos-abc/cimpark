from flask import Flask, Response
import cv2
import pickle
import cvzone
import numpy as np

app = Flask(__name__)

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

def checkParkingSpace(imgPro, img, white_background=False):
    spaceCounter = 0

    for pos in posList:
        if isinstance(pos[0], tuple) and isinstance(pos[1], tuple):
            x1, y1 = pos[0]
            x2, y2 = pos[1]
            imgCrop = imgPro[y1:y2, x1:x2]
            count = cv2.countNonZero(imgCrop)

            if count < 900:
                color = (0, 255, 0)  
                thickness = 5
                spaceCounter += 1
            else:
                color = (0, 0, 255)  
                thickness = 2

            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
            cvzone.putTextRect(img, str(count), (x1, y2 - 3), scale=1, thickness=2, offset=0, colorR=color)

def generate_frames(white_background=False):
    #cap = cv2.VideoCapture('carPark.mp4')  
    cap = cv2.VideoCapture('rtsp://10.32.91.192:554/title')
    
    while True:
        ret, img = cap.read()
        if not ret:
            cap.release()  
            cap = cv2.VideoCapture('carPark.mp4')
            continue

        if white_background:
            img_background = np.ones((img.shape[0], img.shape[1], 3), dtype=np.uint8) * 255
        else:
            img_background = img.copy()

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        checkParkingSpace(imgDilate, img_background, white_background)

        ret, buffer = cv2.imencode('.jpg', img_background)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(white_background=False), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_white')
def video_feed_white():
    return Response(generate_frames(white_background=True), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
