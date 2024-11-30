import random
import sys
import cv2
import pygame
import mediapipe as mp


target_fps = 360
ball_speed_x = 6
ball_speed_y = 6
player2_speed = 0
player1_speed = 0
screen_width, screen_height = 1280, 800
player1_points, player2_points = 0, 0
paddle_width = 20
paddle_height = 100
ball_radius = 30
winning_points = 5
sensibility_gesture = 1.1 # so that not the upmost part of the webcam is the upmost part of the playing field

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
                    self.speed = -6
                elif event.key == pygame.K_s:
                    self.speed = 6
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_s]:
                    self.speed = 0

        elif self.control_type == "arrow_keys":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.speed = -6
                elif event.key == pygame.K_DOWN:
                    self.speed = 6
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
        points_won("player1", ball)
    if ball.left <= 0:
        points_won("player2", ball)
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


def points_won(winner, ball):
    global player2_points, player1_points
    if winner == "player1":
        player1_points += 1
    if winner == "player2":
        player2_points += 1
    reset_ball(ball)

    
def reset_ball(ball):
    global ball_speed_x, ball_speed_y
    ball.x = screen_width / 2 - 10
    ball.y = random.randint(10, screen_height - 10)
    ball_speed_x *= random.choice([1, -1])

def control_wasd(event, player):
    """Handle player control with WASD keys."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            player.y -= 6
        elif event.key == pygame.K_s:
            player.y += 6
    if event.type == pygame.KEYUP:
        if event.key in [pygame.K_w, pygame.K_s]:
            player.y = 0


def control_arrow_keys(event, player):
    """Handle player control with Arrow keys."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            player.y -= 6
        elif event.key == pygame.K_DOWN:
            player.y += 6
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
        player.speed = -min(abs(ball_speed_y), 6)
    elif ball.centery > player.rect.centery and ball.centery + ball_speed_y * lookahead > player.rect.centery:
        player.speed = min(abs(ball_speed_y), 6)

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
        
        for i, option in enumerate(options):
            color = "yellow" if selected_option == i else "white"
            text = font.render(option, True, color)
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, 150 + i * 50))
        
        player2_text = font.render(f"Player 1: {options[player2_control]}", True, "yellow" if selected_player == 1 else "white")
        player1_text = font.render(f"Player 2: {options[player1_control]}", True, "yellow" if selected_player == 2 else "white")
        screen.blit(player2_text, (screen_width/2 -17*len("Player 2: Arrow Keys"), screen_height/2+50))
        screen.blit(player1_text, (screen_width/2 +120, screen_height/2+50))

        prompt_text = font.render(
            "Up/Down Change Controls | Left/Right Switch Players | Enter Start Game",
            True,
            "white",
        )
        screen.blit(prompt_text, (30, screen_height - 50))
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

def winner_screen(winner) -> str:
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Game Over")
    font = pygame.font.Font(None, 50)

    options = ["Restart", "Change Controls", "Exit"]
    selected_option = 0

    def draw_winner_screen():
        screen.fill("black")
        title = font.render(f"{winner} Wins!", True, "white")
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 50))

        for i, option in enumerate(options):
            color = "yellow" if selected_option == i else "white"
            text = font.render(option, True, color)
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, 150 + i * 50))

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





def game_loop(player1_controls = 0, player2_controls = 1, cap = None, mpHands = None, initial_start = True):
    global ball_speed_x, ball_speed_y, player2_speed, player1_speed, screen_width, screen_height,\
    player2_points, player1_points, paddle_width, paddle_height, ball_radius

    player1_control, player2_control = menu(player1_controls, player2_controls)
    control_mapping = ["wasd", "arrow_keys", "gesture", "bot"]
    player2 = Player(0, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height, control_mapping[player2_control])
    player1 = Player(screen_width - paddle_width, screen_height // 2 - paddle_height // 2, paddle_width, paddle_height, control_mapping[player1_control])

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ponggame")
    clock = pygame.time.Clock()
    ball = pygame.Rect(screen_width // 2 - ball_radius // 2, screen_height // 2 - ball_radius // 2, ball_radius, ball_radius)
    
    mpHands = mpHands
    cap=cap
    # Display "loading" message if gesture control is enabled
    if (player1_control == 2 or player2_control == 2) and (cap == None or mpHands== None):
        font = pygame.font.Font(None, 50)
        screen.fill("black")
        loading_message = font.render("Loading CV2 and Gesture Recognition...", True, "white")
        screen.blit(loading_message, (screen_width // 2 - loading_message.get_width() // 2, screen_height // 2 - loading_message.get_height() // 2))
        pygame.display.update()
        
        # Perform the gesture recognition setup
        cap = cv2.VideoCapture(0)
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    step = 0
    fps_font = pygame.font.Font(None, 30)

    three_second_cooldown = initial_start     
    while True:
        # Countdown before game start
        if three_second_cooldown:
            three_second_cooldown = False
            countdown_font = pygame.font.Font(None, 100)
            for countdown in range(3, 0, -1):  # 3, 2, 1
                screen.fill("black")
                countdown_surface = countdown_font.render(str(countdown), True, "white")
                screen.blit(countdown_surface, (screen_width // 2 - countdown_surface.get_width() // 2, screen_height // 2 - countdown_surface.get_height() // 2))
                pygame.display.update()
                pygame.time.delay(1000)  # Delay for 1 second
        delta_time = clock.tick(target_fps) / 10
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
        if (player2.control_type == "gesture" or player1.control_type == "gesture") and step == 3:
            success, img = cap.read()
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)

            if player2.control_type == "gesture":
                control_gesture(player2, results, img, screen_height)
            if player1.control_type == "gesture":
                control_gesture(player1, results, img, screen_height)
            step = 0


        if (player2.control_type == "bot" or player1.control_type == "bot"):
            if player2.control_type == "bot":
                control_bot(delta_time=delta_time, player=player2, ball=ball)
            if player1.control_type == "bot":
                control_bot(delta_time=delta_time, player=player1, ball=ball)
        # Update ball position and collisions
        animate_ball(delta_time, player2.rect, player1.rect, ball)

        # Draw game objects
        screen.fill("black")
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
        step += 1
        # Check for winner
        if player2_points >= winning_points or player1_points >= winning_points:
            winner = "Player 2" if player2_points >= winning_points else "Player 1"
            action = winner_screen(winner)
            if action == "restart":
                player2_points, player1_points = 0, 0
                three_second_cooldown = True
                continue
            elif action == "menu":
                game_loop(player2_control, player1_control, cap = cap, mpHands=mpHands, initial_start=False)

    
game_loop()