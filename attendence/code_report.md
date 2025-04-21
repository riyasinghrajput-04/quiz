# Face Recognition Attendance System - Code Report

## 1. Project Structure
```
attendence/
├── app.py                 # Main application file
├── requirements.txt       # Dependencies
├── templates/
│   └── index.html        # Web interface template
└── faces/                # Directory for student face images
```

## 2. Dependencies (requirements.txt)
```python
opencv-python      # Computer vision and image processing
dlib              # Machine learning and face detection
face-recognition   # Face recognition library
Flask             # Web framework
numpy             # Numerical operations
Pillow            # Image processing
cmake==3.28.1     # Required for dlib compilation
keyboard          # Keyboard input handling
```

## 3. Core Components

### 3.1 Main Application (app.py)

#### 3.1.1 Initialization
```python
# Global Variables
students = {}              # Stores student face encodings
marked_attendance = set()  # Tracks marked students
start_time = None         # Application start time
```

#### 3.1.2 Database Management
```python
def init_db():
    # Creates SQLite database with attendance table
    # Table Structure:
    # - id (Primary Key)
    # - user_id (Student ID)
    # - name (Student Name)
    # - timestamp (Attendance Time)
```

#### 3.1.3 Face Loading System
```python
def load_sample_faces():
    # Loads faces from 'faces' directory
    # Processes each image:
    # 1. Extracts name and ID from filename
    # 2. Detects face using HOG model
    # 3. Creates face encoding
    # 4. Stores in students dictionary
```

#### 3.1.4 Attendance Management
```python
def mark_attendance(name, user_id):
    # Records attendance in database
    # Prevents duplicate entries
    # Returns True if marked, False if already marked
```

#### 3.1.5 Video Processing
```python
def process_frame(frame):
    # Main video processing function
    # Steps:
    # 1. Shows 10-second countdown
    # 2. Resizes frame for performance
    # 3. Detects faces
    # 4. Compares with known faces
    # 5. Marks attendance if match found
    # 6. Draws bounding boxes and labels
```

#### 3.1.6 Web Interface
```python
# Flask Routes:
@app.route('/')           # Main page
@app.route('/video_feed') # Video streaming
@app.route('/attendance_data') # Attendance data API
@app.route('/clear_attendance') # Clear attendance API
```

### 3.2 Web Interface (templates/index.html)

#### 3.2.1 Structure
```html
- Header Section
  - Title
  - Description
- Video Feed Section
  - Real-time camera feed
- Attendance Log Section
  - Table of attendance records
  - Clear attendance button
```

#### 3.2.2 JavaScript Functions
```javascript
updateAttendanceTable()  # Fetches and updates attendance data
clearAttendance()        # Clears attendance records
```

## 4. Data Flow

### 4.1 Face Recognition Process
1. Camera captures video frame
2. Frame is processed by `process_frame()`
3. Faces are detected using HOG model
4. Detected faces are compared with stored encodings
5. If match found, attendance is marked
6. Results are displayed on video feed

### 4.2 Web Interface Updates
1. Video feed updates in real-time
2. Attendance table updates every 5 seconds
3. Clear attendance button triggers database reset

## 5. Key Features

### 5.1 Face Recognition
- Uses HOG model for face detection
- Face encodings for recognition
- Confidence threshold for matches
- Multiple face detection support

### 5.2 Database
- SQLite for data storage
- Timestamp tracking
- Duplicate prevention
- Data persistence

### 5.3 Web Interface
- Real-time video feed
- Auto-updating attendance log
- Clear attendance functionality
- Responsive design

### 5.4 Performance
- Frame resizing for faster processing
- Efficient face detection
- Optimized database queries
- Background processing

## 6. Security Features

### 6.1 Data Security
- Parameterized database queries
- Input validation
- Secure file handling
- Error handling

### 6.2 Application Security
- Graceful exit handling
- Resource cleanup
- Error logging
- Input sanitization

## 7. Usage Flow

1. Application Start
   - Loads student faces
   - Initializes database
   - Starts web server
   - Opens browser

2. Face Recognition
   - Camera captures video
   - Faces are detected
   - Matches are found
   - Attendance is marked

3. Web Interface
   - Displays video feed
   - Shows attendance log
   - Allows clearing records
   - Auto-updates data

4. Application Exit
   - Press 'a' to exit
   - Clean shutdown
   - Resource release 