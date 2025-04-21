import os
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, render_template, Response, jsonify, request
import sqlite3
import face_recognition
from PIL import Image
import io
import webbrowser
from threading import Timer
import keyboard
import sys
import time

app = Flask(__name__)
start_time = None

def open_browser():
    webbrowser.open_new('http://localhost:5000/')
    global start_time
    start_time = time.time()

def check_exit():
    if keyboard.is_pressed('a'):
        print("\nExiting application... (Key 'a' pressed)")
        os._exit(0)

# Initialize student data
students = {}
marked_attendance = set()

def load_sample_faces():
    faces_dir = "faces"
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)
        return

    for filename in os.listdir(faces_dir):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            try:
                name_id = os.path.splitext(filename)[0]
                name, user_id = name_id.split('_')
                image_path = os.path.join(faces_dir, filename)
                
                # Load and encode the face
                image = face_recognition.load_image_file(image_path)
                # Try different face locations to find the best encoding
                face_locations = face_recognition.face_locations(image, model="hog")
                
                if not face_locations:
                    print(f"No face found in {filename}. Please check the image.")
                    continue
                
                # Get the encoding for the first face found
                face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                
                students[user_id] = {
                    'name': name,
                    'encoding': face_encoding
                }
                print(f"Successfully loaded {name} (ID: {user_id})")
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
    
    print(f"\nTotal students loaded: {len(students)}")
    if len(students) == 0:
        print("WARNING: No student faces were loaded! Please check your images.")

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS attendance')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  name TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()
    global marked_attendance
    marked_attendance = set()

def mark_attendance(name, user_id):
    if user_id in marked_attendance:
        return False
    
    current_time = datetime.now()
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO attendance (user_id, name, timestamp) VALUES (?, ?, ?)",
              (user_id, name, current_time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    marked_attendance.add(user_id)
    return True

def process_frame(frame):
    global start_time
    
    if start_time is None or time.time() - start_time < 10:
        seconds_left = 10 - int(time.time() - (start_time or time.time()))
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        font = cv2.FONT_HERSHEY_DUPLEX
        text = f"Starting in {seconds_left} seconds..."
        font_scale = 1.5
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = (h + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
        return frame

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Find faces in the frame
    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
    if face_locations:
        # Get encodings for found faces
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        # Process each face found in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Scale back up face locations since we scaled down the image
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Try to match with known faces
            matches = []
            best_match = None
            best_distance = float('inf')
            
            for user_id, student in students.items():
                # Compare face encodings
                face_distances = face_recognition.face_distance([student['encoding']], face_encoding)
                distance = face_distances[0]
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = (user_id, student['name'], distance)
            
            # Draw debug info
            debug_text = f"Match confidence: {(1 - best_distance) * 100:.1f}%"
            cv2.putText(frame, debug_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            # If we found a match with good confidence
            if best_match and best_distance < 0.5:  # Adjust this threshold if needed
                user_id, name, distance = best_match
                
                if user_id in marked_attendance:
                    # Already marked
                    color = (0, 165, 255)  # Orange
                    text = f"{name} - Marked Already"
                else:
                    # New attendance
                    color = (0, 255, 0)  # Green
                    mark_attendance(name, user_id)
                    text = f"{name} ({user_id})"
            else:
                # Unknown face
                color = (0, 0, 255)  # Red
                text = "Unknown"
            
            # Draw box and label
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, text, (left + 6, bottom - 6),
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    
    return frame

def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        check_exit()  # Check for exit key press
        
        success, frame = camera.read()
        if not success:
            break
        
        processed_frame = process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance_data')
def attendance_data():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''SELECT user_id, name, timestamp 
                 FROM attendance 
                 ORDER BY timestamp DESC 
                 LIMIT 50''')
    data = c.fetchall()
    conn.close()
    
    attendance_list = [{"user_id": row[0],
                       "name": row[1],
                       "timestamp": row[2]} for row in data]
    return jsonify(attendance_list)

@app.route('/clear_attendance')
def clear_attendance():
    init_db()
    return jsonify({"status": "success"})

@app.route('/restart_camera')
def restart_camera():
    return jsonify({"status": "success", "message": "Camera restarted"})

if __name__ == '__main__':
    init_db()
    load_sample_faces()
    print("\nStarting web server...")
    print("Press 'a' to stop the application at any time")
    Timer(1.5, open_browser).start()
    app.run(debug=True) 