from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
from picamera2 import Picamera2
import socket
import time
import threading

# Global variable to track if the task is running
is_running = False

# Function to calculate the Eye Aspect Ratio (EAR) which helps in detecting drowsiness
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])  # Distance between vertical eye landmarks
    B = distance.euclidean(eye[2], eye[4])  # Another vertical eye landmark distance
    C = distance.euclidean(eye[0], eye[3])  # Distance between horizontal eye landmarks
    ear = (A + B) / (2.0 * C)  # Calculate EAR
    return ear

# Function to handle the drowsiness detection task
def run_task():
    global is_running
    while is_running:
        # Initialize TCP client socket and connect to Flask server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('172.20.10.3', 5010))  # Server IP and port
        
        # Threshold and frame checks for drowsiness
        thresh = 0.25
        frame_check = 2

        # Initialize Dlib face detector and facial landmark predictor
        detect = dlib.get_frontal_face_detector()
        predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

        # Define landmarks for left and right eyes
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

        # Initialize Picamera2 to capture frames
        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration())
        picam2.start()

        flag = 0  # Counter for frames where drowsiness is detected

        try:
            while is_running:
                # Capture frame from camera
                frame1 = picam2.capture_array()
                frame = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                frame = imutils.resize(frame, width=450)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces in the grayscale frame
                subjects = detect(gray, 0)
                for subject in subjects:
                    # Get the facial landmarks
                    shape = predict(gray, subject)
                    shape = face_utils.shape_to_np(shape)

                    # Extract eye regions
                    leftEye = shape[lStart:lEnd]
                    rightEye = shape[rStart:rEnd]

                    # Calculate EAR for both eyes
                    leftEAR = eye_aspect_ratio(leftEye)
                    rightEAR = eye_aspect_ratio(rightEye)
                    ear = (leftEAR + rightEAR) / 2.0

                    # Draw eye contours on the frame
                    leftEyeHull = cv2.convexHull(leftEye)
                    rightEyeHull = cv2.convexHull(rightEye)
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                    
                    data = "False"  # Default status is not drowsy
                    
                    # If EAR is below threshold, start counting frames for drowsiness
                    if ear < thresh:
                        flag += 1
                        if flag >= frame_check:
                            # Mark the frame as drowsy after a number of frames below threshold
                            cv2.putText(frame, "****************ALERT!****************", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.putText(frame, "****************ALERT!****************", (10, 325),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            print("Drowsy")
                            drowsy_status = True
                            data = str(drowsy_status)  # Send "True" for drowsy
                        else:
                            drowsy_status = False
                            data = str(drowsy_status)
                    else:
                        flag = 0
                    
                    # Send drowsy status to server
                    client_socket.sendall(data.encode('utf-8'))
                    print(f'sent: {data}')
                    time.sleep(2)  # Delay between sends
                
                # Display the frame with eye contours
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

        finally:
            # Ensure proper resource cleanup after task completion
            client_socket.close()
            cv2.destroyAllWindows()
            picam2.stop()
            picam2.close()

    print("Task stopped")
    
# Function to handle incoming TCP signals to start/stop the drowsiness task
def wait_for_signal(client_socket):
    global is_running
    while True:
        # Receive messages from the server
        message = client_socket.recv(1024).decode('utf-8')
        if message == "start_signal":
            # Start the task if it isn't already running
            if not is_running:
                print(f"Received message: {message}")
                is_running = True
                threading.Thread(target=run_task).start()
            else:
                print("Task is already running")
        elif message == "stop_signal":
            # Stop the task if it is running
            if is_running:
                print(f"Received message: {message}")
                is_running = False
            else:
                print("Task is stopped")
        if not message:
            break
    client_socket.close()

# Function to set up and start the server to listen for control signals
def start_server():
    # Set up TCP server to listen on port 5011
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5011))
    server.listen(5)
    print("server is listening on port 5011")
    
    while True:
        # Accept incoming connections and handle them in a new thread
        client_sock, addr = server.accept()
        print(f"accepted connection from {addr}")
        client_handler = threading.Thread(target=wait_for_signal, args=(client_sock,))
        client_handler.start()

# Start the TCP server
start_server()

    
    
"""    
def wait_for_signal():
    host = '0.0.0.0'
    port = 5011
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print("Waiting for signals...")
        
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                data = data.strip()
                if not data:
                    break
                
                message = data.decode('utf-8')
                print(f"Received message: {message}")
                
                if(message == "start_signal"):
                    print("Received start signal, executing task...")
                    break
                
wait_for_signal()


"""
"""
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('172.20.10.3', 5010))
"""

'''
thresh = 0.25
frame_check = 2
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")# Dat file is the crux of the code

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

flag=0

try:
    while True:
        frame1 = picam2.capture_array()
        frame = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detect(gray, 0)
        for subject in subjects:
            shape = predict(gray, subject)
            shape = face_utils.shape_to_np(shape)#converting to NumPy Array
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            
            data ="False"
            if ear < thresh:
                flag += 1
                print (flag)
                if flag >= frame_check:
                    cv2.putText(frame, "****************ALERT!****************", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "****************ALERT!****************", (10,325),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    print ("Drowsy")
                    drowsy_status = True
                    data = str(drowsy_status)
                else:
                    drowsy_status = False
                    data = str(drowsy_status)
            else:
                flag = 0
            
            
            client_socket.sendall(data.encode('utf-8'))
            print(f'sent: {data}')
            data = "False"
            time.sleep(2)

        
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    finally:
        client_socket.close()
    cv2.destroyAllWindows()
    cap.release() 
    '''