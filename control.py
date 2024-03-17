import pygame
import math

from mona import MonaUno, Mona


CONTROL_MONA = 0

screen = pygame.display.set_mode((300, 300))
clock = pygame.time.Clock()
sent_stop = False
ir = (0, 0, 0, 0, 0)
state = 0
angle = 0
xp = yp = 0
pygame.init()
font = pygame.font.SysFont("Arial", 32)


def irc(x):
    return (x // 4, 255 - (x // 4), 255 if x < 950 else 0)


uno = MonaUno()
monas = [
    Mona(uno, 0),
    Mona(uno, 1),
]
monas[0].spawn_poll_thread()
monas[1].spawn_poll_thread()

while True:
    if state == 0:
        screen.fill((230, 230, 230))
    else:
        screen.fill((230, 200, 200))

    pygame.draw.line(screen, irc(ir[0]), (10, 140), (10, 240), 5)
    pygame.draw.line(screen, irc(ir[1]), (20, 120), (80, 40), 5)
    pygame.draw.line(screen, irc(ir[2]), (100, 20), (200, 20), 5)
    pygame.draw.line(screen, irc(ir[3]), (220, 40), (280, 120), 5)
    pygame.draw.line(screen, irc(ir[4]), (290, 140), (290, 240), 5)

    p0 = (150, 150)
    p1 = (
        p0[0] + int(100 * math.sin(angle)),
        p0[0] - int(100 * math.cos(angle)),
    )
    pygame.draw.line(screen, (0, 127, 255), p0, p1, 5);

    screen.blit(font.render(str(round(math.degrees(angle) % 360, 1)), (0, 0, 0), 1), (100, 100))
    screen.blit(font.render(str(round(xp, 1)), (0, 0, 0), 1), (100, 132))
    screen.blit(font.render(str(round(yp, 1)), (0, 0, 0), 1), (100, 164))

    if monas[0].wall_left:
        pygame.draw.rect(screen, (255, 0, 0), (0, 0, 20, 300))
    if monas[0].wall_right:
        pygame.draw.rect(screen, (255, 0, 0), (280, 0, 20, 300))
    if monas[0].wall_front:
        pygame.draw.rect(screen, (255, 0, 0), (0, 0, 300, 20))

    pygame.display.flip()

    if monas[0].state is not None:
        # print(packet)
        if monas[0].state.source == CONTROL_MONA:
            ir = monas[0].state.ir
            state = monas[0].state.state
            angle = monas[0].state.angle_radians
            xp = monas[0].state.world_x
            yp = monas[0].state.world_y

            print(ir)

    mona_binds = (
        # Mona 1
        (
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_PAGEUP,
            pygame.K_PAGEDOWN,
            pygame.K_SPACE,
        ),
        # Mona 2
        (
            pygame.K_w,
            pygame.K_s,
            pygame.K_a,
            pygame.K_d,
            pygame.K_q,
            pygame.K_e,
            pygame.K_z,
        )
    )

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            quit()
        elif e.type == pygame.KEYDOWN:
            for mona, keys in zip(monas, mona_binds):
                if e.key == keys[0]:  # Forward
                    mona.move_forward()
                elif e.key == keys[1]:  # Back
                    mona.move_backward()
                elif e.key == keys[2]:  # Left
                    mona.move_left()
                elif e.key == keys[3]:  # Right
                    mona.move_right()
                elif e.key == keys[4]:  # Turn left
                    mona.turn_left_90()
                elif e.key == keys[5]:  # Turn right
                    mona.turn_right_90()
                elif e.key == keys[6]:  # Spin and out
                    mona.turn_180_and_out()

    clock.tick(30)
