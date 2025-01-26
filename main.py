import pygame
import psycopg2
import sys
import os
from logic.ui import LoginApp
from logic.dialogpopup import FuncApp
import socket
from dotenv import load_dotenv
from multiprocessing import Process
load_dotenv()


# --------------------------------------------------------------------------------
# Configuration and Global Variables
# --------------------------------------------------------------------------------

POSTGRES_HOST = os.getenv('POSTGRES_HOST')        # e.g., "localhost" or "remote.server.com"
POSTGRES_DB = os.getenv('POSTGRES_DB') 
POSTGRES_USER = os.getenv('POSTGRES_USER') 
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD') 
POSTGRES_PORT = os.getenv('POSTGRES_PORT')                         # Default PostgreSQL port is 5432

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_SPEED = 5
PLAYER_SIZE = 30

# The game has 10 levels. Each level has a unique arrangement of walls.
# We'll store walls as lists of Rects (x, y, width, height).
# For simplicity, these are just "example" walls; feel free to customize.
def get_level_walls(level_num):
    # A simple function that returns walls for each level.
    # You can adjust or add more complex designs.
    # The coordinate system: (0,0) is top-left by default in Pygame.
    
    if level_num == 1:
        return [
            pygame.Rect(200, 100, 50, 400),
            pygame.Rect(400, 50, 50, 400),
            pygame.Rect(600, 150, 50, 400),
        ]
    elif level_num == 2:
        return [
            pygame.Rect(100, 200, 600, 50),
            pygame.Rect(200, 400, 400, 50),
        ]
    elif level_num == 3:
        return [
            pygame.Rect(100, 100, 50, 300),
            pygame.Rect(300, 200, 50, 300),
            pygame.Rect(500, 100, 50, 300),
        ]
    elif level_num == 4:
        return [
            pygame.Rect(150, 150, 500, 50),
            pygame.Rect(150, 300, 500, 50),
        ]
    elif level_num == 5:
        return [
            pygame.Rect(50, 50, 700, 40),
            pygame.Rect(50, 510, 700, 40),
            pygame.Rect(50, 50, 40, 500),
            pygame.Rect(710, 50, 40, 500),
            pygame.Rect(300, 200, 200, 50),
        ]
    elif level_num == 6:
        return [
            pygame.Rect(200, 200, 50, 300),
            pygame.Rect(400, 100, 50, 300),
            pygame.Rect(600, 250, 50, 300),
        ]
    elif level_num == 7:
        return [
            pygame.Rect(100, 300, 600, 50),
            pygame.Rect(200, 100, 50, 200),
            pygame.Rect(550, 350, 50, 200),
        ]
    elif level_num == 8:
        return [
            pygame.Rect(100, 100, 600, 50),
            pygame.Rect(100, 200, 50, 300),
            pygame.Rect(200, 450, 500, 50),
            pygame.Rect(700, 250, 50, 200),
        ]
    elif level_num == 9:
        return [
            pygame.Rect(150, 150, 500, 50),
            pygame.Rect(150, 150, 50, 300),
            pygame.Rect(600, 150, 50, 300),
            pygame.Rect(150, 400, 500, 50),
        ]
    elif level_num == 10:
        return [
            pygame.Rect(100, 100, 600, 400),
            pygame.Rect(200, 200, 400, 200),
        ]
    else:
        return []

# --------------------------------------------------------------------------------
# Database Functions
# --------------------------------------------------------------------------------

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    A simple way to check if the local machine has internet access.
    Tries to open a socket to 8.8.8.8 (Google DNS) on port 53.
    Returns True if successful, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print("No internet connection:", ex)
        return False

def create_connection():
    """
    Create a connection to the PostgreSQL database.
    Returns a psycopg2 connection or None if failed.
    """
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        return conn
    except Exception as e:
        print("Failed to connect to database:", e)
        return None

def create_tables(conn):
    """
    Create the 'users' table if it does not exist.
    """
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        high_score INTEGER DEFAULT 0
    )
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()


def get_user_high_score(conn, username):
    """
    Get the user's high_score from the database.
    """
    query = "SELECT high_score FROM users WHERE username = %s"
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        row = cur.fetchone()
        if row:
            return row[0]
    return 0

def update_user_high_score(conn, username, new_score):
    """
    Update the user's high_score if new_score is greater than current high_score.
    """
    current_score = get_user_high_score(conn, username)
    if new_score > current_score:
        query = "UPDATE users SET high_score = %s WHERE username = %s"
        with conn.cursor() as cur:
            cur.execute(query, (new_score, username))
        conn.commit()

# --------------------------------------------------------------------------------
# Game Logic
# --------------------------------------------------------------------------------

def run_game(username, conn):
    """
    Main game loop. The player starts at level 1 or at the user's existing high_score + 1.
    The user can move with the arrow keys or WASD to reach the top-right corner.
    When a level is completed, if it is the user's highest completed level, we update DB.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("10-Level Wall Maze")
    is_func_dialog = False
    clock = pygame.time.Clock()

    # If user has a high_score, that means they've completed that many levels.
    # Start them on the next level, but do not exceed 10.
    start_level = get_user_high_score(conn, username) + 1
    if start_level > 10:
        start_level = 10

    current_level = start_level

    # Player starts at bottom-left corner, which we define as:
    # (0, SCREEN_HEIGHT - PLAYER_SIZE)
    player_rect = pygame.Rect(0, SCREEN_HEIGHT - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)

    running = True
    while running:
        clock.tick(FPS)

        # Close the game if all levels are done
        if current_level > 10:
            print("Congratulations! You've completed all levels!")
            break

        for event in pygame.event.get():
            if event.type == 32787: #exit type
                print("Exit button pressed. Exiting game.")
                running = False  # Exit the main loop

        # Movement input
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = PLAYER_SPEED

        # Save old position in case we collide
        old_x, old_y = player_rect.x, player_rect.y

        # Move
        player_rect.x += dx
        player_rect.y += dy

        # Get walls for current level
        walls = get_level_walls(current_level)

        # Collision detection: if collide with any wall, revert movement
        #! COLISION HANDLING
        collided = False
        for wall in walls:
            if player_rect.colliderect(wall):
                player_rect.x = old_x
                player_rect.y = old_y
                collided = True
                
        if player_rect.x < 0 or player_rect.y < 0 or \
           player_rect.x + PLAYER_SIZE > SCREEN_WIDTH or \
           player_rect.y + PLAYER_SIZE > SCREEN_HEIGHT:
            player_rect.x = max(0, min(player_rect.x, SCREEN_WIDTH - PLAYER_SIZE))
            player_rect.y = max(0, min(player_rect.y, SCREEN_HEIGHT - PLAYER_SIZE))
            collided = True
  
            
        if collided:
            print("colided")

        #! COLISION HANDLING
        # Keep player within screen bounds (optional, so we don't go off-screen)
        if player_rect.x < 0:
            player_rect.x = 0
        if player_rect.y < 0:
            player_rect.y = 0
        if player_rect.x + PLAYER_SIZE > SCREEN_WIDTH:
            player_rect.x = SCREEN_WIDTH - PLAYER_SIZE
        if player_rect.y + PLAYER_SIZE > SCREEN_HEIGHT:
            player_rect.y = SCREEN_HEIGHT - PLAYER_SIZE

        # Check if player reached top-right corner region:
        # Let's define "reached top-right corner" as x > SCREEN_WIDTH - 100 and y < 100
        if player_rect.x > SCREEN_WIDTH - 100 and player_rect.y < 100:
            print(f"Level {current_level} Complete!")
            
            # Update the user's high_score in DB if this is the highest level they've reached
            if current_level > get_user_high_score(conn, username):
                update_user_high_score(conn, username, current_level)

            current_level += 1
            # Reset player position for next level
            player_rect.x = 0
            player_rect.y = SCREEN_HEIGHT - PLAYER_SIZE

        # Draw everything
        screen.fill((0, 0, 0))  # black background

        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, (200, 200, 200), wall)

        # Draw player
        pygame.draw.rect(screen, (0, 255, 0), player_rect)

        # Display current level
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(f"Level: {current_level}", True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

        pygame.display.flip()

    pygame.quit()

def main():
    # Check for internet connection
    if check_internet_connection():
        print("Internet connection detected.")
        conn = create_connection()
        if conn:
            create_tables(conn)
            #! 
            x = LoginApp(conn=conn)
            x.run()
            if x.username:
                x.terminate()
                run_game(x.username, conn)
            else:
                print("Could not authenticate or register user. Exiting.")
            conn.close()
        else:
            print("Could not connect to the database. Exiting.")
    else:
        print("No internet connection. You cannot authenticate or register.")
        print("Game requires database access, so we must exit.")

if __name__ == "__main__":
    main()
