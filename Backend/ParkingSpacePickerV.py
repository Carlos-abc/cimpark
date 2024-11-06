import cv2
import pickle

# Inicializamos la lista de posiciones y los puntos temporales
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []

temp_points = []  # Almacenará los dos puntos temporales del rectángulo

def mouseClick(events, x, y, flags, params):
    global temp_points

    if events == cv2.EVENT_LBUTTONDOWN:
        # Almacenar el punto cuando se haga clic izquierdo
        temp_points.append((x, y))

        # Si se han seleccionado dos puntos, guardamos el rectángulo
        if len(temp_points) == 2:
            # Guardamos las coordenadas como tuplas
            posList.append((temp_points[0], temp_points[1]))
            temp_points = []  # Reiniciamos la lista temporal para futuros clics

    if events == cv2.EVENT_RBUTTONDOWN:
        # Eliminar el último rectángulo si se hace clic derecho
        if posList:
            posList.pop()  # Elimina el último rectángulo

    # Guardar la lista de posiciones actualizadas
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)

# Capturamos video desde un archivo MP4
# Para hacerlo funcionar con RTSP, reemplaza esta línea con la URL de tu flujo RTSP
cap = cv2.VideoCapture(r'C:/Users/SSD/Desktop/cimpark/backend/carPark.mp4')  # Reemplaza con la ruta de tu archivo MP4
#cap = cv2.VideoCapture('rtsp://10.32.151.190:554/title')

# Leer solo el primer frame del video
ret, frame = cap.read()

# Liberar el video ya que no necesitamos más frames
cap.release()

if not ret:
    print("Error al leer el video.")
else:
    while True:
        img = frame.copy()  # Hacemos una copia del frame para evitar dibujar permanentemente sobre la imagen original

        # Dibujar los rectángulos guardados con dos puntos
        for rect in posList:
            if isinstance(rect[0], tuple) and isinstance(rect[1], tuple):
                cv2.rectangle(img, rect[0], rect[1], (255, 0, 255), 2)

        # Dibujar los puntos temporales seleccionados (para visualizar al crear un nuevo rectángulo)
        for point in temp_points:
            cv2.circle(img, point, 5, (0, 255, 0), -1)

        # Mostrar la imagen del primer frame con los rectángulos
        cv2.imshow("Frame", img)
        cv2.setMouseCallback("Frame", mouseClick)

        # Presiona 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cerrar todas las ventanas
    cv2.destroyAllWindows()
