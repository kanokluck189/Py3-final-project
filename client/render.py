# Draw the 2D top-down map
# Render players
# Visually indicate:
    # Who is “It”
    # Smaller player size
    # Faster player effect
# Show frozen players (simple color or text)

import pygame


class Renderer:
    def __init__(self, width=1200, height=800):
        # Initialize Pygame
        pygame.init()
        
        # Screen setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Peepat - Multiplayer Tag Game")
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colors
        self.colors = {
            'background': (20, 20, 30),
            'grid': (40, 40, 50),
            'player_normal': (100, 200, 255),
            'player_it': (255, 100, 100),
            'player_frozen': (150, 150, 200),
            'player_self_outline': (255, 255, 100),
            'player_outline': (255, 255, 255),
            'text': (255, 255, 255),
            'text_gray': (150, 150, 150),
            'ui_bg': (40, 40, 50),
            'freeze_phase': (255, 100, 100),
            'move_phase': (100, 255, 100)
        }

    def clear_screen(self):
        """Clear the screen with background color"""
        self.screen.fill(self.colors['background'])

    def draw_grid(self):
        """Draw background grid"""
        grid_spacing = 50
        
        # Vertical lines
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(
                self.screen, 
                self.colors['grid'], 
                (x, 0), 
                (x, self.height), 
                1
            )
        
        # Horizontal lines
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(
                self.screen, 
                self.colors['grid'], 
                (0, y), 
                (self.width, y), 
                1
            )

    def draw_player(self, player_id, player_data, is_self=False):
        """Draw a single player"""
        x = int(player_data.get("x", 0))
        y = int(player_data.get("y", 0))
        size = int(player_data.get("size", 20))
        is_it = player_data.get("is_it", False)
        freeze = player_data.get("freeze", 0)
        
        # Determine color based on state
        if freeze > 0:
            color = self.colors['player_frozen']
        elif is_it:
            color = self.colors['player_it']
        else:
            color = self.colors['player_normal']
        
        # Draw player circle
        pygame.draw.circle(self.screen, color, (x, y), size)
        
        # Draw outline (thicker for self)
        outline_width = 3 if is_self else 2
        outline_color = self.colors['player_self_outline'] if is_self else self.colors['player_outline']
        pygame.draw.circle(self.screen, outline_color, (x, y), size, outline_width)
        
        # Draw player label
        label = f"P{player_id}"
        if is_self:
            label += " (YOU)"
        if is_it:
            label += " - IT"
        
        label_surface = self.font_small.render(label, True, self.colors['text'])
        label_rect = label_surface.get_rect(center=(x, y - size - 15))
        self.screen.blit(label_surface, label_rect)
        
        # Draw freeze timer if frozen
        if freeze > 0:
            freeze_text = f"{freeze:.1f}s"
            freeze_surface = self.font_small.render(freeze_text, True, (255, 150, 150))
            freeze_rect = freeze_surface.get_rect(center=(x, y + size + 15))
            self.screen.blit(freeze_surface, freeze_rect)

    def draw_all_players(self, players, self_player_id):
        """Draw all players in the game"""
        for player_id, player_data in players.items():
            is_self = (str(self_player_id) == str(player_id))
            self.draw_player(player_id, player_data, is_self)

    def draw_game_state_panel(self, game_state, player_data):
        """Draw the main game state panel"""
        panel_width = 350
        panel_height = 120
        panel_x = 10
        panel_y = 10
        
        # Background
        pygame.draw.rect(
            self.screen, 
            self.colors['ui_bg'], 
            (panel_x, panel_y, panel_width, panel_height)
        )
        pygame.draw.rect(
            self.screen, 
            self.colors['text'], 
            (panel_x, panel_y, panel_width, panel_height), 
            2
        )
        
        # Game phase text
        phase = game_state.get("game_state", "unknown")
        if phase == "freeze":
            phase_text = "FREEZE PHASE"
            phase_color = self.colors['freeze_phase']
            hint_text = "Get ready..."
        else:
            phase_text = "MOVEMENT PHASE"
            phase_color = self.colors['move_phase']
            
            # Check if player is frozen
            if player_data:
                freeze = player_data.get("freeze", 0)
                if freeze > 0:
                    hint_text = f"Frozen! {freeze:.1f}s"
                else:
                    hint_text = "WASD/Arrows to move"
            else:
                hint_text = "WASD/Arrows to move"
        
        # Render phase
        phase_surface = self.font_medium.render(phase_text, True, phase_color)
        self.screen.blit(phase_surface, (panel_x + 15, panel_y + 15))
        
        # Render hint
        hint_surface = self.font_small.render(hint_text, True, self.colors['text'])
        self.screen.blit(hint_surface, (panel_x + 15, panel_y + 55))
        
        # Player count
        player_count = len(game_state.get("players", {}))
        count_text = f"Players: {player_count}"
        count_surface = self.font_small.render(count_text, True, self.colors['text'])
        self.screen.blit(count_surface, (panel_x + 15, panel_y + 85))

    def draw_connection_status(self, connected):
        """Draw connection status warning if disconnected"""
        if not connected:
            status_text = "DISCONNECTED"
            status_color = (255, 50, 50)
            status_surface = self.font_large.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(self.width // 2, 50))
            
            # Background for visibility
            bg_rect = status_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, self.colors['ui_bg'], bg_rect)
            pygame.draw.rect(self.screen, status_color, bg_rect, 2)
            
            self.screen.blit(status_surface, status_rect)

    def draw_controls_hint(self):
        """Draw controls at bottom of screen"""
        instructions = [
            "Controls: WASD or Arrow Keys to move",
            "Objective: If you're IT, tag another player!",
            "Press ESC to quit"
        ]
        
        y_pos = self.height - 80
        for instruction in instructions:
            text_surface = self.font_small.render(instruction, True, self.colors['text_gray'])
            text_rect = text_surface.get_rect(center=(self.width // 2, y_pos))
            self.screen.blit(text_surface, text_rect)
            y_pos += 25

    def render_frame(self, game_state, player_id, connected):
        """Render a complete frame"""
        # Clear screen
        self.clear_screen()
        
        # Draw grid
        self.draw_grid()
        
        # Get player data
        player_data = None
        if player_id is not None:
            player_data = game_state.get("players", {}).get(str(player_id))
        
        # Draw all players
        players = game_state.get("players", {})
        self.draw_all_players(players, player_id)
        
        # Draw UI elements
        self.draw_game_state_panel(game_state, player_data)
        self.draw_connection_status(connected)
        self.draw_controls_hint()

    def update_display(self):
        """Update the display (call after all drawing is done)"""
        pygame.display.flip()

    def quit(self):
        """Cleanup Pygame"""
        pygame.quit()