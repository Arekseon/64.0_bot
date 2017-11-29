#!/usr/bin/env python


from PIL import ImageGrab
from PIL import Image
import Quartz.CoreGraphics as CG
from mss import mss
# import sys

import numpy as np
import cv2

# global counter
sct = mss()
mon = {'top': 46, 'left': 28, 'width': 640, 'height': 640}

answer = ""
img = ""
answer = ""
gray,not_gray,not_gray2 = "","",""
counter = 0
region = CG.CGRectMake(28, 46, 640, 640)
def get_screenshot():
    # # im=ImageGrab.grab(bbox=(28, 46, 640, 640)) # X1,Y1,X2,Y2
 


    # # while 1:
    # sct.get_pixels(mon)
    # img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
    #     # cv2.imshow('test', np.array(img))
    #     # if cv2.waitKey(25) & 0xFF == ord('q'):
    #     #     cv2.destroyAllWindows()
    #     # break
    
    # answer = np.array(img)
    # # del sct, img, mon

    # printscreen_pil =  ImageGrab.grab(bbox=(46,28,640,640))
    # # time_stamp1 = time.time()
    # printscreen_numpy =   np.array(printscreen_pil, dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],4))
    # region = CG.CGRectMake(28, 46, 640, 640)

    # Create screenshot as CGImage
    image = CG.CGWindowListCreateImage(
        region,
        CG.kCGWindowListOptionOnScreenOnly,
        CG.kCGNullWindowID,
        CG.kCGWindowImageDefault)

    width = CG.CGImageGetWidth(image)
    height = CG.CGImageGetHeight(image)
    bytesperrow = CG.CGImageGetBytesPerRow(image)

    pixeldata = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(image))
    image = np.frombuffer(pixeldata, dtype=np.uint8)
    image = image.reshape((height, bytesperrow//4, 4))
    image = image[:,:width,:]
    return  image

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    answer = abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )
    del d1, d2
    return answer

def find_squares(img):

    # img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    drop = False
    # return squares
    for gray in cv2.split(img):
    # grey = cv2.split(img)[0]
    # gray,not_gray,not_gray2,_ = cv2.split(img)
    # gray = img
    # for x in xrange(1):
        if drop:
            break
        else:
            drop = True
        # for thrs in xrange(0, 255, 208):
            # if thrs == 0:
        bin = cv2.Canny(gray, 0, 50, apertureSize=5)
        # bin = cv2.dilate(bin, None)
        # else:
        #     retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
        # contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        bin, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, True)
            cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
            if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                cnt = cnt.reshape(-1, 2)
                max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                if max_cos < 0.1:
                    squares.append(cnt)
    # del gray,not_gray,not_gray2, bin, retval, cnt_len, cnt
    return squares

def modify_with_offset(square, offset):
    for dot in square:
        dot[0]+=offset[0]
        dot[1]+=offset[1]
    return square

def modify_nultiple_squares_wirh_offset(squares, offset):
    for square in squares:
        square = modify_with_offset(square, offset)
    return squares

def simular_squeares(square1, square2):
    error_size = 10
    square1_height, square1_wedth, square1_x_mid, square1_y_mid = get_square_params(square1)
    square2_height, square2_wedth, square2_x_mid, square2_y_mid = get_square_params(square2)
    
    if (abs(square1_wedth - square2_wedth) < error_size and
        abs(square1_height - square2_height) < error_size and
        abs(square1_x_mid - square2_x_mid ) < error_size and
        abs(square1_y_mid - square2_y_mid) < error_size):
        del square1_height, square1_wedth, square1_x_mid, square1_y_mid
        del square2_height, square2_wedth, square2_x_mid, square2_y_mid
        return True
    del square1_height, square1_wedth, square1_x_mid, square1_y_mid
    del square2_height, square2_wedth, square2_x_mid, square2_y_mid
    return False



def get_unique_squares(squares):
    unique_squares = []
    # unique_squares.append(squares[0])
    for square in squares:
        is_unique = True
        for unique_square in unique_squares:
            if simular_squeares(unique_square, square):
                is_unique = False
        if is_unique:
            unique_squares.append(square)
    return unique_squares


def get_uniqie_background_color(img,shape):
    shape_height, shape_wedth, shape_x_mid, shape_y_mid = get_square_params(shape)
    direction = where_is_square(shape)
    if direction in ['left', 'right']:
        background_color = img[shape_y_mid+shape_height][shape_x_mid][2]
    elif direction in ['down', 'up']:
        background_color = img[shape_y_mid][shape_x_mid+shape_wedth][2]

    else:
        # possibble_background_colors = []
        # for i in [-1,1]:
        #     for j in [-1,1]:
        #         try:
        #             possibble_background_colors.append([shape_y_mid+ i*shape_height][shape_x_mid+ j*shape_wedth][2])
        #         except:
        #             """"""
        # for color in possibble_background_colors:
        #     if color != 0:
        #         background_color = color
        background_color = img[5][65][2]
    # print "background_color for {} is {}".format(shape, background_color)
    # print background_color
    del shape_height, shape_wedth, shape_x_mid, shape_y_mid, direction
    return background_color

def check_if_level_3(img):
    if img[5][65][2] != 0 and img[120][260][2]:
        return True
    return False

def get_red_and_blue_squares(from_file=False, write_screenshot_to_disk=False): # , from_file=False):
    if from_file:    
        img = cv2.imread(filename)
    else:
        img = get_screenshot()
    squares = find_squares(img)
    background_color = img[200][200][2]
    # crop_left_img = img[270:360, 360:,:]
    # crop_right_img = img[270:360, :270,:]

    # # horisontal_crop = img[270:360, :,:]
    # # vertical_crop = img[:,280:370,:]

    # crop_up_img =   img[:270, 280:370,:]
    # crop_down_img = img[360:, 280:370,:]
    
    # left_squares = find_squares(crop_left_img)
    # right_squares = find_squares(crop_right_img)
    # up_squares = find_squares(crop_up_img)
    # down_squares = find_squares(crop_down_img)


    # # horisontal_squares = find_squares(horisontal_crop)
    # # horisontal_squares = modify_nultiple_squares_wirh_offset(horisontal_squares, [0,270])

    # # vertical_squares = find_squares(vertical_crop)
    # # vertical_squares = modify_nultiple_squares_wirh_offset(vertical_squares, [280,0])

    # left_squares =  modify_nultiple_squares_wirh_offset(left_squares, [360,270]) # actually right
    # right_squares = modify_nultiple_squares_wirh_offset(right_squares, [0,270]) # actually left
    # up_squares =    modify_nultiple_squares_wirh_offset(up_squares, [280,0])
    # down_squares =  modify_nultiple_squares_wirh_offset(down_squares, [280,360])

    # squares = left_squares+ right_squares + up_squares + down_squares
    # # squares = horisontal_squares + vertical_squares


    squares = get_unique_squares(squares)
    red_squares = []
    green_squares = []
    blue_squeares = []
    level3 = check_if_level_3(img)
    for shape in squares:
        shape_height, shape_wedth, shape_x_mid, shape_y_mid = get_square_params(shape)
        if not level3:
            if shape_height> 35 and shape_height < 65 and shape_wedth> 35 and shape_height<65: 
                background_color = get_uniqie_background_color(img,shape)
                # background_color = get_background_for_level5(img,shape)
                if not background_color == 0:
                    if img[shape_y_mid][shape_x_mid][2] in [background_color,0]:
                        red_squares.append(shape)
                    else:
                        blue_squeares.append(shape)
            else:
                green_squares.append(shape)
        else:
            if shape_wedth> 50 and shape_wedth<85 and shape_height> 50 and shape_height<85: 
                background_color = img[320][100][2]
                if not background_color == 0:
                    if img[shape_y_mid][shape_x_mid][2] in [background_color-1, background_color, background_color+1,0]:
                        red_squares.append(shape)
                    else:
                        blue_squeares.append(shape)
            else:
                green_squares.append(shape)
    filename = ""
    filename = save_image(img, red_squares, blue_squeares, green_squares,write_screenshot_to_disk)
    del img, squares, background_color
            
    return red_squares, blue_squeares, green_squares, filename

def save_image(img, red_squares, blue_squeares, green_squares, write_screenshot_to_disk):
    global counter
    filename = 'screenshots/screenshot_{}{}.png'.format('0'*(4-len(str(counter))), counter )
    if write_screenshot_to_disk:
        draw_n_save(img, red_squares, blue_squeares, green_squares, filename, counter)
    counter+=1
    return filename
def draw_n_save(img, red_squares, blue_squeares, green_squares, filename, counter):
    # cv2.imwrite("{}or{}".format(filename[:-4], filename[-4:]),img)
    
    cv2.drawContours( img, red_squares, -1, (0, 0, 255,1), 4 )
    cv2.drawContours( img, green_squares, -1, (0, 255, 0,1), 4 )
    cv2.drawContours( img, blue_squeares, -1, (255, 0, 0,1), 4 )
    cv2.imwrite(filename,img)
    


def get_background_color(filename):
    img = cv2.imread(filename)
    background_color = img[200][200][2]
    return background_color


def get_square_params(square):
    height = 0
    width = 0
    x_middle = 0
    y_middle = 0
    x_array=[]
    y_array=[]

    for dot in square:
        x_middle+=dot[0]
        y_middle+=dot[1]
        x_array.append(dot[0])
        y_array.append(dot[1])
    x_middle/=4
    y_middle/=4
    height = max(y_array) - min(y_array)
    width = max(x_array) - min(x_array)
    del x_array,y_array

    return height, width, x_middle, y_middle
def where_is_square(square):
    # global level
    _, _, square_x_mid, square_y_mid = get_square_params(square)
    if abs(abs(320 - square_x_mid) - abs(320 - square_y_mid) )> 15: 
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

if __name__ == '__main__':
    from glob import glob
    for fn in glob('*.png'):
        img = cv2.imread(fn)
        red_squares, blue_squeares, green_squares,_ = get_red_and_blue_squares(from_file=fn)


        cv2.drawContours( img, red_squares, 1, (255, 255, 255,255), 4 )
        cv2.drawContours( img, green_squares, 1, (0, 255, 0,0), 4 )
        cv2.drawContours( img, blue_squeares, 1, (255, 0, 0,0), 4 )
        cv2.imshow('squares', img)
        ch = cv2.waitKey()
        if ch == 27:
            break
    cv2.destroyAllWindows()