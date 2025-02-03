import pygame
import psycopg2
import sys
import os
from logic.ui import LoginApp
# from logic.leaderboard import ScoreApp
import socket
import tkinter as tk
import math
import time
from kivy.clock import Clock
import multiprocessing
from pathlib import Path
from dotenv import load_dotenv
from kivy.config import Config
Config.set('kivy', 'log_level', 'info')
load_dotenv(override=True)


# --------------------------------------------------------------------------------
# Configuration and Global Variables
# --------------------------------------------------------------------------------

POSTGRES_HOST = os.getenv('POSTGRES_HOST')        # e.g., "localhost" or "remote.server.com"
POSTGRES_DB = os.getenv('POSTGRES_DB') 
POSTGRES_USER = os.getenv('POSTGRES_USER') 
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD') 
POSTGRES_PORT = os.getenv('POSTGRES_PORT') # Default PostgreSQL port is 5432


POSTGRES_PASSWORD="lg5EBC4000KYzsS5D5eJ"  
POSTGRES_USER="nikita"             
POSTGRES_DB="main_db"  
POSTGRES_PORT=6000     
POSTGRES_HOST="185.139.69.220"


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
        pygame.Rect(50, 50, 500, 40),
        pygame.Rect(50, 410, 500, 40),
        pygame.Rect(50, 50, 40, 400),
        pygame.Rect(510, 50, 40, 400)  # New rectangle added
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

def get_all_users_scores(conn):
    """
    Retrieve all users' scores from the database and return as a dictionary
    with the username as the key and high_score as the value.
    """
    query = "SELECT username, high_score FROM users"
    scores = {}

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            if results:
                scores = {row[0]: row[1] for row in results}  # Convert to dictionary
            else:
                print("No scores found in the database.")
    except Exception as e:
        print(f"Error fetching scores: {e}")

    return scores  # Returns a dictionary of {username: high_score}

# --------------------------------------------------------------------------------
# Game Logic
# --------------------------------------------------------------------------------
def start_kivy():
    """
    Runs leaderboard.py using the bundled Python interpreter inside the PyInstaller environment.
    """
    base_dir = Path(sys.executable).parent  # Get directory of main.exe
    leaderboard_script = base_dir / "_internal" / "logic" / "leaderboard.py"  # Adjust if necessary

    print(f"Starting Kivy application from: {leaderboard_script}")

    try:
        # Use multiprocessing to start a new process
        multiprocessing.Process(target=exec_leaderboard, args=(leaderboard_script,)).start()
    except Exception as e:
        print(f"Failed to start Kivy application: {e}")

def exec_leaderboard(script_path):
    """
    Reads and executes leaderboard.py while setting __file__ manually.
    """
    global_vars = {"__name__": "__main__", "__file__": script_path, "sys": sys}  # Set __file__
    
    with open(script_path, "r", encoding="utf-8") as f:
        exec(f.read(), global_vars)

def stop_kivy():
    global kivy_process
    if kivy_process and kivy_process.poll() is None:  # Check if it's still running
        print("Stopping Kivy application...")
        kivy_process.terminate()  # Graceful termination
        time.sleep(1)  # Allow time to close properly
        kivy_process.kill()  # Force kill if still running
        kivy_process = None


def run_game(username, conn):
    """
    Main game loop. The player starts at level 1 or at the user's existing high_score + 1.
    The user can move with the arrow keys or WASD to reach the top-right corner.
    When a level is completed, if it is the user's highest completed level, we update DB.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("10-Level Wall Maze")
    user_function = None
    collided = True
    input_active = True
    clock = pygame.time.Clock()
    
    
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    # Load textures
    background_texture = pygame.image.load(os.path.join(assets_dir, "background.jpg")).convert()
    player_texture = pygame.image.load(os.path.join(assets_dir, "player.png")).convert_alpha()
    wall_texture = pygame.image.load(os.path.join(assets_dir, "wall.png")).convert_alpha()
    exit_texture = pygame.image.load(os.path.join(assets_dir, "exit.jpg")).convert_alpha()
    
    # Optionally scale player texture if PLAYER_SIZE is fixed:
    player_texture = pygame.transform.scale(player_texture, (PLAYER_SIZE, PLAYER_SIZE))

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
            print("Game Over. Closing Pygame...")

            pygame.quit()  # Quit Pygame properly

            # Start the Kivy app
            start_kivy()

            # Simulating some delay before stopping (for testing)
            time.sleep(30)  # Let Kivy run for 5 seconds before stopping
            stop_kivy()

            print("Kivy stopped. Exiting program...")
            sys.exit()

        for event in pygame.event.get():
            if event.type == 32787: #exit type
                print("Exit button pressed. Exiting game.")
                running = False  # Exit the main loop
                
        dx, dy = 0, 0
        #! KEYBOARD INPUT
        # keys = pygame.key.get_pressed()
        
        # if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        #     dx = -PLAYER_SPEED
        # if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        #     dx = PLAYER_SPEED
        # if keys[pygame.K_UP] or keys[pygame.K_w]:
        #     dy = -PLAYER_SPEED
        # if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        #     dy = PLAYER_SPEED
        
        #! REDRAW FUNC
        def redraw():
            screen.blit(background_texture, (0, 0))  # black background

            # Draw walls
            for wall in walls:
                wall_tex_scaled = pygame.transform.scale(wall_texture, (wall.width, wall.height))
                screen.blit(wall_tex_scaled, (wall.x, wall.y))

            # Draw player
            screen.blit(player_texture, (player_rect.x, player_rect.y))
            
            # Draw exit area
            exit_area_rect = pygame.Rect(SCREEN_WIDTH - 100, 0, 100, 100)
            exit_tex_scaled = pygame.transform.scale(exit_texture, (exit_area_rect.width, exit_area_rect.height))
            screen.blit(exit_tex_scaled, (exit_area_rect.x, exit_area_rect.y))

            # Display current level
            font = pygame.font.SysFont(None, 36)
            text_surface = font.render(f"Level: {current_level}", True, (255, 255, 255))
            screen.blit(text_surface, (10, 10))

            pygame.display.flip()

        # Save old position in case we collide
        
        old_x, old_y = player_rect.x, player_rect.y

        # Move
        player_rect.x += dx
        player_rect.y += dy
        
        # Get walls for current level
        walls = get_level_walls(current_level)

        # Collision detection: if collide with any wall, revert movement
        #! COLISION HANDLING
       
        for wall in walls:
            if player_rect.colliderect(wall):
                player_rect.x = old_x
                player_rect.y = old_y
                collided = True
                
        if player_rect.x < 0 or player_rect.y < 0 or \
           player_rect.x + PLAYER_SIZE > SCREEN_WIDTH or \
           player_rect.y + PLAYER_SIZE > SCREEN_HEIGHT:
           player_rect.x = max(1, min(player_rect.x, SCREEN_WIDTH - PLAYER_SIZE))
           player_rect.y = max(1, min(player_rect.y, SCREEN_HEIGHT - PLAYER_SIZE))
           collided = True
  
        if collided:
            user_function = None
            if player_rect.colliderect(wall):
                BUFFER_DISTANCE = 2  # Distance to keep from the wall
                if player_rect.right >= wall.left and player_rect.left <= wall.left:
                    player_rect.right = wall.left - BUFFER_DISTANCE  # Move player to the left of the wall
                elif player_rect.left <= wall.right and player_rect.right >= wall.right:
                    player_rect.left = wall.right + BUFFER_DISTANCE  # Move player to the right of the wall
                if player_rect.bottom >= wall.top and player_rect.top <= wall.top:
                    player_rect.bottom = wall.top - BUFFER_DISTANCE  # Move player above the wall
                elif player_rect.top <= wall.bottom and player_rect.bottom >= wall.bottom:
                    player_rect.top = wall.bottom + BUFFER_DISTANCE  # Move player below the wall
            if player_rect.x < 0:
                player_rect.x = 0 + BUFFER_DISTANCE
            if player_rect.y < 0:
                player_rect.y = 0 + BUFFER_DISTANCE
            if player_rect.x + PLAYER_SIZE > SCREEN_WIDTH:
                player_rect.x = SCREEN_WIDTH - PLAYER_SIZE - BUFFER_DISTANCE
            if player_rect.y + PLAYER_SIZE > SCREEN_HEIGHT:
                player_rect.y = SCREEN_HEIGHT - PLAYER_SIZE - BUFFER_DISTANCE
            redraw()
            print("Collision detected! Please input a function to execute:")
            input_active = True
                    
        

            
        if input_active:
            def get_user_input():
                root = tk.Tk()
                root.title("Input Window")

                # Get screen width and height
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()

                # Window dimensions
                window_width = 300
                window_height = 100

                # Calculate position to center the window
                x_position = (screen_width // 2) - (window_width // 2)
                y_position = (screen_height // 2) - (window_height // 2)

                # Set window geometry (Width x Height + X_Position + Y_Position)
                root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

                user_input_var = tk.StringVar()  # StringVar to store input

                def submit_data():
                    if not user_input_var.get().strip():
                        print("Error: User input cannot be blank.")
                        return  # Do not close the window; let the user retry

                    root.quit()  # Quit event loop

                # Entry widget
                entry = tk.Entry(root, textvariable=user_input_var, width=40)
                entry.pack(padx=10, pady=10)

                # Submit button
                submit_button = tk.Button(root, text="Submit", command=submit_data)
                entry.bind("<Return>", lambda event: submit_data())
                submit_button.pack(padx=10, pady=10)

                root.mainloop()  # Start Tkinter event loop
                root.destroy()  # Ensure cleanup

                return user_input_var.get()  # Return user input after window closes
            
            user_function = get_user_input()
            input_active = False
            collided = False
            print("User input received:", user_function)

        
        if user_function:
            try:
                if user_function.strip() == "":
                    input_active = True
                    raise ValueError("User function cannot be blank.")
                
                # Extract the mathematical expression from the user input (e.g., "asc!y=x-5")
                pack = user_function.split("!")
                if len(pack) != 2:
                    input_active = True
                    raise ValueError("Invalid format. Expected format: <seq_type>!<expression> (e.g., asc!y=x-5).")
                
                seq_type = pack[0]
                math_expression = pack[1].split('=')[1].strip()

                print(seq_type, math_expression)
                
                # Prepare the environment for evaluating the math expression
                safe_globals = {
                    "math": math,
                    "cos": math.cos,
                    "sin": math.sin,
                    "abs": abs,
                    "pow": pow
                }
                
                try:
                    math_function = eval(f"lambda x: {math_expression}", safe_globals)
                except Exception as eval_error:
                    input_active = True
                    raise ValueError(f"Invalid mathematical expression: {math_expression}. Error: {eval_error}")
                
                x_value = 10  
                if seq_type.lower() == "asc":
                    player_rect.x += x_value
                    player_rect.y -= math_function(x_value)

                    
                elif seq_type.lower() == "desc":
                    player_rect.x -= x_value
                    player_rect.y -= math_function(x_value)

                else:
                    input_active = True
                    raise ValueError(f"Invalid sequence type: {seq_type}. Expected 'asc' or 'desc'.")
                    
                
                print("user_func", player_rect.x, player_rect.y)

            except ValueError as ve:
                print("Value Error:", ve)
                input_active = True
            except Exception as e:
                print("Unexpected Error:", e)
                input_active = True

        # Check if player reached top-right corner region:
        # Let's define "reached top-right corner" as x > SCREEN_WIDTH - 100 and y < 100
        if player_rect.x > SCREEN_WIDTH - 100 and player_rect.y < 100:
            print(f"Level {current_level} Complete!")
            collided = False
            user_function = None
            
            # Update the user's high_score in DB if this is the highest level they've reached
            if current_level > get_user_high_score(conn, username):
                update_user_high_score(conn, username, current_level)
            current_level += 1
            # Reset player position for next level
            player_rect.x = 0
            player_rect.y = SCREEN_HEIGHT - PLAYER_SIZE
            collided = True
            input_active = True

        # Draw everything
        redraw()
    pygame.quit()

def main():
    # Проверка интернет соединения
    if check_internet_connection():
        print("Internet connection detected.")
        conn = create_connection()
        if conn:
            create_tables(conn)
            x = LoginApp(conn=conn)
            x.run()
            if x.username:
                x.terminate()
                run_game(x.username, conn)
            else:
                print("Невозможно авторизовать пользователя. Выход.")
            conn.close()
        else:
            print("Невозможно подключится к базе данных. Выход.")
    else:
        print("Нет интернет соединения. Невозможно авторизоваться или зарегистрировать пользователя.")
        print("Игра требует подклюбчения к базе данных.")
    

# def show_leaderboard(conn):
#     """Run ScoreApp to display leaderboard safely after game ends."""
#     print("Displaying leaderboard...")
#     leaderboard = ScoreApp(conn, get_all_users_scores(conn))
#     leaderboard.run()
#     leaderboard.terminate()
    
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
