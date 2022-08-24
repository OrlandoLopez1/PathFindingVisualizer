import pygame
from collections import deque
import time
import random
import heapdict
import sys

pygame.init()  # very important
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
POSITIVE_COST = (255, 252, 190)
NEGATIVE_COST = (199, 255, 254)
INFINITE = float('inf')


class Board:

    def __init__(self, window, rows, cols, width, height):
        self.FONT = pygame.font.SysFont('arial', 21)
        self.BIGFONT = pygame.font.SysFont('arial', 42)
        self.A_FONT_U = pygame.font.SysFont('arial', 40)
        self.A_FONT_U.set_underline(True)
        self.A_FONT = pygame.font.SysFont('arial', 40)
        self.TILE_SELECT_FONT = pygame.font.SysFont('arial', 16)
        self.SPEED_FONT = pygame.font.SysFont('arial', 20)
        self.SPEED_FONT_U = pygame.font.SysFont('arial', 20)
        self.SPEED_FONT_U.set_underline(True)
        self.window = window
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.board = [[Tile() for j in range(cols)] for i in range(rows)]
        self.drag = False
        self.speed_setting = 1
        self.cancel_visual = False
        self.scale_x = window.get_width() / width
        self.scale_y = window.get_height() / height
        self.current_tile_type = "start"
        self.tile_options = [pygame.image.load("Assets/Start_Tile.png"), pygame.image.load("Assets/Start_Tile.png"),
                             pygame.image.load("Assets/End_Tile.png"), pygame.image.load("Assets/Empty_Tile.png"),
                             pygame.image.load("Assets/Positive_Cost_Tile.png"),
                             pygame.image.load("Assets/Inaccessible.png")]

        self.tile_options_rects = [None] * 6
        self.learn_btn = None
        self.start_tile = None
        self.end_tile = None
        self.waiting = False
        self.current_weight = ""
        self.current_weight_text = self.BIGFONT.render(self.current_weight, True, (0, 0, 0), None)
        self.current_algorithm = self.A_FONT_U.render("Pick an algorithm!", True, (0, 0, 0), None)
        self.current_algorithm_str = "Select an Algorithm"
        self.current_algorithm_num = 0
        x_pos = self.width * 0.190 * self.scale_x
        y_pos = self.height * 0.725 * self.scale_y
        self.current_algorithm_rect = self.current_algorithm.get_rect(topleft=(x_pos, y_pos))

        left = 1250 * self.scale_x
        top = (self.height * 0.15 * self.scale_y)
        self.shortcuts = pygame.image.load("Assets/Shortcuts.png")
        self.shortcuts_rect = self.shortcuts.get_rect(topleft=(left, top))

        left = 900 * self.scale_x
        top = (self.height * 0.15 * self.scale_y)
        self.algorithm_text = self.A_FONT_U.render("     ALGORITHMS     ", True, (0, 0, 0), None)
        self.algorithm_text_rect = self.algorithm_text.get_rect(topleft=(left, top))

        self.BFS_btn = self.A_FONT.render(" Breadth First Search ", True, (0, 0, 0), None)
        self.BFS_btn_rect = self.BFS_btn.get_rect(topleft=(left, top + 45 * self.scale_y))

        self.DFS_btn = self.A_FONT.render(" Depth First Search ", True, (0, 0, 0), None)
        self.DFS_btn_rect = self.DFS_btn.get_rect(topleft=(left, top + 90 * self.scale_y))

        self.dijkstra_btn = self.A_FONT.render(" Dijkstra's Algorithm", True, (0, 0, 0), None)
        self.dijkstra_btn_rect = self.dijkstra_btn.get_rect(topleft=(left, top + 135 * self.scale_y))

        self.A_star_btn = self.A_FONT.render(" A* Search", True, (0, 0, 0), None)
        self.A_star_btn_rect = self.A_star_btn.get_rect(topleft=(left, top + 180 * self.scale_y))

        #  = 900 * self.scale_x
        # = (self.height * 0.50 * self.scale_y)
        left = (self.width * .425 * self.scale_x)
        top = (self.height * 0.02 * self.scale_y)
        self.speed_text = self.SPEED_FONT_U.render("    Speed    ", True, (0, 0, 0), None)
        self.speed_text_rect = self.speed_text.get_rect(topleft=(left, top))

        self.high_btn = self.SPEED_FONT.render(" High* ", True, (0, 0, 0), None)
        self.high_btn_rect = self.high_btn.get_rect(topleft=(left, top + 25 * self.scale_y))

        self.medium_btn = self.SPEED_FONT.render(" Medium ", True, (0, 0, 0), None)
        self.medium_btn_rect = self.medium_btn.get_rect(topleft=(left, top + 50 * self.scale_y))

        self.slow_btn = self.SPEED_FONT.render(" Slow ", True, (0, 0, 0), None)
        self.slow_btn_rect = self.slow_btn.get_rect(topleft=(left, top + 75 * self.scale_y))

    def initialize_board(self):
        # board[row][col]
        # TL corner
        self.board[0][0].right = self.board[0][1]
        self.board[0][0].down = self.board[1][0]
        self.board[0][0].left = None
        self.board[0][0].up = None
        # TR corner
        self.board[0][self.cols - 1].left = self.board[0][self.cols - 2]
        self.board[0][self.cols - 1].down = self.board[1][self.cols - 1]
        self.board[0][self.cols - 1].right = None
        self.board[0][self.cols - 1].up = None
        # BL corner
        self.board[self.rows - 1][0].right = self.board[self.rows - 1][1]
        self.board[self.rows - 1][0].up = self.board[self.rows - 2][0]
        self.board[self.rows - 1][0].left = None
        self.board[self.rows - 1][0].down = None
        # BR corner
        self.board[self.rows - 1][self.cols - 1].left = self.board[self.rows - 1][self.cols - 2]
        self.board[self.rows - 1][self.cols - 1].up = self.board[self.rows - 2][self.cols - 1]
        self.board[self.rows - 1][self.cols - 1].right = None
        self.board[self.rows - 1][self.cols - 1].down = None
        # LEFT side
        for i in range(1, self.rows - 1):
            self.board[i][0].right = self.board[i][1]
            self.board[i][0].up = self.board[i - 1][0]
            self.board[i][0].down = self.board[i + 1][0]
            self.board[i][0].left = None

        # RIGHT side
        for i in range(1, self.rows - 1):
            self.board[i][self.cols - 1].left = self.board[i][self.cols - 2]  # changed from right to left
            self.board[i][self.cols - 1].up = self.board[i - 1][self.cols - 1]
            self.board[i][self.cols - 1].down = self.board[i + 1][self.cols - 1]
            self.board[i][self.cols - 1].right = None
        # TOP side
        for i in range(1, self.cols - 1):
            self.board[0][i].left = self.board[0][i - 1]
            self.board[0][i].right = self.board[0][i + 1]
            self.board[0][i].down = self.board[1][i]
            self.board[0][i].up = None
        # BOTTOM side
        for i in range(1, self.cols - 1):
            self.board[self.rows - 1][i].left = self.board[self.rows - 1][i - 1]
            self.board[self.rows - 1][i].right = self.board[self.rows - 1][i + 1]
            self.board[self.rows - 1][i].up = self.board[self.rows - 2][i]
            self.board[self.rows - 1][i].down = None
        # MIDDLE
        for i in range(1, self.rows - 1):
            for j in range(1, self.cols - 1):
                self.board[i][j].left = self.board[i][j - 1]
                self.board[i][j].right = self.board[i][j + 1]
                self.board[i][j].up = self.board[i - 1][j]
                self.board[i][j].down = self.board[i + 1][j]

        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j].pos = (i, j)
    def fix_screen_after_resizing(self):

        pass

    def draw_board(self):
        # changes size of grid tiles
        factor1 = 0.75
        # changes size of the bar above the grid
        factor2 = 1.5

        self.window.fill(GRAY)
        self.scale_x = self.window.get_width() / self.width
        self.scale_y = self.window.get_height() / self.height
        # screen = pygame.display.set_mode()
        """
        Might be faster if conditional checks for changes in screensize before scaling
        """

        # Tile customization bar
        for i in range(len(self.tile_options)):
            if i == 0:
                x_pos = ((self.width * 0.125 * self.scale_x) + (32 * self.scale_x - 64)) * factor2
                y_pos = (self.height * 0.05 * self.scale_y)
            else:
                x_pos = ((self.width * 0.125 * self.scale_x) + (32 * self.scale_x * i)) * factor2
                y_pos = (self.height * 0.05 * self.scale_y)
            self.tile_options[i] = pygame.transform.scale(self.tile_options[i],
                                                          (32 * self.scale_x * factor2, 32 * self.scale_y * factor2))
            self.tile_options_rects[i] = self.tile_options[i].get_rect(topleft=(x_pos, y_pos))

            self.window.blit(self.tile_options[i], (x_pos, y_pos))
            if i == 0 and self.current_tile_type == "positive_cost":
                self.window.blit(self.current_weight_text, (x_pos + 5, y_pos - 1))
        # Board tiles might want to load images initially during initialize board function
        for i in range(self.rows):  # todo might be able to optimize
            for j in range(self.cols):
                x_pos = (self.width * 0.05 * self.scale_x) + (32 * self.scale_x * j * factor1)
                y_pos = (self.height * 0.15 * self.scale_y) + (32 * self.scale_y * i * factor1)
                self.board[i][j].image = pygame.transform.scale(self.board[i][j].image,
                                                                (32 * self.scale_x * factor1,
                                                                 32 * self.scale_y * factor1))
                self.board[i][j].image_rect = self.board[i][j].image.get_rect(topleft=(x_pos, y_pos))
                self.window.blit(self.board[i][j].image, (x_pos, y_pos))
                # font = pygame.font.SysFont('arial', 12)
                # text = font.render("88", True, (0, 0, 0), None)
                if self.board[i][j].weight != 0:
                    self.window.blit(self.board[i][j].text, (x_pos + 3, y_pos - 1))  # 10

    def draw_screen(self):  # todo optimize later

        self.window.blit(self.shortcuts, self.shortcuts_rect)
        self.window.blit(self.algorithm_text, self.algorithm_text_rect)
        self.window.blit(self.BFS_btn, self.BFS_btn_rect)
        self.window.blit(self.DFS_btn, self.DFS_btn_rect)
        self.window.blit(self.dijkstra_btn, self.dijkstra_btn_rect)
        self.window.blit(self.A_star_btn, self.A_star_btn_rect)
        self.current_algorithm = self.A_FONT_U.render(self.current_algorithm_str, True, (0, 0, 0), None)
        self.window.blit(self.current_algorithm, self.current_algorithm_rect)
        self.window.blit(self.speed_text, self.speed_text_rect)
        self.window.blit(self.high_btn, self.high_btn_rect)
        self.window.blit(self.medium_btn, self.medium_btn_rect)
        self.window.blit(self.slow_btn, self.slow_btn_rect)

        x_pos = ((self.width * 0.125 * self.scale_x) + (32 * self.scale_x)) * 1.5
        y_pos = (self.height * 0.05 * self.scale_y)

        start_tile_text = self.TILE_SELECT_FONT.render(" Start ", True, (0, 0, 0), None)
        self.window.blit(start_tile_text, (x_pos, y_pos))
        x_pos += 32 * 1.5
        end_tile_text = self.TILE_SELECT_FONT.render(" End ", True, (0, 0, 0), None)
        self.window.blit(end_tile_text, (x_pos, y_pos))
        x_pos += 32 * 1.5
        empty_tile_text = self.TILE_SELECT_FONT.render(" Empty ", True, (0, 0, 0), None)
        self.window.blit(empty_tile_text, (x_pos, y_pos))
        x_pos += 32 * 1.5
        positive_cost_tile_text = self.TILE_SELECT_FONT.render(" Cost +", True, (0, 0, 0), None)
        self.window.blit(positive_cost_tile_text, (x_pos, y_pos))

    def update_display(self):
        self.draw_board()
        self.draw_screen()
        pygame.display.flip()

    def wait_for_input(self):
        self.waiting = True
        user_input = []
        x_pos = ((self.width * 0.125 * self.scale_x) + (32 * self.scale_x - 64)) * 1.5
        y_pos = (self.height * 0.05 * self.scale_y)

        self.tile_options[0] = pygame.transform.scale(self.tile_options[0],
                                                      (32 * self.scale_x * 1.5, 32 * self.scale_y * 1.5))
        self.tile_options_rects[0] = self.tile_options[0].get_rect(topleft=(x_pos, y_pos))
        self.window.blit(self.tile_options[0], (x_pos, y_pos))
        waiting_text = self.TILE_SELECT_FONT.render("Enter tile cost and press enter", True, (0, 0, 0), None)
        self.window.blit(waiting_text, (x_pos, y_pos + int(self.height * 0.06) * self.scale_y))
        pygame.display.flip()
        while self.waiting:
            events = pygame.event.get()
            for event in events:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                    if len(user_input) > 0:
                        user_input.pop()
                        self.window.blit(self.tile_options[0], (x_pos, y_pos))
                        pygame.display.flip()

                elif pygame.key.get_pressed()[pygame.K_RETURN]:
                    pygame.event.pump()
                    if len(user_input) == 0:
                        self.current_weight = ""
                    elif len(user_input) == 1:
                        self.current_weight = user_input[0]
                        self.waiting = False

                    else:
                        print("error")
                elif event.type == pygame.KEYUP:

                    if str(event.unicode).isdigit():
                        user_input.append(str(event.unicode))
                        self.current_weight = ("".join(user_input))
                        self.current_weight_text = self.BIGFONT.render(self.current_weight, True, (0, 0, 0), None)
                        self.window.blit(self.current_weight_text,
                                         (x_pos + 5 * self.scale_x, y_pos - 1 * self.scale_y))
                        pygame.display.flip()
                        if len(user_input) >= 2:
                            self.waiting = False

        pygame.event.pump()

    def update_algorithm_indicator(self, algorithm_num):
        if algorithm_num == 1:
            self.BFS_btn = self.A_FONT.render(" Breadth First Search* ", True, (0, 0, 0), None)
            self.DFS_btn = self.A_FONT.render(" Depth First Search ", True, (0, 0, 0), None)
            self.dijkstra_btn = self.A_FONT.render(" Dijkstra's Algorithm", True, (0, 0, 0), None)
            self.A_star_btn = self.A_FONT.render(" A* Search", True, (0, 0, 0), None)
        if algorithm_num == 2:
            self.BFS_btn = self.A_FONT.render(" Breadth First Search ", True, (0, 0, 0), None)
            self.DFS_btn = self.A_FONT.render(" Depth First Search* ", True, (0, 0, 0), None)
            self.dijkstra_btn = self.A_FONT.render(" Dijkstra's Algorithm", True, (0, 0, 0), None)
            self.A_star_btn = self.A_FONT.render(" A* Search", True, (0, 0, 0), None)
        if algorithm_num == 3:
            self.BFS_btn = self.A_FONT.render(" Breadth First Search ", True, (0, 0, 0), None)
            self.DFS_btn = self.A_FONT.render(" Depth First Search ", True, (0, 0, 0), None)
            self.dijkstra_btn = self.A_FONT.render(" Dijkstra's Algorithm*", True, (0, 0, 0), None)
            self.A_star_btn = self.A_FONT.render(" A* Search", True, (0, 0, 0), None)
        if algorithm_num == 4:
            self.BFS_btn = self.A_FONT.render(" Breadth First Search ", True, (0, 0, 0), None)
            self.DFS_btn = self.A_FONT.render(" Depth First Search ", True, (0, 0, 0), None)
            self.dijkstra_btn = self.A_FONT.render(" Dijkstra's Algorithm", True, (0, 0, 0), None)
            self.A_star_btn = self.A_FONT.render(" A* Search*", True, (0, 0, 0), None)
        pygame.display.flip()
    def visualizer_speed_factor(self):
        if self.speed_setting == 1:
            time.sleep(0.001)
        elif self.speed_setting == 2:
            time.sleep(0.1)
        elif self.speed_setting == 3:
            time.sleep(0.5)

    def randomize_tiles(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j].weight = random.randrange(0, 100)
                self.board[i][j].text = self.FONT.render(str(self.board[i][j].weight), True, (0, 0, 0), None)
                if self.board[i][j].weight != 0:
                    # self.board[i][j].text = self.FONT.render(self.current_weight, True, (0, 0, 0), None)
                    self.draw_single_tile(self.board[i][j], "positive_cost")
                else:
                    self.draw_single_tile(self.board[i][j], "empty")

        random_row_start = random.randrange(0,20)
        random_col_start = random.randrange(0,30)
        temp1 = [random_row_start, random_col_start]
        self.board[random_row_start][random_col_start].start = True
        self.start_tile = self.board[random_row_start][random_col_start]
        self.draw_single_tile(self.start_tile, "start")

        random_row_end = random.randrange(0,20)
        random_col_end = random.randrange(0,30)
        temp2 = [random_row_end, random_col_end]
        while temp1 == temp2:
            random_row_end = random.randrange(0, 20)
            random_col_end = random.randrange(0, 30)
            temp2 = [random_row_end, random_col_end]

        self.board[random_row_end][random_col_end].end = True
        self.end_tile = self.board[random_row_end][random_col_end]
        self.draw_single_tile(self.end_tile, "end")


    # for debugging
    def show_tile_info(self, mouse_pos):
        for i in range(self.rows):
            for j in range(self.cols):
                clicked = self.board[i][j].image_rect.collidepoint(mouse_pos)
                if clicked:
                    print("Tile type: " + self.board[i][j].tile_type)
                    print("Weight: " + str(self.board[i][j].weight))
                    print("Total Cost: " + str(self.board[i][j].total_cost))
                    # print("Visited by: " + str(self.board[i][j].visited_by.weight))

    def update_tile(self, mouse_pos):  # change later so that it doesnt check when irrelevant space clicked
        for i in range(1, len(self.tile_options)):
            clicked = self.tile_options_rects[i].collidepoint(mouse_pos)
            if clicked:
                self.tile_options[0] = self.tile_options[i]
                if i == 1:
                    self.current_tile_type = "start"
                elif i == 2:
                    self.current_tile_type = "end"
                elif i == 3:
                    self.current_tile_type = "empty"
                elif i == 4:
                    self.current_tile_type = "positive_cost"
                    self.waiting = True
                    input = ""
                    run = True
                    x_pos = ((self.width * 0.125 * self.scale_x) + (32 * self.scale_x - 64)) * 1.5
                    y_pos = (self.height * 0.05 * self.scale_y)
                    self.tile_options[0] = pygame.transform.scale(self.tile_options[0],
                                                                  (32 * self.scale_x * 1.5, 32 * self.scale_y * 1.5))
                    self.tile_options_rects[0] = self.tile_options[0].get_rect(topleft=(x_pos, y_pos))
                    self.window.blit(self.tile_options[0], (x_pos, y_pos))
                    pygame.display.flip()
                    self.wait_for_input()
                    self.drag = False


                elif i == 5:
                    self.current_tile_type = "blocked"

        for i in range(self.rows):
            for j in range(self.cols):
                clicked = self.board[i][j].image_rect.collidepoint(mouse_pos)
                if clicked:
                    # self.board[i][j].tile_type = self.current_tile_type
                    if self.board[i][j].start:
                        self.start_tile = None
                    elif self.board[i][j].end:
                        self.end_tile = None
                    self.board[i][j].transform_tile(self.current_tile_type)
                    if self.current_tile_type == "start":
                        if self.start_tile != None and self.start_tile != self.board[i][j]:
                            self.start_tile.transform_tile("empty")
                        self.start_tile = self.board[i][j]
                        self.board[i][j].total_cost = 0

                    elif self.current_tile_type == "end":
                        if self.end_tile != None and self.end_tile != self.board[i][j]:
                            self.end_tile.transform_tile("empty")
                        self.end_tile = self.board[i][j]
                        self.board[i][j].total_cost = 0
                    elif self.current_tile_type == "positive_cost":
                        self.board[i][j].weight = int(self.current_weight)
                        self.board[i][j].text = self.FONT.render(self.current_weight, True, (0, 0, 0), None)
                    return

        if self.BFS_btn_rect.collidepoint(mouse_pos):
            self.current_algorithm_str = " Breadth First Search"
            self.current_algorithm_num = 1
            self.update_algorithm_indicator(1)

        elif self.DFS_btn_rect.collidepoint(mouse_pos):
            self.current_algorithm_str = " Depth First Search"
            self.current_algorithm_num = 2
            self.update_algorithm_indicator(2)

        elif self.dijkstra_btn_rect.collidepoint(mouse_pos):
            self.current_algorithm_str = " Dijkstra's Algorithm"
            self.current_algorithm_num = 3
            self.update_algorithm_indicator(3)
            
        elif self.A_star_btn_rect.collidepoint(mouse_pos):
            self.current_algorithm_str = " A* Search"
            self.current_algorithm_num = 4
            self.update_algorithm_indicator(4)

        elif self.high_btn_rect.collidepoint(mouse_pos):
            self.high_btn = self.SPEED_FONT.render(" High* ", True, (0, 0, 0), None)
            self.medium_btn = self.SPEED_FONT.render(" Medium ", True, (0, 0, 0), None)
            self.slow_btn = self.SPEED_FONT.render(" Slow ", True, (0, 0, 0), None)
            self.speed_setting = 1

        elif self.medium_btn_rect.collidepoint(mouse_pos):
            self.high_btn = self.SPEED_FONT.render(" High ", True, (0, 0, 0), None)
            self.medium_btn = self.SPEED_FONT.render(" Medium* ", True, (0, 0, 0), None)
            self.slow_btn = self.SPEED_FONT.render(" Slow ", True, (0, 0, 0), None)
            self.speed_setting = 2

        elif self.slow_btn_rect.collidepoint(mouse_pos):
            self.high_btn = self.SPEED_FONT.render(" High ", True, (0, 0, 0), None)
            self.medium_btn = self.SPEED_FONT.render(" Medium ", True, (0, 0, 0), None)
            self.slow_btn = self.SPEED_FONT.render(" Slow* ", True, (0, 0, 0), None)

            self.speed_setting = 3

    def reset_board(self):
        self.start_tile = None
        self.end_tile = None
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j].reset_tile_completely()

    def store_prev_state(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j].prev_tile_type = self.board[i][j].tile_type

    def reset_visited_tiles(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j].reset_visited()
                self.board[i][j].transform_tile(self.board[i][j].prev_tile_type)
                if self.board[i][j].prev_tile_type == "start":
                    self.start_tile = self.board[i][j]
                elif self.board[i][j].prev_tile_type == "end":
                    self.end_tile = self.board[i][j]

    def draw_single_tile(self, tile, tile_type):
        factor1 = 0.75
        tile.transform_tile(tile_type)
        tile.image = pygame.transform.scale(tile.image, (32 * self.scale_x * factor1, 32 * self.scale_y * factor1))
        self.window.blit(tile.image, tile.image_rect.topleft)
        if tile.weight != 0:
            self.window.blit(tile.text,
                             (tile.image_rect.left + 3 * self.scale_x, tile.image_rect.top - 1 * self.scale_y))
        pygame.display.flip()
        pygame.event.pump()  # crucial for performance

    def cancel_visualization(self):
        events = pygame.event.get()
        for event in events:
            if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                    self.cancel_visual = True
            elif pygame.key.get_pressed()[pygame.K_c]:
                sys.exit()

    def check_start_and_end(self):
        if self.start_tile is None or self.end_tile is None:
            print("Need both end and start tile")
            return False
        return True

    def update_queue(self, current, queue, visiting):
        if current.right is not None and not current.right.blocked and not current.right.visited:
            if current.right in visiting and visiting[current.right]:
                pass
            else:
                queue.append(current.right)
                visiting[current.right] = True
        if current.down is not None and not current.down.blocked and not current.down.visited:
            if current.down in visiting and visiting[current.down]:
                pass
            else:
                queue.append(current.down)
                visiting[current.down] = True
        if current.left is not None and not current.left.blocked and not current.left.visited:
            if current.left in visiting and visiting[current.left]:
                pass
            else:
                queue.append(current.left)
                visiting[current.left] = True
        if current.up is not None and not current.up.blocked and not current.up.visited:
            if current.up in visiting and visiting[current.up]:
                pass
            else:
                queue.append(current.up)
                visiting[current.up] = True

    def breadth_first_search(self):
        self.draw_board()
        self.draw_screen()
        if not self.check_start_and_end():
            return
        self.store_prev_state()
        queue = deque([])
        visiting = {}
        found = False

        queue.append(self.start_tile)
        it = 0
        while not found and len(queue) > 0 and not self.cancel_visual:
            self.cancel_visualization()
            self.visualizer_speed_factor()
            self.update_queue(queue[0], queue, visiting)

            if not queue[0].visited:
                if queue[0].end:
                    found = True
                else:
                    self.draw_single_tile(queue[0], "visited")
                    visiting[queue[0]] = False

            queue.popleft()
        if not found:
            print("Not found")
        self.cancel_visual = False

    def update_stack(self, current, stack):
        if current.up is not None and not current.up.blocked and not current.up.visited:
            stack.append(current.up)
        if current.left is not None and not current.left.blocked and not current.left.visited:
            stack.append(current.left)
        if current.down is not None and not current.down.blocked and not current.down.visited:
            stack.append(current.down)
        if current.right is not None and not current.right.blocked and not current.right.visited:
            stack.append(current.right)

    def depth_first_search(self):
        self.draw_board()
        self.draw_screen()
        if not self.check_start_and_end():
            return
        self.store_prev_state()
        stack = []
        # visiting = {}
        found = False

        stack.append(self.start_tile)
        it = 0
        while not found and len(stack) > 0 and not self.cancel_visual:
            self.cancel_visualization()
            self.visualizer_speed_factor()
            current = stack[-1]
            stack.pop()
            self.update_stack(current, stack)
            if not current.visited:
                if current.end:
                    found = True
                    break
                else:
                    self.draw_single_tile(current, "visited")
        if not found:
            print("Not found")
        self.cancel_visual = False
    def update_shortest_path(self, current, visited):
        if current.right is not None and not current.right.blocked and current.right not in visited:

            current.right.total_cost = min(current.right.total_cost, current.total_cost + current.right.weight)
            if current.right.total_cost == current.total_cost + current.right.weight:
                current.right.visited_by = current

        if current.down is not None and not current.down.blocked and current.down not in visited:
            current.down.total_cost = min(current.down.total_cost, current.total_cost + current.down.weight)
            if current.down.total_cost == current.total_cost + current.down.weight:
                current.down.visited_by = current

        if current.left is not None and not current.left.blocked and current.left not in visited:
            current.left.total_cost = min(current.left.total_cost, current.total_cost + current.left.weight)
            if current.left.total_cost == current.total_cost + current.left.weight:
                current.left.visited_by = current

        if current.up is not None and not current.up.blocked and current.up not in visited:
            current.up.total_cost = min(current.up.total_cost, current.total_cost + current.up.weight)
            if current.up.total_cost == current.total_cost + current.up.weight:
                current.up.visited_by = current

    def update_heapdict(self, current, hd, visited):
        if current.up is not None and current.up not in visited and not current.up.blocked:
            hd[current.up] = current.up.total_cost
            if current.up.visited_by is None:
                current.up.visited_by = current
        if current.left is not None and current.left not in visited and not current.left.blocked:
            hd[current.left] = current.left.total_cost
            if current.left.visited_by is None:
                current.left.visited_by = current
        if current.down is not None and current.down not in visited and not current.down.blocked:
            hd[current.down] = current.down.total_cost
            if current.down.visited_by is None:
                current.down.visited_by = current
        if current.right is not None and current.right not in visited and not current.right.blocked:
            hd[current.right] = current.right.total_cost
            if current.right.visited_by is None:
                current.right.visited_by = current

    def dijkstra(self):
        self.draw_board()
        self.draw_screen()
        if not self.check_start_and_end():
            return
        self.store_prev_state()
        hd = heapdict.heapdict()
        visited = {}
        found = False
        hd[self.start_tile] = self.start_tile.weight
        while len(hd) > 0 and not found and not self.cancel_visual:
            self.cancel_visualization()
            self.visualizer_speed_factor()
            current = hd.peekitem()
            hd.popitem()
            visited[current[0]] = True
            if current[0].end:
                found = True
            else:
                self.update_shortest_path(current[0], visited)
                self.update_heapdict(current[0], hd, visited)

                if not current[0].start:
                    self.draw_single_tile(current[0], "visited")

        done = False
        temp = current[0]
        if not found:
            pass
        else:
            while not temp.start:
                temp = temp.visited_by
                if temp.visited_by is not None and not temp.start:
                    self.draw_single_tile(temp, "path")
        self.cancel_visual = False


    def heuristic_A(self, current):
        dif = 0
        dif += abs(current.pos[0] - self.end_tile.pos[0])
        dif += abs(current.pos[1] - self.end_tile.pos[1])
        return dif


    def update_shortest_path_A(self, current, visited):
        if current.right is not None and not current.right.blocked and current.right not in visited:
            possible_better_path = current.total_cost + current.right.weight + self.heuristic_A(current.right)
            current.right.total_cost = min(current.right.total_cost, possible_better_path)
            if current.right.total_cost == possible_better_path:
                current.right.visited_by = current

        if current.down is not None and not current.down.blocked and current.down not in visited:
            possible_better_path = current.total_cost + current.down.weight + self.heuristic_A(current.down)
            current.down.total_cost = min(current.down.total_cost, possible_better_path)
            if current.down.total_cost == possible_better_path:
                current.down.visited_by = current

        if current.left is not None and not current.left.blocked and current.left not in visited:
            possible_better_path = current.total_cost + current.left.weight + self.heuristic_A(current.left)
            current.left.total_cost = min(current.left.total_cost, possible_better_path)
            if current.left.total_cost == possible_better_path:
                current.left.visited_by = current

        if current.up is not None and not current.up.blocked and current.up not in visited:
            possible_better_path = current.total_cost + current.up.weight + self.heuristic_A(current.up)
            current.up.total_cost = min(current.up.total_cost, possible_better_path)
            if current.up.total_cost == possible_better_path:
                current.up.visited_by = current


    def  update_heapdict_A(self, current, hd, visited):
        if current.up is not None and current.up not in visited and not current.up.blocked:
            hd[current.up] = current.up.total_cost + self.heuristic_A(current.up)
            if current.up.visited_by is None:
                current.up.visited_by = current
        if current.left is not None and current.left not in visited and not current.left.blocked:
            hd[current.left] = current.left.total_cost + self.heuristic_A(current.left)
            if current.left.visited_by is None:
                current.left.visited_by = current
        if current.down is not None and current.down not in visited and not current.down.blocked:
            hd[current.down] = current.down.total_cost + self.heuristic_A(current.down)
            if current.down.visited_by is None:
                current.down.visited_by = current
        if current.right is not None and current.right not in visited and not current.right.blocked:
            hd[current.right] = current.right.total_cost + self.heuristic_A(current.right)
            if current.right.visited_by is None:
                current.right.visited_by = current


    def A_star(self):
        self.draw_board()
        self.draw_screen()
        if not self.check_start_and_end():
            return
        self.store_prev_state()
        hd = heapdict.heapdict()
        visited = {}
        found = False
        hd[self.start_tile] = self.start_tile.weight
        while len(hd) > 0 and not found and not self.cancel_visual:
            self.cancel_visualization()
            self.visualizer_speed_factor()
            current = hd.peekitem()
            hd.popitem()
            visited[current[0]] = True
            if current[0].end:
                found = True
            else:
                self.update_shortest_path_A(current[0], visited)
                self.update_heapdict_A(current[0], hd, visited)

                if not current[0].start:
                    self.draw_single_tile(current[0], "visited")

        done = False
        temp = current[0]
        if not found:
            print("Not Found")
        else:
            while not temp.start:
                temp = temp.visited_by
                if temp.visited_by is not None and not temp.start:
                    self.draw_single_tile(temp, "path")
        self.cancel_visual = False

class Tile(Board):

    def __init__(self):
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.start = False
        self.end = False
        self.visited = False
        self.blocked = False
        self.pos = [0,0]
        self.weight = 0
        self.total_cost = INFINITE
        self.visited_by = None
        self.visiting_next = None
        self.tile_type = "empty"
        self.prev_tile_type = None
        self.image = pygame.image.load("Assets/Empty_Tile.png")
        self.image_rect = None
        self.FONT = pygame.font.SysFont('arial', 21)
        self.text = self.FONT.render(str(self.weight), True, (0, 0, 0), None)

    def reset_tile(self):
        self.start = False
        self.end = False
        self.visited = False
        self.blocked = False
        self.weight = 0
        self.visited_by = None
        self.visiting_next = None
        self.tile_type = "empty"
        self.image = pygame.image.load("Assets/Empty_Tile.png")
        self.text = self.FONT.render(str(self.weight), True, (0, 0, 0), None)  # todo might need to remove

    def reset_visited(self):
        # self.start = False
        # self.end = False
        # self.blocked = False
        self.total_cost = INFINITE

        self.visited = False
        self.visited_by = None
        self.visiting_next = None
        # self.tile_type = "Assets/Empty_Tile.png"
        # self.image = self.prev_image

    def reset_tile_keep_weight(self):
        self.start = False
        self.end = False
        self.visited = False
        self.blocked = False
        self.total_cost = INFINITE
        self.visited_by = None
        self.visiting_next = None
        self.tile_type = "empty"
        self.image = pygame.image.load("Assets/Empty_Tile.png")

    def reset_tile_keep_weight_and_path(self):
        self.start = False
        self.end = False
        self.blocked = False
        self.visited = False
        self.tile_type = "empty"
        self.image = pygame.image.load("Assets/Empty_Tile.png")

    def reset_tile_completely(self):
        self.start = False
        self.end = False
        self.visited = False
        self.blocked = False
        self.weight = 0
        self.total_cost = INFINITE
        self.visited_by = None
        self.visiting_next = None
        self.tile_type = "empty"
        self.prev_tile_type = None
        self.image = pygame.image.load("Assets/Empty_Tile.png")
        self.text = self.FONT.render(str(self.weight), True, (0, 0, 0), None)

    def transform_tile(self, type):
        if type == "start":
            self.reset_tile()
            self.tile_type = type
            self.start = True
            self.visited = True
            self.total_cost = 0
            self.image = pygame.image.load("Assets/Start_Tile.png")


        elif type == "end":
            self.reset_tile()
            self.tile_type = type
            self.end = True
            self.total_cost = 0
            self.image = pygame.image.load("Assets/End_Tile.png")


        elif type == "blocked":
            self.reset_tile()
            self.tile_type = type
            self.blocked = True
            self.image = pygame.image.load("Assets/Inaccessible.png")


        elif type == "visited":
            self.reset_tile_keep_weight_and_path()
            # self.prev_tile_type = self.tile_type
            self.tile_type = type
            self.visited = True
            self.image = pygame.image.load("Assets/Visited_Tile.png")

        elif type == "empty":
            self.reset_tile()

        elif type == "positive_cost":
            self.reset_tile_keep_weight()
            self.tile_type = type
            self.image = pygame.image.load("Assets/Positive_Cost_Tile.png")

        # elif type == "negative_cost":
        #     self.reset_tile_keep_weight()
        #     self.tile_type = type
        #     self.image = pygame.image.load("Assets/Negative_Cost_Tile.png")

        elif type == "path":
            self.reset_tile_keep_weight_and_path()
            self.tile_type = type
            self.image = pygame.image.load("Assets/Path_Tile.png")

