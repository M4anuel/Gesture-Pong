import random
import sys
import pygame
from pygame.locals import USEREVENT

def animate_ball(delta_time):
    global ball_speed_x, ball_speed_y, paddle_width, ball_radius
    ball.x += ball_speed_x * delta_time
    ball.y += ball_speed_y * delta_time
    if ball.bottom >= screen_height:
        ball_speed_y *= -1
        ball.bottom=screen_height
    if ball.top <= 0:
        ball_speed_y *= -1
        ball.top=0
    if ball.right >= screen_width:
        points_won("player2")
    if ball.left <= 0:
        points_won("player1")
    if ball.left >= screen_width or ball.left <= 0:
        ball_speed_x *= -1
    if ball.colliderect(player1):
        ball_speed_x *= -1
        ball.x=0+paddle_width
    if ball.colliderect(player2):
        ball_speed_x *= -1
        ball.x=screen_width-paddle_width-ball_radius

def animate_player1(delta_time):
    global player1_speed
    player1.y += player1_speed*delta_time

    if player1.top <= 0:
        player1.top = 0
    if player1.bottom >= screen_height:
        player1.bottom = screen_height

def animate_player2(delta_time):
    global player2_speed
    player2.y += player2_speed*delta_time
    if ball.centery <= player2.centery:
        player2_speed = -6
    if ball.centery >= player2.centery:
        player2_speed = 6
    if player2.top <= 0:
        player2.top = 0
    if player2.bottom >= screen_height:
        player2.bottom = screen_height

def points_won(winner):
    global player2_points, player1_points

    if winner == "player2":
        player2_points += 1
    if winner == "player1":
        player1_points += 1

    reset_ball()

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.x = screen_width/2-10
    ball.y= random.randint(10,100)
    ball_speed_x *= random.choice([1, -1])
pygame.init()

screen_width, screen_height = 1280, 800

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Ponggame")

clock = pygame.time.Clock()

ball_radius = 30
ball = pygame.Rect(0,0,ball_radius,ball_radius) # x,y top left. w,h size
ball.center = (screen_width/2, screen_height/2)

paddle_width = 20
paddle_height = 100

player1 = pygame.Rect(0,0,paddle_width,paddle_height)
player1.centery = screen_height / 2

player2 = pygame.Rect(0,0,paddle_width,paddle_height)
player2.midright = (screen_width, screen_height / 2)

target_fps = 360
REFRESH_EVENT = USEREVENT + 1
pygame.time.set_timer(REFRESH_EVENT, 1000 // target_fps)


ball_speed_x = 4
ball_speed_y = 4

player1_speed = 0
player2_speed = 6

player2_points, player1_points = 0, 0
score_font = pygame.font.Font(None, 100)
fps_font = pygame.font.Font(None, 30)
while True:
    delta_time = clock.tick(target_fps)/10
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player1_speed = -6
            if event.key == pygame.K_DOWN:
                player1_speed = 6
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player1_speed = 0
            if event.key == pygame.K_DOWN:
                player1_speed = 0
        if event.type == REFRESH_EVENT:
            pass
    animate_ball(delta_time)
    animate_player1(delta_time)
    animate_player2(delta_time)

    # Draw game objects
    screen.fill("black")

    player1_score_surface = score_font.render(str(player1_points), True, "white")
    player2_score_surface = score_font.render(str(player2_points), True, "white")
    fps_surface = fps_font.render(str(int(clock.get_fps())), True, "white")

    screen.blit(player1_score_surface, (3*screen_width/4, 20))
    screen.blit(player2_score_surface, (screen_width/4, 20))
    screen.blit(fps_surface, (10, 10))

    pygame.draw.aaline(screen, "white", (screen_width/2,0), (screen_width/2,screen_height))
    pygame.draw.ellipse(screen, "white", ball)
    pygame.draw.rect(screen, "white", player1)
    pygame.draw.rect(screen, "white", player2)

    pygame.display.update()
    pygame.time.set_timer(REFRESH_EVENT, 1000 // target_fps)