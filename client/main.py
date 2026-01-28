# Initialize Pygame
# Run the game loop
# Capture keyboard input
# Send movement input to server
# Call render and network updates

import pygame
import socket
import json
import threading

# Configuration
SERVER_HOST = "localhost"
SERVER_PORT = 5555
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60


class GameClient:
    def __init__(self):      
        # INITIALIZE PYGAME
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Peepat Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Network
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.player_id = None
        
        # Game state received from server
        self.game_state = {
            "game_state": "freeze",
            "players": {}
        }
        
        self.running = True

    def connect_to_server(self):
        """Connect to game server"""
        try:
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            self.connected = True
            
            # Start thread to receive updates from server
            threading.Thread(target=self.receive_updates, daemon=True).start()
            
            print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False


    # NETWORK UPDATES - Receive from server

    def receive_updates(self):
        """Continuously receive game state from server"""
        buffer = ""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    self.connected = False
                    break
                
                buffer += data
                
                # Process complete messages (separated by newlines)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message:
                        self.process_server_message(message)
            except:
                self.connected = False
                break

    def process_server_message(self, message):
        """Process incoming message from server"""
        try:
            data = json.loads(message)
            
            # Update game state
            if data.get("type") == "state":
                self.game_state = data
            
            # Receive our player ID
            elif data.get("type") == "player_id":
                self.player_id = data["id"]
                print(f"Player ID assigned: {self.player_id}")
                
        except json.JSONDecodeError:
            pass


    # CAPTURE KEYBOARD INPUT

    def capture_input(self):
        """Capture keyboard input and return movement direction"""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        # Check if we can move
        can_move = False
        if self.player_id is not None:
            player_data = self.game_state.get("players", {}).get(str(self.player_id))
            if player_data:
                is_frozen = player_data.get("freeze", 0) > 0
                game_playing = self.game_state.get("game_state") == "playing"
                can_move = game_playing and not is_frozen
        
        # Get input if allowed to move
        if can_move:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += 1
            
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
        
        return dx, dy


    # SEND MOVEMENT INPUT TO SERVER

    def send_movement(self, dx, dy):
        """Send movement input to server"""
        if not self.connected:
            return
        
        try:
            message = json.dumps({
                "type": "move",
                "dx": dx,
                "dy": dy
            }) + '\n'
            
            self.socket.sendall(message.encode('utf-8'))
        except:
            self.connected = False


    # RENDER

    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill((20, 20, 30))
        
        # Draw all players
        players = self.game_state.get("players", {})
        for player_id, player_data in players.items():
            x = int(player_data.get("x", 0))
            y = int(player_data.get("y", 0))
            size = int(player_data.get("size", 20))
            is_it = player_data.get("is_it", False)
            freeze = player_data.get("freeze", 0)
            is_self = (str(self.player_id) == str(player_id))
            
            # Choose color
            if freeze > 0:
                color = (150, 150, 200)  # Purple - frozen
            elif is_it:
                color = (255, 100, 100)  # Red - IT
            else:
                color = (100, 200, 255)  # Blue - normal
            
            # Draw player
            pygame.draw.circle(self.screen, color, (x, y), size)
            
            # Draw outline for self
            if is_self:
                pygame.draw.circle(self.screen, (255, 255, 100), (x, y), size, 3)
            
            # Draw label
            label = f"P{player_id}"
            if is_it:
                label += " IT"
            text = self.font.render(label, True, (255, 255, 255))
            text_rect = text.get_rect(center=(x, y - size - 20))
            self.screen.blit(text, text_rect)
        
        # Draw game state info
        game_state = self.game_state.get("game_state", "unknown")
        if game_state == "freeze":
            state_text = "FREEZE PHASE - Get Ready!"
            color = (255, 100, 100)
        else:
            state_text = "MOVEMENT PHASE"
            color = (100, 255, 100)
        
        text = self.font.render(state_text, True, color)
        self.screen.blit(text, (20, 20))
        
        # Draw controls hint
        hint = self.font.render("WASD to move | ESC to quit", True, (150, 150, 150))
        self.screen.blit(hint, (20, SCREEN_HEIGHT - 50))
        
        # Update display
        pygame.display.flip()


    # RUN THE GAME LOOP

    def run(self):
        """Main game loop"""
        # Connect to server
        if not self.connect_to_server():
            print("Failed to connect to server")
            return
        
        print("Game started! Use WASD to move")
        
        # Main loop
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Capture keyboard input
            dx, dy = self.capture_input()
            
            # Send movement input to server
            if dx != 0 or dy != 0:
                self.send_movement(dx, dy)
            
            # Render
            self.render()
            
            # Maintain FPS
            self.clock.tick(FPS)
        
        # Cleanup
        if self.connected:
            self.socket.close()
        pygame.quit()



# ENTRY POINT
def main():
    client = GameClient()
    client.run()


if __name__ == '__main__':
    main()
