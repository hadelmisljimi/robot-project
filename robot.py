import pygame
import sys
import math

pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animated Robot - Full Control")

clock = pygame.time.Clock()

# Load textures
body_orig = pygame.image.load("textures/body.png").convert_alpha()
head_orig = pygame.image.load("textures/head.png").convert_alpha()
left_arm_orig = pygame.image.load("textures/left_arm.png").convert_alpha()
right_arm_orig = pygame.image.load("textures/right_arm.png").convert_alpha()
left_leg_orig = pygame.image.load("textures/left_leg.png").convert_alpha()
right_leg_orig = pygame.image.load("textures/right_leg.png").convert_alpha()

# Robot state
robot_x, robot_y = WIDTH//2, HEIGHT//2
scale = 1.0
leg_step = 0
step_speed = 0.1
move_speed = 5
mouse_target = None

# Colors
colors = [(50,50,60),(50,0,0),(0,50,0),(60,0,70),(100,50,0)]
color_index = 0
color_mode = False  # False = original, True = colored

# Offsets
def get_offsets(scale):
    b_w,b_h=120*scale,100*scale
    h_w,h_h=100*scale,90*scale
    a_w,a_h=35*scale,90*scale
    l_w,l_h=40*scale,100*scale
    return {
        "body_size": (int(b_w),int(b_h)),
        "head_size": (int(h_w),int(h_h)),
        "arm_size": (int(a_w),int(a_h)),
        "leg_size": (int(l_w),int(l_h)),
        "head_offset_y": -int(b_h//2 + h_h//2 - 5*scale),
        "arm_offset_y": -int(b_h//4),
        "arm_offset_x": int(b_w//2 + 10),
        "leg_offset_x": 20,
        "leg_offset_y": int(b_h//2)
    }

def tint_surface(surface, color):
    tinted = surface.copy()
    overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    overlay.fill(color + (0,))
    tinted.blit(overlay,(0,0),special_flags=pygame.BLEND_RGBA_ADD)
    return tinted

def draw_rotated_arm(surf, image, pos, angle):
    r=pygame.transform.rotate(image, angle)
    rect=r.get_rect(midtop=pos)
    surf.blit(r, rect)

def draw_leg(surf,image,pos,offset_y):
    rect=image.get_rect(midtop=(pos[0],pos[1]+offset_y))
    surf.blit(image, rect)

parts_orig = [body_orig, head_orig, left_arm_orig, right_arm_orig, left_leg_orig, right_leg_orig]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            mouse_target=event.pos
        elif event.type == pygame.KEYDOWN and event.key==pygame.K_SPACE:
            color_mode=True
            color_index=(color_index+1)%len(colors)

    keys=pygame.key.get_pressed()
    # Movement
    dx=dy=0
    if keys[pygame.K_LEFT]: dx -= move_speed; leg_step+=step_speed
    if keys[pygame.K_RIGHT]: dx += move_speed; leg_step+=step_speed
    if keys[pygame.K_UP]: dy -= move_speed; leg_step+=step_speed
    if keys[pygame.K_DOWN]: dy += move_speed; leg_step+=step_speed
    robot_x+=dx
    robot_y+=dy
    # Zoom
    if keys[pygame.K_w]: scale+=0.01; leg_step+=step_speed
    if keys[pygame.K_s]: scale=max(0.1,scale-0.01); leg_step+=step_speed
    # Mouse movement
    if mouse_target:
        mdx, mdy = mouse_target[0]-robot_x, mouse_target[1]-robot_y
        dist=math.hypot(mdx,mdy)
        if dist>move_speed:
            robot_x+=mdx/dist*move_speed
            robot_y+=mdy/dist*move_speed
            leg_step+=step_speed
        else:
            robot_x,robot_y=mouse_target
            mouse_target=None

    offsets=get_offsets(scale)
    body,head,left_arm,right_arm,left_leg,right_leg = [
        pygame.transform.scale(parts_orig[i], offsets[s])
        for i,s in enumerate(["body_size","head_size","arm_size","arm_size","leg_size","leg_size"])
    ]

    if color_mode:
        current_color=colors[color_index]
        body,head,left_arm,right_arm,left_leg,right_leg=[
            tint_surface(p,current_color) for p in [body,head,left_arm,right_arm,left_leg,right_leg]
        ]

    # Animation
    l_leg_off=math.sin(leg_step)*15
    r_leg_off=math.sin(leg_step+math.pi)*15
    swing=5
    l_arm_ang=math.sin(leg_step+math.pi)*swing
    r_arm_ang=math.sin(leg_step)*swing

    screen.fill((40,40,40))
    # Legs
    draw_leg(screen,left_leg,(robot_x-offsets["leg_offset_x"],robot_y+offsets["leg_offset_y"]),l_leg_off)
    draw_leg(screen,right_leg,(robot_x+offsets["leg_offset_x"],robot_y+offsets["leg_offset_y"]),r_leg_off)
    # Body
    screen.blit(body,body.get_rect(center=(robot_x,robot_y)))
    # Arms
    draw_rotated_arm(screen,left_arm,(robot_x-offsets["arm_offset_x"],robot_y+offsets["arm_offset_y"]),l_arm_ang)
    draw_rotated_arm(screen,right_arm,(robot_x+offsets["arm_offset_x"],robot_y+offsets["arm_offset_y"]),r_arm_ang)
    # Head
    screen.blit(head,head.get_rect(center=(robot_x,robot_y+offsets["head_offset_y"])))

    pygame.display.flip()
    clock.tick(60)
