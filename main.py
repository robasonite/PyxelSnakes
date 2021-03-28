import pyxel
import enum
import time
import random
import collections
    
# Calculate starting X value for centered text.
def center_text(text, page_width, char_width = pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return (page_width - text_width) / 2

# The same thing, but for the Y position.
def virtical_center_text(text, page_height, char_height = pyxel.FONT_HEIGHT):
    return (page_height / 2) - (char_height / 2)

# Calculate starting X value for right-aligned text.
def right_text(text, page_width, char_width = pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return page_width - (text_width + char_width)


# Check if 2 objects are overlapping
def intersects(objA, objB):
    is_intersected = False
    if (
        objB.x + objB.w > objA.x and
        objA.x + objA.w > objB.x and
        objB.y + objB.h > objA.y and
        objA.y + objA.h > objB.y
        ):
        is_intersected = True

    return is_intersected
        


# Snake direction labels
class Direction(enum.Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

# Game state labels
class GameState(enum.Enum):
    RUNNING = 0
    GAME_OVER = 1
    PAUSED = 2


# Level class for drawing walls.
class Level():
    def __init__(self, w, h):
        self.tm = 0
        self.x = 0
        self.y = 0
        self.w = w / 8
        self.h = h / 8

    def draw(self):
        pyxel.bltm(0, 0, self.tm, self.x, self.y, self.w, self.h)


class SnakeSection():
    def __init__(self, x, y, isHead=False):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.isHead = isHead

    def draw(self, direction):
        width = self.w
        height = self.h
        sprite_x = 0
        sprite_y = 0

        # If head section, change and flip the sprite depending on direction.
        if self.isHead:
            if direction == Direction.RIGHT:
                sprite_x = 8
                sprite_y = 0
            if direction == Direction.LEFT:
                sprite_x = 8
                sprite_y = 0
                width = width * -1
            if direction == Direction.DOWN:
                sprite_x = 0
                sprite_y = 8
            if direction == Direction.UP:
                sprite_x = 0
                sprite_y = 8
                height = height * -1

        pyxel.blt(self.x, self.y, 0, sprite_x, sprite_y, width, height)


# Responsible for drawing scores and other UI stuff
class Hud:
    def __init__(self, w, h):
        self.w = w
        self.h = h

        # The title text is centered.
        self.title_text = "Nibbles"
        self.title_text_x = center_text(self.title_text, self.w)

        # The score text is on the right side.
        self.score_text = str(0)
        self.score_text_x = right_text(self.score_text, self.w)

        # The level text is on the left side.
        self.level_text = "Level 0"
        self.level_text_x = 10

        # The apples text is right next to the level text.
        self.apples_text = "Apples "
        self.apples_text_x = len(self.level_text) * pyxel.FONT_WIDTH + self.level_text_x + 5

        # Paused label.
        self.pause_text = "PAUSED"
        self.pause_text_x = center_text(self.pause_text, self.w)
        self.pause_text_y = virtical_center_text(self.pause_text, self.h)

    def draw_title(self):
        # Draw a rectangle behind the title text.
        # Arguments:
        # - X
        # - Y
        # - Width
        # - Height
        # - Color (ID of the current palete)
        pyxel.rect(self.title_text_x - 1, 0, len(self.title_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)

        # Draw the title text.
        # Arguments:
        # - X
        # - Y
        # - Text
        # - Color
        pyxel.text(self.title_text_x, 1, self.title_text, 12)

    def draw_score(self, score):
        self.score_text = str(score)
        self.score_text_x = right_text(self.score_text, self.w)
        pyxel.rect(self.score_text_x - 1, 0, len(self.score_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.score_text_x, 0, self.score_text, 3)

    def draw_level(self, level):
        self.level_text = "Level " + str(level)
        pyxel.rect(self.level_text_x - 1, 0, len(self.level_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.level_text_x, 0, self.level_text, 3)

    def draw_apples(self, apples):
        self.apples_text = "Apples " + str(apples)
        pyxel.rect(self.apples_text_x - 1, 0, len(self.apples_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.apples_text_x, 0, self.apples_text, 8)

    def draw_paused(self):
        pyxel.rect(self.pause_text_x - 1, self.pause_text_y - 1, len(self.pause_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.pause_text_x, self.pause_text_y, self.pause_text, 7)



# Make an apple for the snake to eat.
# Handles drawing and moving the apple, anything on the apple (snake eats it).
class Apple:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 0, self.w, self.h)

    # NOTE: This function was moved to the global scope because of its utility.
    # It made absolutely NO SENSE to attach such an important function to a
    # fucking CLASS. 
    # Check for a collision with another object.
#    def intersects(self, u, v, w, h):
#        is_intersected = False
#        if (
#            u + w > self.x and
#            self.x + self.w > u and
#            v + h > self.y and
#            self.y + self.h > v
#            ):
#            is_intersected = True
#
#        return is_intersected

    def move(self, x, y):
        self.x = x
        self.y = y


class App:
    def __init__(self):
        # First two arguments are the width and height
        self.screenWidth = 160
        self.screenHeight = 120

        # Initialize the Pyxel
        pyxel.init(self.screenWidth,self.screenHeight, scale=6, caption="Nibbles", fps=60)

        # Load the main spritesheet.
        pyxel.load("assets/resources.pyxres")

        # Whether or not we want music.
        self.play_music = True

        # Game state.
        #self.game_state = GameState.RUNNING

        # Create the snake and its sections.
        self.snake = []

        ##########################################
        # REDUNDANT CODE
        # start_new_game function is used instead.
        ##########################################
        #self.snake.append(SnakeSection(32, 32, isHead=True))
        #self.snake.append(SnakeSection(24, 32))
        #self.snake.append(SnakeSection(16, 32))
        #self.snake_direction = Direction.RIGHT
        #self.sections_to_add = 0
        
        # Create an apple object.
        #self.apple = Apple(64, 32)
        #self.move_apple()


        # Time tracking
        #self.speed = 1.5
        #self.time_last_frame = time.time()
        #self.dt = 0
        #self.time_since_last_move = 0
       
        # Input queing
        # Store direction changes so that the player can chain them.
        self.input_que = collections.deque()

        self.start_new_game()

        # Run the game.
        pyxel.run(self.update, self.draw)


    def start_new_game(self):
        
        # Score, apples, and level
        self.score = 0
        self.apples_eaten = 0
        self.current_level = 1

        # Instantiate this to draw the walls.
        self.level = Level(self.screenWidth, self.screenHeight)

        # Hud elements
        self.hud = Hud(self.screenWidth, self.screenHeight)

        # Clear and rebuild the snake.
        self.snake.clear()
        self.game_state = GameState.RUNNING
        self.snake.append(SnakeSection(32, 32, isHead=True))
        self.snake.append(SnakeSection(24, 32))
        self.snake.append(SnakeSection(16, 32))
        self.snake_direction = Direction.RIGHT
        self.sections_to_add = 0

        # Make a new apple.
        self.apple = Apple(64, 32)
        self.move_apple()

        # Reset time tracking.
        self.speed = 1.5
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_last_move = 0

        # Reset the input que
        self.input_que.clear()

        # Check if we want music.
        # If so, play it.
        if self.play_music:
            pyxel.playm(0, loop=True)

        # Restart the game.
        self.game_state = GameState.RUNNING



    def update(self):
        # Update delta time.
        # This is required to keep the snake from flying off the screen immediately.
        time_this_frame = time.time()
        self.dt = time_this_frame - self.time_last_frame
        self.time_last_frame = time_this_frame
        self.time_since_last_move += self.dt

        # Input
        self.check_input()
        
        if self.game_state == GameState.RUNNING:
            # Move the snake and check for collisions.
            if self.time_since_last_move >= 1 / self.speed:
                self.time_since_last_move = 0

                # Move the snake.
                self.move_snake()

                # Check for collisions.
                self.check_collisions()

                # Increase score:
                self.score += len(self.snake) * self.apples_eaten + 1



    def toggle_music(self):
        if self.play_music:
            # Stop playing all sounds on all channels.
            pyxel.stop()
            self.play_music = False

        else:
            pyxel.playm(0, loop=True)
            self.play_music = True
   

    def toggle_paused(self):
        # Avoid pausing if the state is GAME_OVER
        if self.game_state != GameState.GAME_OVER:
            if self.game_state == GameState.RUNNING:
                self.game_state = GameState.PAUSED

            else:
                self.game_state = GameState.RUNNING



    def draw(self):

        # Clear the screen.
        pyxel.cls(0)

        # Draw the level walls.
        self.level.draw()

        # Draw the apple.
        self.apple.draw()

        for s in self.snake:
            s.draw(self.snake_direction)

        # Draw the hud elements.
        #pyxel.text(10, 10, str(self.game_state), 12)
        #self.hud.draw_title()
        self.hud.draw_score(self.score)
        self.hud.draw_level(self.current_level)
        self.hud.draw_apples(self.apples_eaten)

        # Handle pausing.
        if self.game_state == GameState.PAUSED:
            self.hud.draw_paused()



    def check_collisions(self):
        # Apple
        #if self.apple.intersects(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
        if intersects(self.apple, self.snake[0]):
            self.speed += (self.speed * 0.1)
            self.sections_to_add += 4

            # Move the apple to another location.
            self.move_apple()

            # Increment the apple counter.
            self.apples_eaten += 1

            # Play a sound effect.
            # Sound track 0 on Channel 3.
            pyxel.play(3, 0)

        # Snake crashing in itself.
        for s in self.snake:
            # Ignore the head section
            if s == self.snake[0]:
                continue

            else:
                if intersects(s, self.snake[0]):
                    # End the game.
                    self.game_state = GameState.GAME_OVER

                    # Stop all sound.
                    pyxel.stop()

                    # Play the crash sound.
                    pyxel.play(3, 1)

        
        # Check for collisions with the wall.
        # The tilemap function deals in terms of units of 8 according to the 
        # YouTuber.
        #
        # tilemap(0) refers to the first "tilemap image".
        # tilemap().get retrieves data from a tilemap at X, Y.
        # The YouTube mentioned that this returned the "sprite ID" at X, Y.
        # Neither the YouTuber CaffeinatedTech nor the official Pyxel
        # documentation explain why '== 3' works, but no other number works.
        #print(pyxel.tilemap(0).get(self.snake[0].x / 8, self.snake[0].y / 8))
        
        # Furthermore, when the result is printed, 3 and 4 are the only numbers
        # the expression produces. 3 is produced whenever the head of the
        # snake overlaps with a wall. Otherwise 4 is produced.
        #
        # The only corelation I found is that 3 happens to be the X position of
        # the wall tile I drew with 'pyxeleditor', divided by 8. Beyond that,
        # this doesn't make sense.
        if pyxel.tilemap(0).get(self.snake[0].x / 8, self.snake[0].y / 8) == 3:
            self.game_state = GameState.GAME_OVER
            pyxel.stop()
            pyxel.play(3, 1)



    def move_apple(self):
        # Select a new random location for the apple. It should NOT be offscreen
        # or inside the snake.
        good_position = False
        while not good_position:
            new_x = random.randrange(8, self.screenWidth - 8, 8)
            new_y = random.randrange(8, self.screenHeight - 8, 8)
            good_position = True

            # Check the snake position
            class Throwaway:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
                    self.w = 8
                    self.h = 8

            new_location = Throwaway(new_x, new_y)
            for s in self.snake:
                if intersects(s, new_location):
                    good_position = False
                    break

            # Wall check


            if good_position:
                self.apple.move(new_x, new_y)


    def move_snake(self):
        # Check for change in direction.
        if len(self.input_que) > 0:
            # Remove the first item from the que and use it's value.
            self.snake_direction = self.input_que.popleft()


        # Grow the snake if necessary.
        if self.sections_to_add > 0:
            s = self.snake[-1]
            self.snake.append(SnakeSection(s.x, s.y))
            self.sections_to_add -= 1

        # Move the head first.
        previous_location_x = self.snake[0].x
        previous_location_y = self.snake[0].y

        if self.snake_direction == Direction.RIGHT:
            self.snake[0].x += self.snake[0].w

        if self.snake_direction == Direction.LEFT:
            self.snake[0].x -= self.snake[0].w

        if self.snake_direction == Direction.UP:
            self.snake[0].y -= self.snake[0].h

        if self.snake_direction == Direction.DOWN:
            self.snake[0].y += self.snake[0].h

        # Move the tail.
        for s in self.snake:

            # Don't move the head twice.
            if s == self.snake[0]:
                continue

            # Move section to where the previous one was.
            current_location_x = s.x
            current_location_y = s.y
            s.x = previous_location_x
            s.y = previous_location_y

            # Update previous location for next section.
            previous_location_x = current_location_x
            previous_location_y = current_location_y


    def check_input(self):
        # Allow the music to be switched on and off.
        # NOTE: Discovered that 'btnr' for tracking button RELEASE works
        # better.
        if pyxel.btnr(pyxel.KEY_M):
            self.toggle_music()

        # Allow the game to be paused.
        if pyxel.btnr(pyxel.KEY_P):
            self.toggle_paused()

        # Allow the game to be restarted.
        if self.game_state == GameState.GAME_OVER:
            if pyxel.btn(pyxel.KEY_ENTER):
                self.start_new_game()



        ############
        # MOVEMENT
        ############
        # If the que has no inputs, check against the snake direction.
        if len(self.input_que) == 0:
            #checkAgainst = self.snake_direction
            checkQue = False

        # If the que DOES have inputs, both the last input and the current direction must be checked.
        else:
            checkQue = True 

        if pyxel.btn(pyxel.KEY_RIGHT):

            # These checks prevent the snake from immediately crashing into itself.
            if self.snake_direction != Direction.LEFT and self.snake_direction != Direction.RIGHT:
                if checkQue:
                    if self.input_que[-1] != Direction.LEFT and self.input_que[-1] != Direction.RIGHT:
                        self.input_que.append(Direction.RIGHT)
                else:
                    self.input_que.append(Direction.RIGHT)
        
        elif pyxel.btn(pyxel.KEY_LEFT):
            if self.snake_direction != Direction.RIGHT and self.snake_direction != Direction.LEFT:
                if checkQue:
                    if self.input_que[-1] != Direction.RIGHT and self.input_que[-1] != Direction.LEFT:
                        self.input_que.append(Direction.LEFT)
                else:
                    self.input_que.append(Direction.LEFT)

        elif pyxel.btn(pyxel.KEY_UP):
            if self.snake_direction != Direction.DOWN and self.snake_direction != Direction.UP:
                if checkQue:
                    if self.input_que[-1] != Direction.DOWN and self.input_que[-1] != Direction.UP:
                        self.input_que.append(Direction.UP)
                else:
                    self.input_que.append(Direction.UP)
        
        elif pyxel.btn(pyxel.KEY_DOWN):
            if self.snake_direction != Direction.UP and self.snake_direction != Direction.DOWN:
                if checkQue:
                    if self.input_que[-1] != Direction.UP and self.input_que[-1] != Direction.DOWN:
                        self.input_que.append(Direction.DOWN)
                else:
                    self.input_que.append(Direction.DOWN)



if __name__ == '__main__':
    App()
