import random
import sys
import cv2
import pygame
import mediapipe as mp
import time


target_fps = 360
player2_speed = 0
player1_speed = 0
base_resolution = (16, 10)

screen_size_options = [
        (base_resolution[0]*50, base_resolution[1]*50),
        (base_resolution[0]*80, base_resolution[1]*80),
        (base_resolution[0]*100, base_resolution[1]*100),
        (base_resolution[0]*125, base_resolution[1]*125),
        (base_resolution[0]*150, base_resolution[1]*150)
    ]
screen_size_index = 1
screen_width, screen_height = screen_size_options[screen_size_index][0], screen_size_options[screen_size_index][1]
player1_points, player2_points = 0, 0
paddle_height = screen_height/6.5 #100
paddle_width = paddle_height/5 #20
ball_radius = paddle_height*0.3 #30
winning_points = 2
sensibility_gesture = 1.125 # so that not the upmost part of the webcam is the upmost part of the playing field
speed_scale = 160
ball_speed_x = screen_height/speed_scale # the higher this number, the slower the ball (duh...)
ball_speed_y = ball_speed_x
paddle_speed = ball_speed_y*(speed_scale/120)
reset_start_time = None

class Player:
    def __init__(self, x, y, width, height, control_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = 0
        self.control_type = control_type

    def update_position(self, delta_time):
        """Update paddle position based on speed."""
        self.rect.y += self.speed * delta_time
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    def handle_input(self, event):
        """Handle input based on control type."""
        if self.control_type == "wasd":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.speed = -paddle_speed
                elif event.key == pygame.K_s:
                    self.speed = paddle_speed
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_s]:
                    self.speed = 0

        elif self.control_type == "arrow_keys":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.speed = -paddle_speed
                elif event.key == pygame.K_DOWN:
                    self.speed = paddle_speed
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    self.speed = 0

def animate_ball(delta_time, player2, player1, ball):
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
        points_won("player1")
        reset_ball(ball)
    if ball.left <= 0:
        points_won("player2")
        reset_ball(ball)
    if ball.left >= screen_width or ball.left <= 0:
        ball_speed_x *= -1
    if ball.colliderect(player2):
        ball_speed_x *= -1
        ball.x = 0 + paddle_width
    if ball.colliderect(player1):
        ball_speed_x *= -1
        ball.x = screen_width - paddle_width - ball_radius
def animate_gesture(finger_y, player2):
    player2.rect.y = finger_y - player2.rect.height / 2
    if player2.rect.top <= 0:
        player2.rect.top = 0
    if player2.rect.bottom >= screen_height:
        player2.rect.bottom = screen_height


def points_won(winner):
    global player2_points, player1_points
    if winner == "player1":
        player1_points += 1
    if winner == "player2":
        player2_points += 1

    
def reset_ball(ball):
    global ball_speed_x, ball_speed_y, reset_start_time
    ball.x = screen_width / 2 - ball_radius / 2
    ball.y = screen_height / 2
    ball_speed_x = 0
    ball_speed_y = 0
    reset_start_time = time.time()


def control_wasd(event, player):
    """Handle player control with WASD keys."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            player.y -= paddle_speed
        elif event.key == pygame.K_s:
            player.y += paddle_speed
    if event.type == pygame.KEYUP:
        if event.key in [pygame.K_w, pygame.K_s]:
            player.y = paddle_speed


def control_arrow_keys(event, player):
    """Handle player control with Arrow keys."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            player.y -= paddle_speed
        elif event.key == pygame.K_DOWN:
            player.y += paddle_speed
    if event.type == pygame.KEYUP:
        if event.key in [pygame.K_UP, pygame.K_DOWN]:
            player.y = 0


def control_gesture(player, results, img, screen_height):
    """Handle player control with gestures (mediapipe)."""
    finger_y = screen_height / 2
    pinch_detected = False
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            thumb_tip = handLms.landmark[4]
            index_finger_tip = handLms.landmark[8]
            h, w, _ = img.shape
            cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            finger_y = (screen_height * cy / h) * sensibility_gesture

            # Detect pinch gesture
            distance = ((index_finger_tip.x - thumb_tip.x)**2 + (index_finger_tip.y - thumb_tip.y)**2)**0.5
            if distance < 0.05:
                pinch_detected = True

            # Update player position
            if pinch_detected:
                animate_gesture(finger_y, player)


def control_bot(delta_time, player, ball):
    """Handle CPU control for a bot player."""
    global player1_speed
    lookahead = 3
    if ball.centery < player.rect.centery and ball.centery + ball_speed_y * lookahead < player.rect.centery:
        player.speed = -min(abs(ball_speed_y), paddle_speed)
    elif ball.centery > player.rect.centery and ball.centery + ball_speed_y * lookahead > player.rect.centery:
        player.speed = min(abs(ball_speed_y), paddle_speed)

    player.rect.y += player1_speed * delta_time
    if player.rect.top <= 0:
        player.rect.top = 0
    if player.rect.bottom >= screen_height:
        player.rect.bottom = screen_height


def assign_controls(player2_control, player1_control):
    """Map player controls to the appropriate input functions."""
    input_mapping = {
        0: control_wasd,
        1: control_arrow_keys,
        2: control_gesture,
        3: control_bot,
    }
    return input_mapping[player2_control], input_mapping[player1_control]

def menu(player1_controls, player2_controls):
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pong - Main Menu")
    font = pygame.font.Font(None, 50)

    options = ["WASD", "Arrow Keys", "Gesture", "Bot"]
    player2_control = player1_controls  # Default to "WASD"
    player1_control = player2_controls  # Default to "Arrow Keys"
    
    selected_option = player1_controls
    selected_player = 1

    def draw_menu():
        screen.fill("black")
        title = font.render("Select Controls", True, "white")
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 50))
        player1_color = "green"
        player2_color = "blue"
        for i, option in enumerate(options):
            if selected_option == i:
                color = player1_color if selected_player == 1 else player2_color
            else:
                color = "white"
            text = font.render(option, True, color)
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, 150 + i * 50))
        
        player2_text = font.render(f"Player 1: {options[player2_control]}", True, player1_color if selected_player == 1 else "white")
        player1_text = font.render(f"Player 2: {options[player1_control]}", True, player2_color if selected_player == 2 else "white")
        screen.blit(player2_text, (screen_width/2 -17*len("Player 2: Arrow Keys"), screen_height/2+50))
        screen.blit(player1_text, (screen_width/2 +120, screen_height/2+50))

        prompt_text = font.render(
            "Up/Down Change Controls | Left/Right Switch Players | Enter Start Game",
            True,
            "white",
        )
        screen.blit(prompt_text, (screen_width // 2 - prompt_text.get_width() // 2,screen_height - 50))
        pygame.display.update()

    while True:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % len(options)
                    if selected_player == 1:
                        player2_control = selected_option
                    elif selected_player == 2:
                        player1_control = selected_option
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % len(options)
                    if selected_player == 1:
                        player2_control = selected_option
                    elif selected_player == 2:
                        player1_control = selected_option
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    selected_player = 1
                    selected_option = player2_control
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    selected_player = 2
                    selected_option = player1_control
                elif event.key == pygame.K_RETURN:  # Confirm selections
                    return player1_control, player2_control

def winner_screen(winner, player1, player2, ball) -> str:
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Game Over")
    font = pygame.font.Font(None, 50)

    options = ["Restart", "Change Controls", "Exit"]
    selected_option = 0

    def draw_winner_screen():
        screen.fill("black")
         # Display field
        pygame.draw.rect(screen, "white", player2.rect)
        pygame.draw.rect(screen, "white", player1.rect)
        pygame.draw.aaline(screen, "white", (screen_width / 2, 0), (screen_width / 2, screen_height))
        #pygame.draw.ellipse(screen, "white", ball)

        # Display scores
        score_font = pygame.font.Font(None, 100)
        player2_score_surface = score_font.render(str(player2_points), True, "white")
        player1_score_surface = score_font.render(str(player1_points), True, "white")     
        screen.blit(player2_score_surface, (3 * screen_width // 4, 20))
        screen.blit(player1_score_surface, (screen_width // 4, 20))


        title = score_font.render(f"{winner} Wins!", True, "white")
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, screen_height//2-200))

        for i, option in enumerate(options):
            color = "yellow" if selected_option == i else "white"
            text = font.render(option, True, color)
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height//2-80 + i * 50))

        pygame.display.update()

    while True:
        draw_winner_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN :
                    if selected_option == 0:  # Restart
                        return "restart"
                    elif selected_option == 1:  # Change Controls
                        return "menu"
                    elif selected_option == 2:  # Exit
                        pygame.quit()
                        sys.exit()





def game_loop(player1_controls = 0, player2_controls = 1, cap = None, mpHands = None):
    global ball_speed_x, ball_speed_y, player2_speed, player1_speed, screen_width, screen_height,\
    player2_points, player1_points, paddle_width, paddle_height, ball_radius, reset_start_time, paddle_height

    player1_control, player2_control = menu(player1_controls, player2_controls)
    control_mapping = ["wasd", "arrow_keys", "gesture", "bot"]
    player2 = Player(0, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height, control_mapping[player2_control])
    player1 = Player(screen_width - paddle_width, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height, control_mapping[player1_control])

    pygame.init()
    pygame.display.set_caption("Ponggame")
    clock = pygame.time.Clock()
    ball = pygame.Rect(screen_width // 2 - ball_radius // 2, screen_height // 2 - ball_radius // 2, ball_radius, ball_radius)
    screen = pygame.display.set_mode((screen_width, screen_height))

    mpHands = mpHands
    cap = cap
    hands = None if cap == mpHands else mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    font = pygame.font.Font(None, 50)
    countdown_font = pygame.font.Font(None, int(paddle_height*2))
    # Display "loading" message if gesture control is enabled
    if (player1_control == 2 or player2_control == 2) and (cap == None or mpHands == None):
        screen.fill("black")
        loading_message = font.render("Loading CV2 and Gesture Recognition...", True, "white")
        screen.blit(loading_message, (screen_width // 2 - loading_message.get_width() // 2, screen_height // 2 - loading_message.get_height() // 2))
        pygame.display.update()
        # Perform the gesture recognition setup
        cap = cv2.VideoCapture(0)
        success, img = cap.read()  # so cam already turns on
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        clock = pygame.time.Clock()
    reset_start_time = time.time()

    fps_font = pygame.font.Font(None, 30)
    ball_speed_x = 0
    ball_speed_y = 0
    step = 0
    while True:
        # Check for winner
        if player2_points >= winning_points or player1_points >= winning_points:
            winner = "Player 2" if player2_points >= winning_points else "Player 1"
            action = winner_screen(winner, player1, player2, ball)
            if action == "restart":
                player2_points, player1_points = 0, 0
                reset_start_time = time.time()
                continue
            elif action == "menu":
                game_loop(player2_control, player1_control, cap = cap, mpHands=mpHands)
        
        delta_time =  clock.tick(target_fps) / 10

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle inputs for both players
            player2.handle_input(event)
            player1.handle_input(event)

        # Update paddle positions
        player2.update_position(delta_time)
        player1.update_position(delta_time)
        
        # Handle gesture controls if selected
        if step == 3:
            if (player2.control_type == "gesture" or player1.control_type == "gesture"):
                step = -1
                success, img = cap.read()
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(imgRGB)

                if player2.control_type == "gesture":
                    control_gesture(player2, results, img, screen_height)
                if player1.control_type == "gesture":
                    control_gesture(player1, results, img, screen_height)
        step += 1

        if (player2.control_type == "bot" or player1.control_type == "bot"):
            if player2.control_type == "bot":
                control_bot(delta_time=delta_time, player=player2, ball=ball)
            if player1.control_type == "bot":
                control_bot(delta_time=delta_time, player=player1, ball=ball)

        screen.fill("black") #has to be before first drawing :)

        if reset_start_time is not None:
            elapsed_time = time.time() - reset_start_time
            remaining_time = max(0, int(3 - elapsed_time))

            countdown_text = countdown_font.render(str(remaining_time+1), True, "white")
            screen.blit(countdown_text, (screen_width // 2 - countdown_text.get_width() // 2, screen_height // 3 - countdown_text.get_height() // 2))

            if elapsed_time >= 3:
                ball_speed_x = screen_height / speed_scale * random.choice([1, -1])
                ball_speed_y = ball_speed_x * random.choice([1, -1])
                reset_start_time = None
            else:
                pygame.draw.ellipse(screen, "white", ball)

        # Update ball position and handle collisions
        animate_ball(delta_time, player2.rect, player1.rect, ball)

        # If a player scores, reset the ball immediately (no delay)
        if ball.x <= 0:  # Player 2 scores
            points_won("player2")
            reset_ball(ball)  # Ball immediately reset to center
        elif ball.x >= screen_width:  # Player 1 scores
            points_won("player1")
            reset_ball(ball)  # Ball immediately reset to center

        # Draw game objects
        pygame.draw.ellipse(screen, "white", ball)
        pygame.draw.rect(screen, "white", player2.rect)
        pygame.draw.rect(screen, "white", player1.rect)
        pygame.draw.aaline(screen, "white", (screen_width / 2, 0), (screen_width / 2, screen_height))

        # Display scores
        score_font = pygame.font.Font(None, 100)
        player2_score_surface = score_font.render(str(player2_points), True, "white")
        player1_score_surface = score_font.render(str(player1_points), True, "white")        
        fps_surface = fps_font.render(str(int(clock.get_fps())), True, "white")
        screen.blit(player2_score_surface, (3 * screen_width // 4, 20))
        screen.blit(player1_score_surface, (screen_width // 4, 20))
        screen.blit(fps_surface, (10, 10))
        pygame.display.update()


 

game_loop()
