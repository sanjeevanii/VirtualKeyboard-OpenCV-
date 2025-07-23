import cv2
import mediapipe as mp
import pyautogui
from math import hypot
import time

#Initialize webcam
cap = cv2.VideoCapture(0)

#MediaPipe hand tracking setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

#Keyboard layout (1 row for now)
keys = [
    ["Q","W","E","R","T","Y","U","I","O","P"],
    ["A","S","D","F","G","H","J","K","L"],
    ["Z","X","C","V","B","N","M","<"," "]
]


#For debouncing
last_pressed = None
press_delay = 0.6  # seconds
last_time = time.time()

#Function to draw keyboard
def draw_keyboard(img):
    for row_idx, row in enumerate(keys):
        for key_idx, key in enumerate(row):
            x = 50 + key_idx * 60
            y = 50 + row_idx * 60
            overlay = img.copy()
            cv2.rectangle(overlay, (x, y), (x + 50, y + 50), (50, 50, 50), -1)
            alpha = 0.6
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
            cv2.putText(img, key, (x + 15, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return img

#Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  #Flip horizontally for non-mirrored view
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    #Draw keyboard layout
    draw_keyboard(img)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))
                if id == 8:  #Index fingertip
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

            #Check if finger is "clicking" (index and middle tips close)
            if lm_list:
                ix, iy = lm_list[7][1:]  #Index tip
                mx, my = lm_list[4][1:]  #thumb tip
                dist = hypot(ix - mx, iy - my)

                #Draw a circle when "click" gesture detected
                if dist < 40:
                    cv2.circle(img, (ix, iy), 15, (0, 0, 255), cv2.FILLED)

                    #Check if inside any key area
                    for row_idx, row in enumerate(keys):
                        for key_idx, key in enumerate(row):
                            x = 50 + key_idx * 60
                            y = 50 + row_idx * 60
                            if x < ix < x + 50 and y < iy < y + 50:
                                current_time = time.time()
                                if last_pressed != key or (current_time - last_time) > press_delay:
                                    pyautogui.press(key.lower())
                                last_pressed = key
                                last_time = current_time
                                #Highlight pressed key
                                cv2.rectangle(img, (x, y), (x + 50, y + 50), (0, 255, 0), cv2.FILLED)
                                cv2.putText(img, key, (x + 15, y + 35),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            #Draw hand landmarks
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    #Show webcam feed
    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindow
shreysanjevanixoxo