from appscript import app, k
import numpy as np
import time, math
import autopy
import screenshot_taker as st
import squeare_detector as sd
import cv2, sys

def shoot_left():
    app('System Events').keystroke('a')
def shoot_right():
    app('System Events').keystroke('d')
def shoot_up():
    app('System Events').keystroke('w')
def shoot_down():
    app('System Events').keystroke('s')

def shoot_on_comand(command):
    # print "\n\n\n\n\n\n\n\n\n\n**************\n\n\n\n\n\n\n\n"
    
    commands = {'left':'a', 'right':'d', 'up':'w','down':'s'}
    if command in commands:
        app('System Events').keystroke(commands[command])
    else:
        if command == "right-down":
            # print "\n\n\n\n\n\n\n\n\n\n**************\n\n\n\n\n\n\n\n"
            app('System Events').keystroke(commands['right'])
            app('System Events').keystroke(commands['down'])
        if command == "right-up":
            app('System Events').keystroke(commands['right'])
            app('System Events').keystroke(commands['up'])
        if command == "left-down":
            app('System Events').keystroke(commands['left'])
            app('System Events').keystroke(commands['down'])
        if command == "left-up":
            app('System Events').keystroke(commands['left'])
            app('System Events').keystroke(commands['up'])



def shoot_on_commands(commands, wait_between_same = False):
    last_command = ""
    for command in commands:
        if command == last_command and wait_between_same:
            time.sleep(0.01)
        shoot_on_comand(command)

def where_is_square(square, level3):
    _, _, square_x_mid, square_y_mid = sd.get_square_params(square)
    if abs(abs(320 - square_x_mid) - abs(320 - square_y_mid) )> 15 or not level3:
        if abs(square_x_mid - 320) > abs(square_y_mid - 320):
            if square_x_mid>320:
                return "right"
            else:
                return "left"
        else:
            if square_y_mid>320:
                return "down"
            else:
                return "up"
    else:
        # print "FOUND DIOGONAL"
        if square_x_mid>320:
            if square_y_mid>320:
                return "right-down"
            else:
                return "right-up"
        else:
            if square_y_mid>320:
                return "left-down"
            else:
                return "left-up"

def clean_n_lines_on_screen(n):
    for i in xrange(n):
        sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line

def get_distance(square):
    _, _, square_x_mid, square_y_mid = sd.get_square_params(square)
    return  math.sqrt((320 - square_x_mid)*(320 - square_x_mid) + (320 - square_y_mid)*(320 - square_y_mid))    



# def get_closest_direction(squares):
#     min_distance = 320
#     closest_direction = "" 
#     for square in squares:
#         if get_distance(square) < min_distance:
#             min_distance = get_distance(square)
#             closest_direction = where_is_square(square)
#     return closest_direction

def get_commands_to_shoot(red_squares, blue_squares,level3):
    bots = []
    for red_square in red_squares:
        bots.append(Bot(red_square, True, level3))
    for blue_square in blue_squares:
        bots.append(Bot(blue_square, False, level3))
    sorted(bots, key=lambda bot: bot.distance)
    commands = []
    dont_shoot_this_direction_anymore = []
    for bot in bots:
        if bot.enemy:
            if not (bot.posiition in dont_shoot_this_direction_anymore):
                commands.append(bot.posiition)
        else:
            dont_shoot_this_direction_anymore.append(bot.posiition) 
    return commands




class Bot():
    def __init__(self, square, enemy, level3):
        self.height, self.width, self.x_mid, self.y_mid = sd.get_square_params(square) 
        self.enemy = enemy
        self.posiition = where_is_square(square, level3)
        self.distance = get_distance(square)

if __name__ == '__main__':
    args = sys.argv
    level3 = False
    if len(args)>1:
        if args[1] == '1':
            DELAY = 0.1
        elif args[1] == '3':
            DELAY = 0.03
            level3 = True
        elif args[1] == '4':
            DELAY == 0.01

    else:
        DELAY = 0.0


    autopy.mouse.move(200,200)
    time.sleep(0.5)
    autopy.mouse.click()
    time.sleep(2)
    if level3:
        time.sleep(1)
    # time.sleep(5)
    app('System Events').keystroke('d')
    time.sleep(1)
    empty_counter = 0
    background_color = 0
    lines_to_clean = 0
    background_colors = {118:'red', 56:'blue', 78:'purple', 80:'green'}
    counter  = 0
    start_time = time.time() 
    for i in xrange(1000):
        counter +=1
        log = ""
        file_name = st.make_screenshot()
        new_background_color = sd.get_background_color(file_name)
        if new_background_color == 0 and empty_counter < 10:
            """"""
        else: 
            # if background_color != new_background_color:
                # time.sleep(0.005)
                # file_name = st.make_screenshot()
                # new_background_color = sd.get_background_color(file_name)
            background_color = new_background_color
        red_squares, blue_squares,_ = sd.get_red_and_blue_squares(file_name, level3) 
        if background_color in background_colors:
            log = "background_color: {}".format(background_colors[background_color])
        else:
            log = "background_color: {}".format(background_color) 
        if len(red_squares)>0:
            empty_counter=0
    
            commands = get_commands_to_shoot(red_squares, blue_squares, level3)
            shoot_on_commands(commands, wait_between_same=True)
    



            clean_n_lines_on_screen(lines_to_clean)
            lines_to_clean = 0
            log =  "{}; commands to shoot: {}".format(log, commands)
            log+="\n enemies:"
            lines_to_clean+=6
            for red_square in red_squares:
                log="{}\n    [{},{}]".format(log, red_square[0][0], red_square[0][1])
                lines_to_clean+=1
            log+="\n              "
            log+="\n              "
            log+="\n              "
            log+="\n              "
            print log



        # cv2.imshow('squares', blank_image)
        if background_color==0 or len(red_squares)==0:
            empty_counter+=1
            if empty_counter==20:
                break
        time.sleep(DELAY)
    end_time = time.time()
    print "time = {}".format((end_time - start_time))
    print "frames = {}".format(counter)
    print "frame / time = {}".format((end_time- start_time)/ counter)
        




