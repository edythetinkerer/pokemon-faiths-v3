import pygame
import sys
import math
from constants import (
    DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, Colors,
    TEXT_SPEED, MAX_NAME_CHARS, FADE_SPEED, ELDER_BOB_SPEED, ELDER_BOB_AMPLITUDE
)
from ui.ui_components import GradientBackground
from core.logger import get_logger

logger = get_logger('IntroSequence')

class TextBox:
    def __init__(self, width, height, pos_y, font_size=32):
        # Input validation
        if width <= 0 or height <= 0:
            raise ValueError("TextBox width and height must be positive")
        if font_size <= 0:
            raise ValueError("Font size must be positive")
            
        self.width = width
        self.height = height
        self.pos_y = pos_y
        self.font = pygame.font.SysFont("georgia", font_size)
        self.text_color = Colors.TEXT_PRIMARY
        self.box_color = (*Colors.BACKGROUND_BOTTOM, 200) # Use tuple unpacking for alpha
        self.border_color = Colors.BUTTON_NORMAL
        self.text_speed = TEXT_SPEED
        self.current_text = ""
        self.target_text = ""
        self.text_index = 0
        self.is_finished = False
        self.padding = 20

    def start_text(self, text):
        self.target_text = text
        self.current_text = ""
        self.text_index = 0
        self.is_finished = False

    def update(self):
        if not self.is_finished:
            self.text_index += self.text_speed
            self.current_text = self.target_text[:self.text_index]
            if self.text_index >= len(self.target_text):
                self.is_finished = True

    def draw(self, screen, x_offset=50):  # Add x_offset parameter
        # Create box surface with alpha
        box_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, self.box_color, box_surface.get_rect())
        pygame.draw.rect(box_surface, self.border_color, box_surface.get_rect(), 2)
        
        # Draw text with wrapping
        words = self.current_text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, self.text_color)
            if test_surface.get_width() < self.width - self.padding * 2:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        # Draw each line
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            y_pos = self.padding + i * (self.font.get_linesize() + 5)
            box_surface.blit(text_surface, (self.padding, y_pos))
        
        # Draw box on screen (using x_offset instead of centering)
        screen.blit(box_surface, (x_offset, self.pos_y))

class NameInput:
    def __init__(self, width, height, pos_y):
        # Input validation
        if width <= 0 or height <= 0:
            raise ValueError("NameInput width and height must be positive")
            
        self.width = width
        self.height = height
        self.pos_y = pos_y
        self.font = pygame.font.SysFont("georgia", 32)
        self.text_color = Colors.TEXT_PRIMARY
        self.box_color = (*Colors.BACKGROUND_BOTTOM, 200)
        self.border_color = Colors.BUTTON_NORMAL
        self.active_border_color = Colors.BUTTON_HOVER
        self.name = ""
        self.active = False
        self.max_chars = MAX_NAME_CHARS
        self.padding = 20
        self.blink_time = 0
        self.show_cursor = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.name.strip()) > 0:
                    return True
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif len(self.name) < self.max_chars and event.unicode.isalnum():
                self.name += event.unicode
        return False

    def update(self, time):
        self.blink_time = time
        self.show_cursor = int(time * 2) % 2 == 0

    def draw(self, screen, x_offset=50):  # Add x_offset parameter
        # Create box surface with alpha
        box_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, self.box_color, box_surface.get_rect())
        pygame.draw.rect(box_surface, self.active_border_color if self.active else self.border_color, 
                        box_surface.get_rect(), 2)
        
        # Draw prompt
        prompt = self.font.render("Enter your name:", True, self.text_color)
        box_surface.blit(prompt, (self.padding, self.padding))
        
        # Draw name
        name_text = self.name
        if self.show_cursor:
            name_text += "│"
        name_surface = self.font.render(name_text, True, self.text_color)
        box_surface.blit(name_surface, (self.padding, self.padding + self.font.get_linesize() + 5))
        
        # Draw box on screen (using x_offset instead of centering)
        screen.blit(box_surface, (x_offset, self.pos_y))

class GenderSelect:
    def __init__(self, width, height, pos_y):
        # Input validation
        if width <= 0 or height <= 0:
            raise ValueError("GenderSelect width and height must be positive")
            
        self.width = width
        self.height = height
        self.pos_y = pos_y
        self.font = pygame.font.SysFont("georgia", 32)
        self.text_color = Colors.TEXT_PRIMARY
        self.box_color = (*Colors.BACKGROUND_BOTTOM, 200)
        self.border_color = Colors.BUTTON_NORMAL
        self.selected_color = Colors.BUTTON_HOVER
        self.padding = 20
        self.selected = "male"  # Only male for now

    def draw(self, screen, x_offset=50):  # Add x_offset parameter
        # Create box surface with alpha
        box_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, self.box_color, box_surface.get_rect())
        pygame.draw.rect(box_surface, self.border_color, box_surface.get_rect(), 2)
        
        # Draw prompt
        prompt = self.font.render("Select your gender:", True, self.text_color)
        box_surface.blit(prompt, (self.padding, self.padding))
        
        # Draw male option (only option for now)
        male_text = "♂ Male"
        male_surface = self.font.render(male_text, True, self.selected_color)
        box_surface.blit(male_surface, (self.padding, self.padding + self.font.get_linesize() + 5))
        
        # Draw box on screen (using x_offset instead of centering)
        screen.blit(box_surface, (x_offset, self.pos_y))

class IntroSequence:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.time = 0
        
        # Load and scale elder sprite
        try:
            self.elder_image = pygame.image.load("assets/sprites/elder.png").convert_alpha()
            # Scale elder to full screen height
            elder_height = screen_height
            elder_width = int(self.elder_image.get_width() * (elder_height / self.elder_image.get_height()))
            self.elder_image = pygame.transform.scale(self.elder_image, (elder_width, elder_height))
            # Position elder on right side of screen
            self.elder_x = screen_width - elder_width + 100  # Overlap slightly with screen edge
            self.elder_y = 0  # Start from top of screen
            logger.info("Elder sprite loaded successfully")
        except (pygame.error, FileNotFoundError) as e:
            logger.error(f"Failed to load elder sprite: {e}")
            # Create placeholder
            self.elder_image = pygame.Surface((200, screen_height))
            self.elder_image.fill((100, 80, 60))
            self.elder_x = screen_width - 200
            self.elder_y = 0
        
        # Elder animation
        self.elder_offset = 0
        self.elder_bob_speed = ELDER_BOB_SPEED
        
        # Create UI elements
        box_width = int(screen_width * 0.6)  # Narrower to fit with elder
        box_height = 200
        self.text_box = TextBox(box_width, box_height, screen_height - box_height - 50)
        self.name_input = NameInput(box_width, 150, screen_height // 2 - 75)
        self.gender_select = GenderSelect(box_width, 150, screen_height // 2 - 75)
        
        # Adjust UI positions to left side since elder is on right
        self.ui_x = 50  # Left margin
        
        # State management
        self.state = "intro"
        self.current_dialogue = 0
        self.dialogue_texts = [
            "In this harsh world, survival is a daily struggle. Resources are scarce, and communities must make difficult choices.",
            "Every month, we gather for Exile Day. One person must leave our village, chosen by vote, to preserve what little we have.",
            "Pokemon here are different. They bear scars of survival, both physical and emotional. Some lose limbs, others go blind, and many... don't survive.",
            "But those who endure... they develop something remarkable. Their wounds and trauma shape them, making them stronger, more resilient.",
            "We call this the Veteran System. It's not about experience points or levels. It's about survival, adaptation, and the will to continue.",
            "Now, young one, before you begin your journey in this unforgiving world, tell me about yourself..."
        ]
        
        # Background color
        self.bg_color_top = Colors.BACKGROUND_TOP
        self.bg_color_bottom = Colors.BACKGROUND_BOTTOM
        
        # Create optimized background
        self.background = GradientBackground(self.screen_width, self.screen_height, 
                                           self.bg_color_top, self.bg_color_bottom)
        
        # Fade effect
        self.fade_alpha = 0
        self.fading_in = True
        self.fade_speed = FADE_SPEED
        
        logger.info("Intro sequence initialized")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running = False
                return None
            
            if self.state == "intro":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if self.text_box.is_finished:
                        self.current_dialogue += 1
                        if self.current_dialogue < len(self.dialogue_texts):
                            self.text_box.start_text(self.dialogue_texts[self.current_dialogue])
                        else:
                            self.state = "name"
                            self.name_input.active = True
            
            elif self.state == "name":
                if self.name_input.handle_event(event):
                    self.state = "gender"
            
            elif self.state == "gender":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return {
                        "name": self.name_input.name,
                        "gender": self.gender_select.selected
                    }

    def update(self):
        dt = self.clock.tick(60) / 1000.0
        self.time += dt
        
        # Update fade effect
        if self.fading_in:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
            if self.fade_alpha <= 0:
                self.fading_in = False
        
        # Update elder animation
        self.elder_offset = math.sin(self.time * self.elder_bob_speed) * ELDER_BOB_AMPLITUDE
        
        # Update current state
        if self.state == "intro":
            if self.current_dialogue == 0 and not self.text_box.target_text:
                self.text_box.start_text(self.dialogue_texts[0])
            self.text_box.update()
        elif self.state == "name":
            self.name_input.update(self.time)

    def draw_background(self):
        """Draw pre-rendered gradient background for massive performance improvement"""
        self.background.draw(self.screen)

    def render(self):
        # Draw background
        self.draw_background()
        
        # Draw elder in intro state
        if self.state == "intro":
            # Apply gentle floating motion
            elder_pos = (self.elder_x, self.elder_y + self.elder_offset)
            self.screen.blit(self.elder_image, elder_pos)
            self.text_box.draw(self.screen, self.ui_x)
        elif self.state == "name":
            # Fade out elder for name input
            elder_alpha = 128
            faded_elder = self.elder_image.copy()
            faded_elder.set_alpha(elder_alpha)
            self.screen.blit(faded_elder, (self.elder_x, self.elder_y + self.elder_offset))
            self.name_input.draw(self.screen, self.ui_x)
        elif self.state == "gender":
            # Keep faded elder for gender selection
            elder_alpha = 128
            faded_elder = self.elder_image.copy()
            faded_elder.set_alpha(elder_alpha)
            self.screen.blit(faded_elder, (self.elder_x, self.elder_y + self.elder_offset))
            self.gender_select.draw(self.screen, self.ui_x)
        
        # Draw fade effect
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()

    def run(self):
        logger.info("Starting intro sequence...")
        while self.running:
            result = self.handle_events()
            if result is not None:
                logger.info(f"Intro complete - Player: {result.get('name', 'Unknown')}, Gender: {result.get('gender', 'Unknown')}")
                return result
            
            self.update()
            self.render()
        
        logger.info("Intro sequence cancelled")
        return None

if __name__ == "__main__":
    # This is just for testing the intro sequence directly
    pygame.init()
    intro = IntroSequence(1366, 768)
    result = intro.run()
    print("Player data:", result)
    pygame.quit()
    sys.exit()

