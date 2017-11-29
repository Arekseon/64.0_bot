import screenshot_taker as ST
import square_detector as SD
import time, sys, threading, math, os, gc
import autopy
from appscript import app, k
from threading import Thread, Lock
from termcolor import colored

from pympler import muppy
from pympler import summary

# global directions_sight, level, game_over, game_over_mutex, direction_access_mutex, speed
# global commands
# global speeds
# speeds = []


BLANK_SCREENSHOT_GAME_OVER_COUNTER = 50
game_over_mutex = Lock()
direction_access_mutex = Lock()
speed_lock = Lock()

directions_sight = {'left':[],
                    'right':[],
                    'up': [],
                    'down':[],

                    'right-down':[],
                    'right-up':[],
                    'left-up': [],
                    'left-down':[]}

commands = {'left':['a'], 
            'right':['d'], 
            'up':['w'],
            'down':['s'],

            'right-down':['d','s'],
            'right-up':  ['d','w'],
            'left-down': ['a','s'],
            'left-up':   ['a','w']
            }


def keep_updating_field(save_screenshots=False):
    global game_over, directions_sight, speed
    game_over_counter = 0
    frame_counter = 0
    start_time = time.time()
    while True:
        game_over_mutex.acquire()
        if game_over:
            game_over_mutex.release()
            break
        game_over_mutex.release()
        
        screenshot_time = time.time()
        red_squares, blue_squares,_, saved_screenshot_name = SD.get_red_and_blue_squares(write_screenshot_to_disk=save_screenshots )

        direction_access_mutex.acquire()
        update_field(red_squares, blue_squares, screenshot_time)
        speed_lock.acquire()
        if print_direction_sight(saved_screenshot_name) == 0 and speed:
            speed_lock.release()
            game_over_counter+=1
            if game_over_counter>BLANK_SCREENSHOT_GAME_OVER_COUNTER:
                game_over= True
        else:
            speed_lock.release()
            game_over_counter=0
        direction_access_mutex.release()
        frame_counter +=1

        time.sleep(0.005)
        gc.collect()
    end_time = time.time()
    delta_time = end_time - start_time
    print "total time: {}".format(delta_time)
    print "total frames: {}".format(frame_counter)
    print "average time per frame: {}".format(delta_time/frame_counter)
    print "speed: {}".format(speed)
    global speeds
    average_speed = 0
    speed_lock.acquire()

    for speed_cell in speeds:
        average_speed +=speed_cell
    average_speed /= len(speeds)
    speed_lock.release()
    print "average speed: {}".format(average_speed)


def print_direction_sight(saved_screenshot_name):
    # global directions_sight, speed
    # print"BOTS ON SIGHT"
    print saved_screenshot_name
    bot_on_sight_counter = 0
    for key in directions_sight:
        if len(directions_sight[key]) >0:
            print " BOT on {}:".format(key)
        for bot in directions_sight[key]:
            bot_on_sight_counter+=1
            bot_to_print=""
            if not bot.enemy:
                bot_to_print = colored("Friend", 'blue')
            else:
                bot_to_print = colored("Enemy ", 'red') if bot.alive else colored("Denemy", 'white')
            print "   {}: {}".format(bot_to_print, bot.distance - speed * (time.time()-bot.time_appeared))
    return bot_on_sight_counter


def update_field(red_squares, blue_squares, screenshot_time):
    # global directions_sight
    for red_square in red_squares:
        red_square_bot = Bot(red_square, True, screenshot_time)
        dublicate = False
        for bot_in_direction in directions_sight[red_square_bot.direction]:
            if check_if_same_bot(bot_in_direction, red_square_bot):
                dublicate = True
        if not dublicate:
            directions_sight[red_square_bot.direction].append(red_square_bot)

    for blue_square in blue_squares:
        blue_square_bot = Bot(blue_square, False, screenshot_time)
        dublicate = False
        for bot_in_direction in directions_sight[blue_square_bot.direction]:
            if check_if_same_bot(bot_in_direction, blue_square_bot):
                dublicate = True
        if not dublicate:
            directions_sight[blue_square_bot.direction].append(blue_square_bot)



def check_if_same_bot(Bot1, Bot2):
    global speed
    if Bot1.direction != Bot2.direction:
        return False
    distance_delta = abs(Bot2.distance - Bot1.distance)
    time_delta = abs(Bot2.time_appeared - Bot1.time_appeared)
    if time_delta == 0:
        return False
    speed_lock.acquire()
    if not speed:
        # global speeds
        print "NO SPEED YET CALCULATED"
        print "distance_delta: {}".format(distance_delta)
        print "time_delta: {}".format(time_delta)
        speed = distance_delta/time_delta
        print speed
        speeds.append(speed)
        speed_lock.release()
        return True
    else:
        # if abs(distance_delta/time_delta - speed) < speed:
        if abs(distance_delta - time_delta*speed) < 30:
            speeds.append(distance_delta/time_delta)
            speed = sum(speeds) / float(len(speeds))
            speed_lock.release()
            if (not Bot1.alive) and time.time() - Bot1.time_shoot>0.1:
                Bot1.alive = True
            return True
        else:
            speed_lock.release()
    return False


def keep_shooting():
    global game_over, directions_sight
    while True:
        game_over_mutex.acquire()
        if game_over:
            game_over_mutex.release()
            break
        game_over_mutex.release()
        

        direction_access_mutex.acquire()
        bots_to_shoot = get_bots_to_shoot()
        for bot in bots_to_shoot:
            print "                          bot to shoot: {}".format(bot.direction)
        # print "________"
        # time.sleep(0.01)
        shoot_bots(bots_to_shoot)
        speed_lock.acquire()
        if speed:
            # speed_lock.release()
            clear_friend_bots()
        speed_lock.release()

        direction_access_mutex.release()
        time.sleep(0.005)




def get_bots_to_shoot():
    # global directions_sight

    bots = []
    for key in directions_sight:
        bots += directions_sight[key]
    sorted(bots, key=lambda bot: bot.distance)
    bots_to_shoot = []
    dont_shoot_this_direction_anymore = []
    for bot in bots:
        if bot.enemy:
            if bot.alive:
                if not (bot.direction in dont_shoot_this_direction_anymore):
                    bots_to_shoot.append(bot)
        else:
            dont_shoot_this_direction_anymore.append(bot.direction) 
    return bots_to_shoot

def clear_friend_bots():
    # global directions_sight, speed
    for key in directions_sight:
        for bot in directions_sight[key]:
            # if not bot.enemy:
                current_time = time.time()
                if current_time > (bot.time_appeared + (bot.distance / speed)):
                    remove_bot(bot)
                    bot.alive = False
                    del bot


class Bot():
    def __init__(self, square, enemy, screenshot_time):
        self.height, self.width, self.x_mid, self.y_mid = SD.get_square_params(square) 
        self.enemy = enemy
        self.direction = where_is_square(square)
        self.distance = get_distance(square)
        self.time_appeared = screenshot_time
        self.time_shoot = 0
        self.alive = True

def where_is_square(square):
    _, _, square_x_mid, square_y_mid = SD.get_square_params(square)
    if abs(abs(320 - square_x_mid) - abs(320 - square_y_mid) )> 15: #or not level == 3:
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
def get_distance(square):
    _, _, square_x_mid, square_y_mid = SD.get_square_params(square)
    return  math.sqrt((320 - square_x_mid)*(320 - square_x_mid) + (320 - square_y_mid)*(320 - square_y_mid))    

def shoot_on_comand(command):
    # global commands
    if command in commands:
        for key in commands[command]:
            print "                               shooting: {}".format(key)
            app('System Events').keystroke(key)

def shoot_bots(bots_to_shoot, wait_between_same = True):
    # global directions_sight
    last_command = ""
    for bot in bots_to_shoot:
        # if bot.direction == last_command and wait_between_same:
        time.sleep(0.01)
        shoot_on_comand(bot.direction)
        # if bot.direction in  ['right-down', 'right-up','left-up', 'left-down']:
        #     time.sleep(0.01)
        #     shoot_on_comand(bot.direction)
            

        bot.alive = False
        bot.time_shoot = time.time()

def remove_bot(bot):
    # global directions_sight
    for key in directions_sight:
        if bot in directions_sight[key]:
            directions_sight[key].remove(bot)
            print "                                                         bot on {} removed".format(bot.direction)

def delete_previos_png():
    from glob import glob
    for fn in glob('screenshots/*.png'):
        print "removing file: {}".format(fn)
        os.remove(fn)
    print "done"

def start_new_game():
    time.sleep(2)
    autopy.mouse.move(800,200)
    time.sleep(0.5)
    autopy.mouse.click()
    time.sleep(2)
    app('System Events').keystroke(126)
    time.sleep(0.5)
    app('System Events').keystroke(36)
    



if __name__ == '__main__':
    delete_previos_png()
    args = sys.argv
    # level3 = False
    # if len(args)<=1:
    #     print "No level specified"
    #     sys.exit()


    global level, game_over, speeds

    # if int(args[1]) in range(1,6):
    #     level = int(args[1])
    # else:
    #     print "Wrong level specified"
    #     sys.exit()
    if 's' in  args:
        save_screenshots = True
    else:
        save_screenshots = False

    game_over = False
    speed = False
    speeds = []

    autopy.mouse.move(200,200)
    time.sleep(0.5)
    autopy.mouse.click()
    time.sleep(1)
    # if level3:
    #     time.sleep(1)
    # time.sleep(5)
    app('System Events').keystroke('d')
    time.sleep(1)
    empty_counter = 0
    background_color = 0
    lines_to_clean = 0


    looping_updating_field = threading.Thread(target=keep_updating_field, args=(save_screenshots,))
    looping_updating_field.start()
    
    looping_shooting = threading.Thread(target=keep_shooting)
    looping_shooting.start()



    global directions_sight
    # time.sleep(64)
    # looping_shooting.join()
    looping_updating_field.join()
    game_over_mutex.acquire()
    game_over = True
    game_over_mutex.release()
    print  "total on left : {}".format(len(directions_sight['left']))
    print  "total on righ : {}".format(len(directions_sight['right']))
    print  "total on down : {}".format(len(directions_sight['down']))
    print  "total on  up  : {}".format(len(directions_sight['up']))
    # time.sleep(20)

    # all_objects = muppy.get_objects()
    # sum1 = summary.summarize(all_objects)
    # summary.print_(sum1)    

    autopy.mouse.move(800,200)
    time.sleep(0.5)
    autopy.mouse.click()


    # start_new_game()
    # start_new_game_thred = threading.Thread(target=start_new_game)
    # start_new_game_thred.start()
    # sys.exit()























