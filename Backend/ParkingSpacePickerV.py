import cv2
import pickle

try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []

temp_points = [] 

def mouseClick(events, x, y, flags, params):
    global temp_points

    if events == cv2.EVENT_LBUTTONDOWN:
        temp_points.append((x, y))

        if len(temp_points) == 2:
            posList.append((temp_points[0], temp_points[1]))
            temp_points = []  

    if events == cv2.EVENT_RBUTTONDOWN:
        if posList:
            posList.pop()  

    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)

#cap = cv2.VideoCapture(r'C:/Users/SSD/Desktop/cimpark/backend/cimpark.mp4')  
cap = cv2.VideoCapture('rtsp://10.32.91.192:554/title')

ret, frame = cap.read()

cap.release()

if not ret:
    print("Error al leer el video.")
else:
    while True:
        img = frame.copy()  

        for rect in posList:
            if isinstance(rect[0], tuple) and isinstance(rect[1], tuple):
                cv2.rectangle(img, rect[0], rect[1], (255, 0, 255), 2)

        for point in temp_points:
            cv2.circle(img, point, 5, (0, 255, 0), -1)

        cv2.imshow("Frame", img)
        cv2.setMouseCallback("Frame", mouseClick)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
