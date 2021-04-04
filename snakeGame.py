import pygame
import random
from spritesheet import SpriteSheet
import sys


class SnakeGame:
    def __init__(self, width, height, rows, columns, speed=1):  # default speed 1, higher = faster
        # initialize pygame
        pygame.init()

        # change title of the window
        pygame.display.set_caption("Snake Game")

        # WIDTH and HEIGHT of the main game window
        self.WIDTH = width
        self.HEIGHT = height

        # The grid for the snake
        self.ROWS = rows
        self.COLUMNS = columns

        # Width/height of a cell in the grid (for convenience)
        self.CELL_WIDTH = self.WIDTH // self.COLUMNS
        self.CELL_HEIGHT = self.HEIGHT // self.ROWS

        # The snake (a list of tuples (coordinates and direction))
        head = (random.randint(0, columns - 3), random.randint(0, rows - 1), pygame.K_RIGHT)
        self.snake = [head, (head[0] + 1, head[1], head[2]), (head[0] + 2, head[1], head[2])]

        # How fast is the snake (DEFAULT = 1)
        self.SPEED = speed
        self.CLOCK = pygame.time.Clock()

        # Snake direction
        self.direction = pygame.K_RIGHT

        # The food
        self.food = self.random_food()
        self.food_eaten = False

        # The main game window
        self.WINDOW = pygame.display.set_mode((width, height))

        # Game sprites
        game_sprites = SpriteSheet("snakeSprite.png")

        self.bg = pygame.transform.scale(pygame.image.load("bg.jpeg"), (self.WIDTH, self.HEIGHT))

        self.snake_head_sprite = {pygame.K_UP: pygame.transform.scale(game_sprites.image_at((3 * 64, 0 * 64, 64, 64)),
                                                                      (self.CELL_WIDTH, self.CELL_HEIGHT)),  # UP
                                  pygame.K_DOWN: pygame.transform.scale(game_sprites.image_at((4 * 64, 1 * 64, 64, 64)),
                                                                        (self.CELL_WIDTH, self.CELL_HEIGHT)),  # DOWN
                                  pygame.K_LEFT: pygame.transform.scale(game_sprites.image_at((3 * 64, 1 * 64, 64, 64)),
                                                                        (self.CELL_WIDTH, self.CELL_HEIGHT)),  # LEFT
                                  pygame.K_RIGHT: pygame.transform.scale(
                                      game_sprites.image_at((4 * 64, 0 * 64, 64, 64)),
                                      (self.CELL_WIDTH, self.CELL_HEIGHT))}  # RIGHT

        self.snake_tail_sprite = {pygame.K_UP: pygame.transform.scale(game_sprites.image_at((3 * 64, 2 * 64, 64, 64)),
                                                                      (self.CELL_WIDTH, self.CELL_HEIGHT)),  # UP
                                  pygame.K_DOWN: pygame.transform.scale(game_sprites.image_at((4 * 64, 3 * 64, 64, 64)),
                                                                        (self.CELL_WIDTH, self.CELL_HEIGHT)),  # DOWN
                                  pygame.K_LEFT: pygame.transform.scale(game_sprites.image_at((3 * 64, 3 * 64, 64, 64)),
                                                                        (self.CELL_WIDTH, self.CELL_HEIGHT)),  # LEFT
                                  pygame.K_RIGHT: pygame.transform.scale(
                                      game_sprites.image_at((4 * 64, 2 * 64, 64, 64)),
                                      (self.CELL_WIDTH, self.CELL_HEIGHT))}  # RIGHT
        self.snake_body_straight = (
        pygame.transform.scale(game_sprites.image_at((1 * 64, 0 * 64, 64, 64)), (self.CELL_WIDTH, self.CELL_HEIGHT)),
        # HORIZONTAL
        pygame.transform.scale(game_sprites.image_at((2 * 64, 1 * 64, 64, 64)),
                               (self.CELL_WIDTH, self.CELL_HEIGHT)))  # VERTICAL
        self.snake_body_curved = (
        pygame.transform.scale(game_sprites.image_at((0 * 64, 0 * 64, 64, 64)), (self.CELL_WIDTH, self.CELL_HEIGHT)),
        # UP-RIGHT / LEFT-DOWN
        pygame.transform.scale(game_sprites.image_at((2 * 64, 0 * 64, 64, 64)), (self.CELL_WIDTH, self.CELL_HEIGHT)),
        # UP-LEFT / RIGHT-DOWN
        pygame.transform.scale(game_sprites.image_at((2 * 64, 2 * 64, 64, 64)), (self.CELL_WIDTH, self.CELL_HEIGHT)),
        # DOWN-LEFT / RIGHT-UP
        pygame.transform.scale(game_sprites.image_at((0 * 64, 1 * 64, 64, 64)),
                               (self.CELL_WIDTH, self.CELL_HEIGHT)))  # DOWN-RIGHT / LEFT-UP

        self.food_sprite = pygame.transform.scale(game_sprites.image_at((0 * 64, 3 * 64, 64, 64)),
                                                  (self.CELL_WIDTH, self.CELL_HEIGHT))

        # Game status
        self.GAME_START = False
        self.GAME_OVER = False

    def draw_game(self):
        # drawing the background
        self.WINDOW.blit(self.bg, (0, 0))

        # drawing the snake
        # draw body first
        for i in range(len(self.snake) - 1):
            if i == 0:
                # draw tail
                sprite = self.snake_tail_sprite[self.snake[1 + self.food_eaten][-1]]
                position = (self.snake[0][0] * self.CELL_WIDTH, self.snake[0][1] * self.CELL_HEIGHT)

                self.WINDOW.blit(sprite, position)
            else:
                if self.food_eaten:  # this is to avoid tail and body drawing overlap
                    self.food_eaten = False
                    continue

                if self.snake[i][-1] == self.snake[i + 1][-1]:  # if straight-body
                    if self.snake[i][-1] == pygame.K_UP or self.snake[i][-1] == pygame.K_DOWN:  # vertical
                        sprite = self.snake_body_straight[1]
                    else:  # horizontal
                        sprite = self.snake_body_straight[0]
                    position = (self.snake[i][0] * self.CELL_WIDTH, self.snake[i][1] * self.CELL_HEIGHT)
                else:  # if curved-body
                    if list((self.snake[i][-1], self.snake[i + 1][-1])) == list((pygame.K_UP, pygame.K_RIGHT)) or \
                            list((self.snake[i][-1], self.snake[i + 1][-1])) == list(
                        (pygame.K_LEFT, pygame.K_DOWN)):  # UP-RIGHT / LEFT-DOWN
                        sprite = self.snake_body_curved[0]
                    elif list((self.snake[i][-1], self.snake[i + 1][-1])) == list((pygame.K_UP, pygame.K_LEFT)) or \
                            list((self.snake[i][-1], self.snake[i + 1][-1])) == list(
                        (pygame.K_RIGHT, pygame.K_DOWN)):  # UP-LEFT / RIGHT-DOWN
                        sprite = self.snake_body_curved[1]
                    elif list((self.snake[i][-1], self.snake[i + 1][-1])) == list((pygame.K_DOWN, pygame.K_LEFT)) or \
                            list((self.snake[i][-1], self.snake[i + 1][-1])) == list(
                        (pygame.K_RIGHT, pygame.K_UP)):  # DOWN-LEFT / RIGHT-UP
                        sprite = self.snake_body_curved[2]
                    elif list((self.snake[i][-1], self.snake[i + 1][-1])) == list((pygame.K_DOWN, pygame.K_RIGHT)) or \
                            list((self.snake[i][-1], self.snake[i + 1][-1])) == list(
                        (pygame.K_LEFT, pygame.K_UP)):  # DOWN-RIGHT / LEFT-UP
                        sprite = self.snake_body_curved[3]
                    position = (self.snake[i][0] * self.CELL_WIDTH, self.snake[i][1] * self.CELL_HEIGHT)
                self.WINDOW.blit(sprite, position)

        # draw head
        sprite = self.snake_head_sprite[self.snake[-1][-1]]
        position = (self.snake[-1][:-1][0] * self.CELL_WIDTH, self.snake[-1][:-1][1] * self.CELL_HEIGHT)

        self.WINDOW.blit(sprite, position)

        # drawing the food
        self.WINDOW.blit(self.food_sprite, (self.food[0] * self.CELL_WIDTH, self.food[1] * self.CELL_HEIGHT))

        # updates the drawn contents to the screen
        pygame.display.update()

    def random_food(self):
        # this is to avoid food spawning on top of the snake
        food = (random.randint(0, self.COLUMNS - 1), random.randint(0, self.ROWS - 1))
        while food in [x[:-1] for x in self.snake[:-1]]:
            food = (random.randint(0, self.COLUMNS - 1), random.randint(0, self.ROWS - 1))
        return food

    def move_snake(self):
        # 1. get a copy of head of the snake (the last element of snake list)
        # 2. move the copy +1 cell to the current direction
        # 3. append the copy to the snake list
        # This will give an illusion of movement

        tail = self.snake[-1]
        col = tail[0]
        row = tail[1]
        if self.direction == pygame.K_UP:  # UP
            row -= 1
        elif self.direction == pygame.K_DOWN:  # DOWN
            row += 1
        elif self.direction == pygame.K_LEFT:  # LEFT
            col -= 1
        elif self.direction == pygame.K_RIGHT:  # RIGHT
            col += 1
        moved_tail = (col, row, self.direction)
        self.snake.pop(0)
        self.snake.append(moved_tail)

    def check_food_eaten(self):
        if self.snake[-1][:-1] == self.food:
            # add food on top of tail
            self.snake.insert(0, self.snake[0])
            self.food = self.random_food()
            self.food_eaten = True

    def check_death(self):
        if self.snake[-1][:-1] in [x[:-1] for x in self.snake[:-1]]:  # check if snake hit its own body
            print(self.snake[:-1])
            self.GAME_OVER = True
        elif self.snake[-1][0] > self.COLUMNS - 1 or \
                self.snake[-1][1] > self.ROWS - 1 or \
                self.snake[-1][0] < 0 or \
                self.snake[-1][1] < 0:  # check if snake is out of game bounds
            print(self.snake[:-1])
            self.GAME_OVER = True
        return self.GAME_OVER

    def start(self):
        # draw the game initial state
        self.draw_game()

        # the main game loop
        while not self.GAME_OVER:
            # delay
            self.CLOCK.tick(10 + self.SPEED * 2)

            # loops over all the events done by the user (such as keypresses, mouseclicks, etc...)
            for event in pygame.event.get():

                # checks if Exit button is pressed
                if event.type == pygame.QUIT:
                    sys.exit()

                # checks if any of the A, W, S, and D keys is pressed, game starts
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != pygame.K_DOWN:  # UP
                        self.direction = pygame.K_UP
                    elif event.key == pygame.K_DOWN and self.direction != pygame.K_UP:  # DOWN
                        self.direction = pygame.K_DOWN
                    elif event.key == pygame.K_LEFT and self.direction != pygame.K_RIGHT:  # LEFT
                        self.direction = pygame.K_LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != pygame.K_LEFT:  # RIGHT
                        self.direction = pygame.K_RIGHT
                    else:
                        break
                    self.GAME_START = True
                    break

            if self.GAME_START:
                # move the snake
                self.move_snake()

                # check if food eaten
                self.check_food_eaten()

                # check if dead
                if self.check_death():
                    continue

                # redraw the game
                self.draw_game()

        # Game over screen
        # text
        gameover_font = pygame.font.SysFont('Comic Sans MS', int(self.WIDTH * (1 / 6)))
        options_font = pygame.font.SysFont('Comic Sans MS', int(self.WIDTH * (1 / 24)))

        gameover_text = gameover_font.render('Game Over!', False, (255, 255, 255))

        option1_text = options_font.render('Press ENTER to play again', False, (255, 255, 255))
        option2_text = options_font.render('Press ESC to quit', False, (255, 255, 255))

        # drawing text to screen
        self.WINDOW.blit(gameover_text, (
        (self.WIDTH - gameover_text.get_rect().width) // 2, (self.HEIGHT - gameover_text.get_rect().height) // 4))

        self.WINDOW.blit(option1_text, (
        (self.WIDTH - option1_text.get_rect().width) // 2, self.HEIGHT - gameover_text.get_rect().height))
        self.WINDOW.blit(option2_text, ((self.WIDTH - option2_text.get_rect().width) // 2,
                                        self.HEIGHT - gameover_text.get_rect().height + option1_text.get_rect().height))

        # update the drawn text to screen
        pygame.display.update()

        # wait for user choice
        while True:
            for event in pygame.event.get():
                # checks if Exit button is pressed
                if event.type == pygame.QUIT:
                    sys.exit()

                # checks if any of the A, W, S, and D keys is pressed, game starts
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Quit
                        return True
                    elif event.key == pygame.K_RETURN:  # Play again
                        return False


if __name__ == '__main__':
    while True:
        snake_game = SnakeGame(600, 600, 25, 25)
        if snake_game.start():
            break
