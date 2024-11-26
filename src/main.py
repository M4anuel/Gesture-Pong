import random
import sys
import time
import cv2
import pygame
import mediapipe as mp
from pygame.locals import USEREVENT
import tkinter as tk

target_fps = 360
ball_speed_x = 4
ball_speed_y = 4
player1_speed = 0
player2_speed = 0
screen_width, screen_height = 1280, 800
player2_points, player1_points = 0, 0
paddle_width = 20
paddle_height = 100
ball_radius = 30
winning_points = 10
options = ['Bot', 'Gesture', 'WASD', 'Arrows']
sensibility_gesture = 1.1 # so that not the upmost part of the webcam is the upmost part of the playing field
show_cam = True


def animate_ball(delta_time, player1, player2, ball):
    global ball_speed_x, ball_speed_y, paddle_width, ball_radius
    ball.x += ball_speed_x * delta_time
    ball.y += ball_speed_y * delta_time
    if ball.bottom >= screen_height:
        ball_speed_y *= -1
        ball.bottom = screen_height
    if ball.top <= 0:
        ball_speed_y *= -1
        ball.top = 0
    if ball.right >= screen_width:
        points_won("player2", ball)
    if ball.left <= 0:
        points_won("player1", ball)
    if ball.left >= screen_width or ball.left <= 0:
        ball_speed_x *= -1
    if ball.colliderect(player1):
        ball_speed_x *= -1
        ball.x = 0 + paddle_width
    if ball.colliderect(player2):
        ball_speed_x *= -1
        ball.x = screen_width - paddle_width - ball_radius

def animate_player1(finger_y, player1):
    player1.y = finger_y - player1.height / 2
    if player1.top <= 0:
        player1.top = 0
    if player1.bottom >= screen_height:
        player1.bottom = screen_height

def animate_cpu(delta_time, player2, ball):
    global player2_speed
   # speed = 6 * clock.get_fps()/60))
    player2.y += player2_speed*delta_time
    lookahead = 3
    if ball.centery < player2.centery and ball.centery + ball_speed_y*lookahead < player2.centery:
        player2_speed = -min(abs(ball_speed_y),6)
    if ball.centery > player2.centery and ball.centery + ball_speed_y*lookahead > player2.centery:
        player2_speed = min(abs(ball_speed_y), 6)
    if player2.top <= 0:
        player2.top = 0
    if player2.bottom >= screen_height:
        player2.bottom = screen_height

def points_won(winner, ball):
    global player1_points, player2_points
    if winner == "player2":
        player2_points += 1
    if winner == "player1":
        player1_points += 1
    reset_ball(ball)

def reset_ball(ball):
    global ball_speed_x, ball_speed_y
    ball.x = screen_width / 2 - 10
    ball.y = random.randint(10, screen_height - 10)
    ball_speed_x *= random.choice([1, -1])

def game_loop(player1_clicked, player2_clicked):
    global ball_speed_x, ball_speed_y, player1_speed, player2_speed, screen_width, screen_height,\
        player1_points, player2_points, paddle_width, paddle_height, ball_radius
    print(player1_clicked, player2_clicked)
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ponggame")
    clock = pygame.time.Clock()
    ball = pygame.Rect(0, 0, ball_radius, ball_radius)  # x,y top left. w,h size
    ball.center = (screen_width / 2, screen_height / 2)
    player1 = pygame.Rect(0, 0, paddle_width, paddle_height)
    player1.centery = screen_height / 2
    player2 = pygame.Rect(0, 0, paddle_width, paddle_height)
    player2.midright = (screen_width, screen_height / 2)
    REFRESH_EVENT = USEREVENT + 1
    pygame.time.set_timer(REFRESH_EVENT, 1000 // target_fps)
    score_font = pygame.font.Font(None, 100)
    fps_font = pygame.font.Font(None, 30)

    # Mediapipe initialization
    cap = cv2.VideoCapture(0)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils
    step = 0
    while True:
        if (player1_points >= winning_points or player2_points >= winning_points):
            cv2.destroyAllWindows()
            pygame.quit()
            menu()
            break
        delta_time = clock.tick(target_fps) / 10
        if step == 4: # the bigger this number the bigger the disparity between fps while looking at fingers vs only draw update
            success, img = cap.read()
            print(delta_time)
            if not success:
                print("Failed to capture image")
                continue
            img_scalefactor = 1 #didn't improve framerate
            resized_image = img # cv2.resize(img, (int(1920*img_scalefactor), int(1080*img_scalefactor))) 
            imgRGB = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)
            finger_y = screen_height / 2  # Default position if no hand is detected
            pinch_detected = False

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    if handLms.landmark[9].x < handLms.landmark[5].x:  # This should indicate the right hand
                        thumb_tip = handLms.landmark[4]
                        index_finger_tip = handLms.landmark[8]
                        h, w, _ = resized_image.shape
                        cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                        finger_y = (screen_height * cy / h)*sensibility_gesture  # Scale position

                        # Calculate the distance between thumb tip and index finger tip
                        distance = ((index_finger_tip.x - thumb_tip.x)**2 + (index_finger_tip.y - thumb_tip.y)**2)**0.5
                        if distance < 0.05:  # Threshold for detecting a pinch gesture
                            pinch_detected = True

                        # Draw hand landmarks on the image
                        mpDraw.draw_landmarks(resized_image, handLms, mpHands.HAND_CONNECTIONS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == REFRESH_EVENT:
                    pass

            if pinch_detected:
                animate_player1(finger_y, player1)
            step = 0
                # Display hand tracking window
            if show_cam:
                cv2.imshow("Hand Tracking", resized_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        animate_cpu(delta_time, player2, ball)
        animate_ball(delta_time, player1, player2, ball)

        # Draw game objects
        screen.fill("black")
        player1_score_surface = score_font.render(str(player1_points), True, "white")
        player2_score_surface = score_font.render(str(player2_points), True, "white")
        fps_surface = fps_font.render(str(int(clock.get_fps())), True, "white")
        screen.blit(player1_score_surface, (3 * screen_width / 4, 20))
        screen.blit(player2_score_surface, (screen_width / 4, 20))
        screen.blit(fps_surface, (10, 10))
        pygame.draw.aaline(screen, "white", (screen_width / 2, 0), (screen_width / 2, screen_height))
        pygame.draw.ellipse(screen, "white", ball)
        pygame.draw.rect(screen, "white", player1)
        pygame.draw.rect(screen, "white", player2)

        pygame.display.update()
        pygame.time.set_timer(REFRESH_EVENT, 1000 // target_fps)

        
        step += 1

    cap.release()
    cv2.destroyAllWindows()

def menu():
    global options
    root = tk.Tk()
    root.title("Gesture-Pong")
    root.eval("tk::PlaceWindow . center")
    root.configure(background="black")
    btn_game = tk.Button(root, text="Gesture-Pong", command=lambda: [game_loop(player1_clicked.get(), player2_clicked.get()), root.destroy()])
    btn_game.pack()
    player1_clicked = tk.StringVar()
    player2_clicked = tk.StringVar()
    player1_clicked.set('Gesture')
    player2_clicked.set('Bot')
    player1_drop_down = tk.OptionMenu(root, player1_clicked, *options)
    player2_drop_down = tk.OptionMenu(root, player2_clicked, *options)
    player1_drop_down.pack()
    player2_drop_down.pack()

    root.mainloop()

menu()
