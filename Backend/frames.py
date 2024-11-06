import cv2
import os

# Ruta del video y carpeta de salida para frames
video_path = 'carPark.mp4'  # Ajusta el nombre del video si es necesario
frames_dir = r'C:/Users/SSD/Desktop/cimpark/backend/frames'

# Crear la carpeta de frames si no existe
os.makedirs(frames_dir, exist_ok=True)

# Cargar el video
cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_interval = total_frames // 20  # Espaciado entre frames para capturar 20

# Guardar 20 frames espaciados
for i in range(20):
    frame_number = i * frame_interval
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        frame_path = os.path.join(frames_dir, f'frame_{i}.jpg')
        cv2.imwrite(frame_path, frame)
        print(f"Guardado: {frame_path}")
    else:
        print(f"Error: No se pudo leer el frame {frame_number}")

cap.release()
print("Frames generados exitosamente.")
