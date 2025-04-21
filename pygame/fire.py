import cv2
import numpy as np
import pygame
import time

pygame.mixer.init()
alarm_sound = pygame.mixer.Sound('alarm.wav')

def detect_fire(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower1 = np.array([0, 100, 100])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([10, 100, 100])
    upper2 = np.array([25, 255, 255])
    lower3 = np.array([25, 100, 100])
    upper3 = np.array([35, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask3 = cv2.inRange(hsv, lower3, upper3)
    
    fire_mask = cv2.bitwise_or(mask1, mask2)
    fire_mask = cv2.bitwise_or(fire_mask, mask3)
    
    kernel = np.ones((5, 5), np.uint8)
    fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
    fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(fire_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    fire_detected = False
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            fire_detected = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, 'FIRE DETECTED', (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    
    return frame, fire_detected

def main():
    cap = cv2.VideoCapture(0)
    
    alarm_playing = False
    last_fire_time = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame, fire_detected = detect_fire(frame)
        
        cv2.imshow('Fire Detection', processed_frame)
        
        if fire_detected:
            last_fire_time = time.time()
            if not alarm_playing:
                alarm_sound.play(-1)
                alarm_playing = True
        else:
            if alarm_playing and (time.time() - last_fire_time > 3):
                alarm_sound.stop()
                alarm_playing = False
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    if alarm_playing:
        alarm_sound.stop()

if __name__ == "__main__":
    main()
