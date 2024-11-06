from flask import Flask, Response
import cv2
import pickle
import cvzone
import numpy as np
import os
import time

app = Flask(__name__)

# Ruta a la carpeta de frames
frames_dir = 'frames'

# Cargar los frames en una lista
frames = []
for i in range(20):
    frame_path = os.path.join(frames_dir, f'frame_{i}.jpg')
    if os.path.exists(frame_path):
        img = cv2.imread(frame_path)
        if img is not None:
            frames.append(img)
        else:
            print(f"Error: No se pudo leer la imagen en {frame_path}")
    else:
        print(f"Error: Archivo no encontrado en {frame_path}")

# Verificar que se hayan cargado todos los frames
if len(frames) < 20:
    print("Advertencia: No se cargaron todos los frames.")

# Cargar las posiciones de los parkings desde el archivo pickle
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
                color = (0, 255, 0)  # Verde para espacios disponibles
                thickness = 5
                spaceCounter += 1
            else:
                color = (0, 0, 255)  # Rojo para espacios ocupados
                thickness = 2

            # Dibujar el rectángulo en la imagen final
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
            cvzone.putTextRect(img, str(count), (x1, y2 - 3), scale=1, thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3, thickness=5, offset=20, colorR=(0, 200, 0))

def generate_frames(white_background=False):
    frame_index = 0  # Índice para recorrer los frames

    while True:
        # Obtener el frame actual
        frame = frames[frame_index]
        
        # Crear una imagen blanca para el fondo si se requiere
        img_background = np.ones((frame.shape[0], frame.shape[1], 3), dtype=np.uint8) * 255 if white_background else frame.copy()

        # Procesamiento de la imagen
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        # Marcar los espacios de estacionamiento sobre la imagen de fondo correspondiente
        checkParkingSpace(imgDilate, img_background, white_background)

        # Codificar el frame en JPEG
        ret, buffer = cv2.imencode('.jpg', img_background)
        frame_data = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        
        # Espera de 5 segundos antes de pasar al siguiente frame
        time.sleep(5)
        
        # Actualizar el índice del frame (circular)
        frame_index = (frame_index + 1) % len(frames)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(white_background=False), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_white')
def video_feed_white():
    return Response(generate_frames(white_background=True), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
