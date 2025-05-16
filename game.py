from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


from math import sin, cos, radians, sqrt, degrees, atan2
import random

# --- GLOBALS ---
position = [0, 0, 0]
player_rotation = 0
player_size = 30

cam_distance = 300
cam_height = 300
cam_angle = 180
fovY = 90
GRID_LENGTH = 600

bullets = []
player_speed = 8
rotation_speed = 10
bullet_speed = 1
bullet_size = 12

live = 5
score = 0
miss_bullet = 0
game_over = False
perspective = "THIRD_PERSON"

# Maze global
maze = None
cell_size = None
exit_x, exit_y = None, None  # To store the exit's grid coordinates

# Enemies
enemies = []
paused = False
game_exit = False
exit_button_rect = (950, 750, 40, 40)  # x, y, width, height
pause_button_rect = (900, 750, 40, 40)




def draw_ui_buttons():
    # Switch to 2D orthogonal projection for UI
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw pause button
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_QUADS)
    glVertex2f(pause_button_rect[0], pause_button_rect[1])
    glVertex2f(pause_button_rect[0] + pause_button_rect[2], pause_button_rect[1])
    glVertex2f(pause_button_rect[0] + pause_button_rect[2], pause_button_rect[1] + pause_button_rect[3])
    glVertex2f(pause_button_rect[0], pause_button_rect[1] + pause_button_rect[3])
    glEnd()
    
    # Draw pause symbol
    glColor3f(0, 0, 0)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(pause_button_rect[0] + 12, pause_button_rect[1] + 10)
    glVertex2f(pause_button_rect[0] + 12, pause_button_rect[1] + 30)
    glVertex2f(pause_button_rect[0] + 28, pause_button_rect[1] + 10)
    glVertex2f(pause_button_rect[0] + 28, pause_button_rect[1] + 30)
    glEnd()

    # Draw exit button
    glColor3f(1, 0, 0)
    glBegin(GL_QUADS)
    glVertex2f(exit_button_rect[0], exit_button_rect[1])
    glVertex2f(exit_button_rect[0] + exit_button_rect[2], exit_button_rect[1])
    glVertex2f(exit_button_rect[0] + exit_button_rect[2], exit_button_rect[1] + exit_button_rect[3])
    glVertex2f(exit_button_rect[0], exit_button_rect[1] + exit_button_rect[3])
    glEnd()
    
    # Draw X symbol
    glColor3f(1, 1, 1)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex2f(exit_button_rect[0] + 10, exit_button_rect[1] + 10)
    glVertex2f(exit_button_rect[0] + 30, exit_button_rect[1] + 30)
    glVertex2f(exit_button_rect[0] + 30, exit_button_rect[1] + 10)
    glVertex2f(exit_button_rect[0] + 10, exit_button_rect[1] + 30)
    glEnd()

    # Restore 3D settings
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)



    
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.health = 100
        self.speed = 1
        self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

    def move(self):
        if self.direction == 'UP':
            new_x, new_y = self.x, self.y + self.speed
        elif self.direction == 'DOWN':
            new_x, new_y = self.x, self.y - self.speed
        elif self.direction == 'LEFT':
            new_x, new_y = self.x - self.speed, self.y
        elif self.direction == 'RIGHT':
            new_x, new_y = self.x + self.speed, self.y
        else:
            return

        if not check_collision(new_x, new_y):
            self.x, self.y = new_x, new_y
        else:
            self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        zombie_color = (0.1, 0.5, 0.1)
        leg_positions = [-10, 10]
        glColor3f(*zombie_color)
        for x in leg_positions:
            glPushMatrix()
            glTranslatef(x, 0, 0)
            glRotatef(-90, 0, 0, 1)
            gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10)
            glPopMatrix()
        glPushMatrix()
        glColor3f(*zombie_color)
        glTranslatef(0, 0, 80)
        glScalef(0.7, 0.4, 0.7)
        glutSolidCube(60)
        glPopMatrix()
        arm_positions = [-25, 25]
        glColor3f(*zombie_color)
        for x in arm_positions:
            glPushMatrix()
            glTranslatef(x, 0, 90)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 5, 5, 40, 10, 10)
            glPopMatrix()
        glPushMatrix()
        glColor3f(0.2, 0.6, 0.2)
        glTranslatef(0, 0, 125)
        gluSphere(gluNewQuadric(), 20, 15, 15)
        glPopMatrix()
        glPopMatrix()

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

def generate_maze(size=21):
    global exit_x, exit_y
    if size % 2 == 0:
        size += 1
    maze = [[1 for _ in range(size)] for _ in range(size)]

    def carve(x, y):
        maze[y][x] = 0
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < size-1 and 0 < ny < size-1 and maze[ny][nx] == 1:
                maze[ny - dy//2][nx - dx//2] = 0
                carve(nx, ny)

    carve(1, 1)
    maze[1][0] = 0  # Entry point
    maze[size - 2][size - 1] = 0  # Exit point
    exit_x, exit_y = size - 1, size - 2  # Corrected exit coordinates (column, row)
    return maze



def set_player_at_entry():
    global position, maze, cell_size, GRID_LENGTH
    entry_row, entry_col = 1, 0
    x = -GRID_LENGTH + entry_col * cell_size + cell_size / 2
    y = -GRID_LENGTH + entry_row * cell_size + cell_size / 2
    position[0], position[1] = x, y


def check_win_condition():
    global position, exit_x, exit_y, game_over, score, cell_size, GRID_LENGTH
    if None in (exit_x, exit_y, cell_size):
        return
    exit_world_x = -GRID_LENGTH + exit_x * cell_size + cell_size / 2
    exit_world_y = -GRID_LENGTH + exit_y * cell_size + cell_size / 2
    distance = sqrt((position[0] - exit_world_x)**2 + (position[1] - exit_world_y)**2)
    if distance < cell_size / 2 and not game_over:
        game_over = True
        score += 50

def check_collision(new_x, new_y):
    global maze, cell_size, GRID_LENGTH
    grid_x = int((new_x + GRID_LENGTH) / cell_size)
    grid_y = int((new_y + GRID_LENGTH) / cell_size)
    if grid_x < 0 or grid_x >= len(maze[0]) or grid_y < 0 or grid_y >= len(maze):
        return True
    return maze[grid_y][grid_x] == 1


def keyboardListener(key, x, y):
    global position, player_rotation, live, miss_bullet, score, game_over, bullets, player_speed,paused
    if key == b'+':  # Increase speed
        player_speed = min(player_speed + 1, 10)  # Cap at 10
    if key == b'-':  # Decrease speed
        player_speed = max(player_speed - 1, 1)
    if key == b'w':
        new_x = position[0] + cos(radians(player_rotation)) * player_speed
        new_y = position[1] + sin(radians(player_rotation)) * player_speed
        if not check_collision(new_x, new_y):
            position[0] = new_x
            position[1] = new_y
    if key == b's':
        new_x = position[0] - cos(radians(player_rotation)) * player_speed
        new_y = position[1] - sin(radians(player_rotation)) * player_speed
        if not check_collision(new_x, new_y):
            position[0] = new_x
            position[1] = new_y
    if key == b'a':
        player_rotation += rotation_speed
        player_rotation %= 360
    if key == b'd':
        player_rotation -= rotation_speed
        player_rotation %= 360

    if key == b'p' or key == b'P':
        paused = not paused
        glutPostRedisplay()
        return

    if key == b'r':  # Restart the game
        live = 5
        score = 0
        miss_bullet = 0
        game_over = False
        bullets = []
        global maze, enemies, exit_x, exit_y
        maze = None
        enemies = []
        exit_x, exit_y = None, None  # Reset the exit coordinates
        draw_maze()
        set_player_at_entry()
        spawn_enemies(10)  # spawn enemies when restarting
        glutPostRedisplay()
        return
    glutPostRedisplay()



def draw_maze():
    global maze, cell_size, GRID_LENGTH, position
    
    if maze is None:
        maze_size = 21  # Should be odd for proper maze borders
        maze = generate_maze(maze_size)
        cell_size = (GRID_LENGTH * 2) / len(maze)
        set_player_at_entry()

    start_x = -GRID_LENGTH
    start_y = -GRID_LENGTH
    wall_height = 120

    glColor3f(0.8, 0.8, 0.8)  # Light gray floor
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == 1:
                x = start_x + j * cell_size
                y = start_y + i * cell_size
                
                # Calculate distance to player
                dist = sqrt((position[0] - x) ** 2 + (position[1] - y) ** 2)
                shade_factor = min(1.0, max(0.3, 1 / (dist / 100)))

                glColor3f(shade_factor, 0.1, 0.6)
                
                glBegin(GL_QUADS)
                glVertex3f(x, y, 0)
                glVertex3f(x + cell_size, y, 0)
                glVertex3f(x + cell_size, y, wall_height)
                glVertex3f(x, y, wall_height)
                
                glVertex3f(x, y + cell_size, 0)
                glVertex3f(x + cell_size, y + cell_size, 0)
                glVertex3f(x + cell_size, y + cell_size, wall_height)
                glVertex3f(x, y + cell_size, wall_height)
                
                glVertex3f(x, y, 0)
                glVertex3f(x, y + cell_size, 0)
                glVertex3f(x, y + cell_size, wall_height)
                glVertex3f(x, y, wall_height)
                
                glVertex3f(x + cell_size, y, 0)
                glVertex3f(x + cell_size, y + cell_size, 0)
                glVertex3f(x + cell_size, y + cell_size, wall_height)
                glVertex3f(x + cell_size, y, wall_height)
                
                glVertex3f(x, y, wall_height)
                glVertex3f(x + cell_size, y, wall_height)
                glVertex3f(x + cell_size, y + cell_size, wall_height)
                glVertex3f(x, y + cell_size, wall_height)
                glEnd()


def check_bullet_enemy_collisions():
    global bullets, enemies, score
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            distance = sqrt((bullet['x'] - enemy.x) ** 2 + (bullet['y'] - enemy.y) ** 2)
            if distance < enemy.size:
                if enemy.take_damage(50):  # Apply damage to enemy
                    score += 10  # Increase score when an enemy dies
                    enemies.remove(enemy)  # Remove the enemy
                bullets.remove(bullet)  # Remove the bullet after collision

def check_player_enemy_collision():
    global live, position, enemies
    for enemy in enemies[:]:
        distance = sqrt((position[0] - enemy.x) ** 2 + (position[1] - enemy.y) ** 2)
        if distance < 30:  # Collision radius (player and enemy)
            live -= 1  # Reduce player lives when colliding with an enemy
            enemies.remove(enemy)  # Remove the enemy upon collision


def spawn_enemies(num_enemies):
    global maze, cell_size
    for _ in range(num_enemies):
        while True:
            # Randomly choose coordinates in the maze
            x = random.randint(1, len(maze[0]) - 2)  # Avoid the border walls
            y = random.randint(1, len(maze) - 2)    # Avoid the border walls
            
            # Check if the selected cell is an open space (0 represents an open space in the maze)
            if maze[y][x] == 0:
                # Convert maze grid position to world coordinates
                spawn_x = -GRID_LENGTH + x * cell_size + cell_size / 2
                spawn_y = -GRID_LENGTH + y * cell_size + cell_size / 2
                enemies.append(Enemy(spawn_x, spawn_y))
                break  # Break the loop once an enemy has been successfully spawned
def update_enemies():
    for enemy in enemies:
        enemy.move()




def specialKeyListener(key, x, y):
    global cam_height, cam_angle, cam_distance
    if key == GLUT_KEY_UP:
        cam_height = min(cam_height + 10, 800)
        cam_distance = max(cam_distance - 10, 200)
    elif key == GLUT_KEY_DOWN:
        cam_height = max(cam_height - 10, 100)
        cam_distance = min(cam_distance + 10, 800)
    elif key == GLUT_KEY_LEFT:
        cam_angle += 5
    elif key == GLUT_KEY_RIGHT:
        cam_angle -= 5
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global bullets, perspective, paused, game_over, game_exit
    y = 800 - y  # Convert to OpenGL coordinates
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Check pause button
        if (pause_button_rect[0] <= x <= pause_button_rect[0] + pause_button_rect[2] and
            pause_button_rect[1] <= y <= pause_button_rect[1] + pause_button_rect[3]):
            paused = not paused
            glutPostRedisplay()
            return
        
        # Check exit button
        if (exit_button_rect[0] <= x <= exit_button_rect[0] + exit_button_rect[2] and
            exit_button_rect[1] <= y <= exit_button_rect[1] + exit_button_rect[3]):
            game_exit = True
            glutLeaveMainLoop()  # Properly exit GLUT loop
            return

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if perspective == "THIRD_PERSON":
            perspective = "FIRST_PERSON"
        else:
            perspective = "THIRD_PERSON"
        glutPostRedisplay()
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        length = 50
        x_bull = position[0] + cos(radians(player_rotation)) * length
        y_bull = position[1] + sin(radians(player_rotation)) * length
        bullets.append({
            'x': x_bull,
            'y': y_bull,
            'z': 90,
            'angle': player_rotation,
            'speed': bullet_speed
        })
    glutPostRedisplay()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if perspective == "THIRD_PERSON":
        offset_x = cam_distance * cos(radians(cam_angle))
        offset_y = cam_distance * sin(radians(cam_angle))
        look_x = position[0]
        look_y = position[1]
        gluLookAt(position[0] + offset_x,
              position[1] + offset_y,
              cam_height,
              look_x, look_y, 100,
              0, 0, 1)
    else:  
        eye_z = 110  
        eye_forward_offset = 20
        eye_x = position[0] + cos(radians(player_rotation)) * eye_forward_offset
        eye_y = position[1] + sin(radians(player_rotation)) * eye_forward_offset
        look_ahead_distance = 100
        center_x = eye_x + cos(radians(player_rotation)) * look_ahead_distance
        center_y = eye_y + sin(radians(player_rotation)) * look_ahead_distance
        center_z = eye_z  
        gluLookAt(eye_x, eye_y, eye_z,
                 center_x, center_y, center_z,
                 0, 0, 1)  

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    glTranslatef(position[0], position[1], 0)

    if game_over:
        glRotatef(90, 1, 0, 0)
    else:
        glRotatef(player_rotation, 0, 0, 1)
        glRotatef(-90, 0, 0, 1)

    leg_positions = [-10, 10]
    glColor3f(0, 0, 1)
    for x in leg_positions:
        glPushMatrix()
        glTranslatef(x, 0, 0)
        glRotatef(-90, 0, 0, 1)
        gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10)
        glPopMatrix()

    glPushMatrix()
    glColor3f(0.138, 0.558, 0.321)
    glTranslatef(0, 0, 80)
    glScalef(0.7, 0.4, 0.7)
    glutSolidCube(60)
    glPopMatrix()

    arm_positions = [-25, 25]
    glColor3f(0.9, 0.9, 0.6)
    for x in arm_positions:
        glPushMatrix()
        glTranslatef(x, 0, 90)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 40, 10, 10)
        glPopMatrix()

    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    glTranslatef(0, 0, 90)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 3, 50, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0, 0, 0)
    glTranslatef(0, 0, 125)
    gluSphere(gluNewQuadric(), 20, 15, 15)
    glPopMatrix()

    glPopMatrix()

def check_game_over():
    global live, game_over
    if live <= 0 and not game_over:
        game_over = True
        print("Game Over!")



def draw_bullets():
    global bullets
    for b in bullets[:]:
        # Calculate new position based on bullet speed and direction
        new_x = b['x'] + cos(radians(b['angle'])) * b['speed']
        new_y = b['y'] + sin(radians(b['angle'])) * b['speed']

        # Check if the bullet hits a wall
        if not check_collision(new_x, new_y):  # If not colliding with a wall, update bullet position
            b['x'] = new_x
            b['y'] = new_y
        else:
            bullets.remove(b)  # Remove bullet if it collides with a wall
        
        # Draw the bullet
        glPushMatrix()
        glColor3f(1, 0, 0)
        glTranslatef(b['x'], b['y'], b['z'])
        glutSolidSphere(bullet_size, 8, 8)
        glPopMatrix()

        # Remove bullet if it goes out of bounds (off screen)
        if abs(b['x']) > GRID_LENGTH or abs(b['y']) > GRID_LENGTH:
            bullets.remove(b)
    glutPostRedisplay()


def border():
    wall_height = 100
    glColor3f(0.5, 0.0, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glEnd()

# Enhance the check_win_condition function to highlight the exit
def check_win_condition():
    global position, exit_x, exit_y, game_over, score
    # Convert maze exit coordinates to world coordinates
    exit_world_x = -GRID_LENGTH + exit_x * cell_size + cell_size / 2
    exit_world_y = -GRID_LENGTH + exit_y * cell_size + cell_size / 2
    
    # Calculate distance from player to exit
    distance_to_exit = sqrt((position[0] - exit_world_x)**2 + (position[1] - exit_world_y)**2)
    
    # Define a threshold distance to consider the player at the exit
    threshold = cell_size / 2  # Half a cell size is reasonable
    
    if distance_to_exit < threshold and not game_over:
        game_over = True
        score += 50  # Bonus points for winning
        print("You win! Game over.") 


def draw_exit_marker():
    global exit_x, exit_y, cell_size, GRID_LENGTH
    
    # Only draw if maze exists
    if maze is None:
        return
        
    # Convert exit coordinates to world space
    exit_world_x = -GRID_LENGTH + exit_x * cell_size + cell_size / 2
    exit_world_y = -GRID_LENGTH + exit_y * cell_size + cell_size / 2
    
    # Draw a marker at the exit (a green cylinder)
    glPushMatrix()
    glTranslatef(exit_world_x, exit_world_y, 0)
    
    # Animating glow effect
    pulse = (sin(glutGet(GLUT_ELAPSED_TIME) / 300.0) + 1) / 2  # Value between 0 and 1
    
    # Draw exit marker - glowing green cylinder
    glColor3f(0.2, 0.8 * pulse + 0.2, 0.2)
    gluCylinder(gluNewQuadric(), cell_size/4, cell_size/4, 40, 20, 1)
    
    # Add a top to the cylinder
    glTranslatef(0, 0, 40)
    gluDisk(gluNewQuadric(), 0, cell_size/4, 20, 1)
    
    glPopMatrix()


def idle():
    if game_exit:
        return  # Stop all updates if exiting
    
    if not game_over and not paused:
        update_enemies()
        check_player_enemy_collision()
        check_bullet_enemy_collisions()
        check_win_condition()
        check_game_over()
    glutPostRedisplay()
def showScreen():
    if game_exit:
        return  # Don't draw if exiting
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # 3D Scene
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_maze()
    draw_exit_marker()
    draw_bushes_and_trees()
    
    for enemy in enemies:
        enemy.draw()
    
    draw_player()
    draw_bullets()
    border()
    
    # 2D UI Elements
    draw_ui_buttons()
    
    # Text overlays
    glDisable(GL_DEPTH_TEST)
    draw_text(10, 770, f"Lives: {live}  Score: {score}")
    
    if paused:
        draw_text(400, 400, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
    
    if game_over:
        if live <= 0:
            draw_text(10, 730, "GAME OVER - Press R to restart", GLUT_BITMAP_TIMES_ROMAN_24)
        else:
            draw_text(10, 730, f"YOU WIN! {score} Press R to restart", GLUT_BITMAP_TIMES_ROMAN_24)
    glEnable(GL_DEPTH_TEST)
    
    glutSwapBuffers()


def draw_horizon():
    glPushMatrix()
    glBegin(GL_QUADS)
    
    # Gradient for the horizon
    glColor3f(0.529, 0.808, 0.922)  # Light sky blue (top of the horizon)
    glVertex3f(-GRID_LENGTH * 2, -GRID_LENGTH * 2, 0)
    glVertex3f(GRID_LENGTH * 2, -GRID_LENGTH * 2, 0)
    
    glColor3f(0.8, 0.8, 0.6)  # Light beige (bottom of the horizon)
    glVertex3f(GRID_LENGTH * 2, GRID_LENGTH * 2, 0)
    glVertex3f(-GRID_LENGTH * 2, GRID_LENGTH * 2, 0)
    
    glEnd()
    glPopMatrix()
    

def draw_bushes_and_trees():
    # Draw bushes
    for i in range(-GRID_LENGTH - 100, GRID_LENGTH + 200, 200):
        for j in [-GRID_LENGTH - 100, GRID_LENGTH + 100]:
            glPushMatrix()
            glTranslatef(i, j, 0)
            glColor3f(0.0, 0.5, 0.0)  # Green color for bushes
            gluSphere(gluNewQuadric(), 30, 16, 16)  # Bush as a sphere
            glPopMatrix()

    # Draw trees
    for i in range(-GRID_LENGTH - 200, GRID_LENGTH + 300, 300):
        for j in [-GRID_LENGTH - 200, GRID_LENGTH + 200]:
            # Tree trunk
            glPushMatrix()
            glTranslatef(i, j, 0)
            glColor3f(0.55, 0.27, 0.07)  # Brown color for trunk
            gluCylinder(gluNewQuadric(), 10, 10, 50, 16, 16)  # Trunk as a cylinder
            glPopMatrix()

            # Tree foliage
            glPushMatrix()
            glTranslatef(i, j, 50)  # Position foliage above the trunk
            glColor3f(0.0, 0.5, 0.0)  # Green color for foliage
            gluSphere(gluNewQuadric(), 40, 16, 16)  # Foliage as a sphere
            glPopMatrix()

def main():
    glutInit()
    global maze, cell_size
    # Ensure the maze is generated and player is positioned first
    if maze is None:
        maze_size = 21  # Should be odd for proper maze borders
        maze = generate_maze(maze_size)
        cell_size = (GRID_LENGTH * 2) / len(maze)  # Adjust cell size based on maze size

    # Now that cell_size is set, we can set the player position
    set_player_at_entry()

    # Now you can spawn enemies
    spawn_enemies(10)

    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    
    glutCreateWindow(b"Project01 - Maze Explorer")
    glutInitWindowPosition(100, 100)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.529, 0.808, 0.922, 1.0)  


    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)

    glutMainLoop()



if __name__ == "__main__":
    main()
