from Board import *

pygame.init()

screen_w = pygame.display.Info().current_w
screen_h = pygame.display.Info().current_h
win = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption('Path finding visualizer')
# Monitor resolution
count = 0
board = Board(win, 20, 30, screen_w, screen_h)
board.initialize_board()
run = True
board.update_display()
x = 0
while run:
    #scales everything in window depending on the current screen dimensions
    scale_x = win.get_width() / screen_w
    scale_y = win.get_height() / screen_h

    for event in pygame.event.get():
        if event.type is not None and board.drag:

            board.update_display()

        if event.type == pygame.QUIT:
            run = False
            sys.exit()


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                run = False
                sys.exit()


            elif event.key == pygame.K_1:
                board.current_algorithm_str = " Breadth First Search"
                board.current_algorithm_num = 1
                board.update_algorithm_indicator(1)
                board.breadth_first_search()
            elif event.key == pygame.K_2:
                board.current_algorithm_str = " Depth First Search"
                board.current_algorithm_num = 2
                board.update_algorithm_indicator(2)
                board.depth_first_search()
            elif event.key == pygame.K_3:
                board.current_algorithm_str = " Dijkstra's Algorithm"
                board.current_algorithm_num = 3
                board.update_algorithm_indicator(3)
                board.dijkstra()
            elif event.key == pygame.K_4:
                board.current_algorithm_str = " A* Search"
                board.current_algorithm_num = 4
                board.update_algorithm_indicator(4)
                board.A_star()

            elif event.key == pygame.K_BACKQUOTE:
                board.reset_visited_tiles()
            elif event.key == pygame.K_DELETE:
                board.reset_board()
            elif event.key == pygame.K_r:
                board.randomize_tiles()
            elif event.key == pygame.K_RETURN:
                if board.current_algorithm_num == 1:
                    board.breadth_first_search()
                elif board.current_algorithm_num == 2:
                    board.depth_first_search()
                elif board.current_algorithm_num == 3:
                    board.dijkstra()
                elif board.current_algorithm_num == 4:
                    board.A_star()
            # for debugging
            # elif event.key == pygame.K_q:
            #     mouse_pos = pygame.mouse.get_pos()
            #     board.show_tile_info(mouse_pos)
            board.update_display()

        elif event.type == pygame.VIDEORESIZE:
            pass
        elif event.type == pygame.MOUSEBUTTONUP:
            board.drag = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            board.drag = True
            mouse_pos = pygame.mouse.get_pos()
            board.update_tile(mouse_pos)
        elif event.type == pygame.MOUSEMOTION:
            if board.drag:
                mouse_pos = pygame.mouse.get_pos()
                board.update_tile(mouse_pos)



