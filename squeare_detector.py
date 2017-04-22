#!/usr/bin/env python

'''
Simple "Square Detector" program.
Loads several images sequentially and tries to find squares in each image.
'''
from PIL import ImageGrab
import Quartz.CoreGraphics as CG
# Python 2/3 compatibility
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
import key_presser as kp

def get_screenshot():
    # print"KILL POIN 0"
    # # im=ImageGrab.grab(bbox=(28, 46, 640, 640)) # X1,Y1,X2,Y2
    # im=CG.CGRectMake(28, 46, 640, 640)
    
    # print"KILL POIN 1"

    # #convert to numpy array
    # # im=im.convert('RGB')
    # print"KILL POIN 2"
    # imcv = np.array(im)
    # print"KILL POIN 3" 
    # # imcv = imcv[:, :, ::-1].copy()
    # print"KILL POIN 4"

    printscreen_pil =  ImageGrab.grab(bbox=(28, 46, 640, 640))
    # printscreen_numpy =   np.array(printscreen_pil.getdata(),dtype='uint8')\
    # .reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
    return printscreen_pil 

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_squares(img):
    # img = get_screenshot()
    # img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    # for gray in cv2.split(img):
    gray,_,_ = cv2.split(img)
    for x in xrange(1):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            # bin, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
    return squares

def simular_squeares(square1, square2):
    error_size = 10
    square1_height, square1_wedth, square1_x_mid, square1_y_mid = get_square_params(square1)
    square2_height, square2_wedth, square2_x_mid, square2_y_mid = get_square_params(square2)
    
    if (abs(square1_wedth - square2_wedth) < error_size and
        abs(square1_height - square2_height) < error_size and
        abs(square1_x_mid - square2_x_mid ) < error_size and
        abs(square1_y_mid - square2_y_mid) < error_size):
        return True
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

# def get_red_squares(filename):
#     img = cv2.imread(filename)
#     squares = find_squares(img)
#     background_color = img[200][200][2]
#     squares = get_unique_squares(squares)
#     red_squares = []
#     green_squares = []
#     blue_squeares = []
#     for shape in squares:
#         shape_height, shape_wedth, shape_x_mid, shape_y_mid = get_square_params(shape)
#         if shape_height> 40 and shape_height < 60 and shape_wedth> 40 and shape_height<60: 
#             if img[shape_y_mid][shape_x_mid][2] == background_color:
#                 red_squares.append(shape)
#             else:
#                 blue_squeares.append(shape)
#         else:
#             green_squares.append(shape)
#     return red_squares

def get_uniqie_background_color(img,shape):
    shape_height, shape_wedth, shape_x_mid, shape_y_mid = get_square_params(shape)
    direction = kp.where_is_square(shape, False)
    if direction in ['left', 'right']:
        background_color = img[shape_y_mid+shape_height][shape_x_mid][2]
    else:
        background_color = img[shape_y_mid][shape_x_mid+shape_wedth][2]
    # print "background_color for {} is {}".format(shape, background_color)
    return background_color


def get_red_and_blue_squares(filename, level3=False):
    img = cv2.imread(filename)
    squares = find_squares(img)
    # squares = find_squares(0)
    background_color = img[200][200][2]
    squares = get_unique_squares(squares)
    red_squares = []
    green_squares = []
    blue_squeares = []
    for shape in squares:
        shape_height, shape_wedth, shape_x_mid, shape_y_mid = get_square_params(shape)
        if not level3:
            if shape_height> 35 and shape_height < 65 and shape_wedth> 35 and shape_height<65: 
                background_color = get_uniqie_background_color(img,shape)
                if not background_color == 0:
                    if img[shape_y_mid][shape_x_mid][2] == background_color:
                        red_squares.append(shape)
                    else:
                        blue_squeares.append(shape)
            else:
                green_squares.append(shape)
        else:
            # print shape
            # print"shape_height: {}, shape_wedth: {}, shape_x_mid: {}, shape_y_mid: {}".format(shape_height, shape_wedth, shape_x_mid, shape_y_mid)
                
            if shape_wedth> 50 and shape_height<85: 
                background_color = img[320][100][2]
                if not background_color == 0:
                    if img[shape_y_mid][shape_x_mid][2] == background_color:
                        red_squares.append(shape)
                    else:
                        blue_squeares.append(shape)
            else:
                green_squares.append(shape)
            
    return red_squares, blue_squeares, green_squares

def get_background_color(filename):
    img = cv2.imread(filename)
    background_color = img[200][200][2]
    return background_color

# def get_blue_squares(filename):
#     img = cv2.imread(filename)
#     squares = find_squares(img)
#     background_color = img[200][200][2]
#     squares = get_unique_squares(squares)
#     red_squares = []
#     green_squares = []
#     blue_squeares = []
#     for shape in squares:
#         shape_height, shape_wedth, shape_x_mid, shape_y_mid = get_square_params(shape)
#         if shape_height> 40 and shape_height < 60 and shape_wedth> 40 and shape_height<60: 
#             if img[shape_y_mid][shape_x_mid][2] == background_color:
#                 red_squares.append(shape)
#             else:
#                 blue_squeares.append(shape)
#         else:
#             green_squares.append(shape)
#     return blue_squeares

def get_square_params(square):
    # print "getting square params + {}".format(square)
    shape_height = abs(square[0][0]- square[2][0])
    shape_wedth = abs(square[0][1]- square[2][1]) 
    shape_x_mid = (square[0][0] + square[2][0])/2 
    shape_y_mid = (square[0][1] + square[2][1])/2
    return shape_height, shape_wedth, shape_x_mid, shape_y_mid

if __name__ == '__main__':
    from glob import glob
    for fn in glob('*.png'):
        img = cv2.imread(fn)
        # # img = cv2.imread(fn, cv2.IMREAD_GRAYSCALE);  
        # # equ = cv2.equalizeHist(img)
        # squares = find_squares(img)
        # print fn
        # print squares
        # background_color = img[200][200][2]
        # i = 0
        # squares = get_unique_squares(squares)
        red_squares, blue_squeares, green_squares = get_red_and_blue_squares(fn,level3=True)
        # red_squares = []
        # green_squares = []
        # blue_squeares = []
        # for shape in squares:
        #     print("shape {}: {} {} {} {}, size: {}:{}".format(i, shape[0],shape[1],shape[2],shape[3], shape[0][0]- shape[2][0],shape[0][1]- shape[2][1]))
        #     i+=1
        #     # if (shape[0][0]>280 and shape[0][0]<300) or (shape[1][0]>280 and shape[1][0]<300) or (shape[2][0]>280 and shape[2][0]<300) or (shape[3][0]>280 and shape[3][0]<300) or (shape[0][1]>280 and shape[0][1]<300) or (shape[1][1]>280 and shape[1][1]<300)or (shape[2][1]>280 and shape[1][1]<300) or (shape[3][1]>280 and shape[1][1]<300):
        #     shape_height, shape_wedth, shape_x_mid, shape_y_mid = get_square_params(shape) 
        #     if shape_height> 40 and shape_height < 60 and shape_wedth> 40 and shape_height<60: 
        #         background_color = get_uniqie_background_color(img,shape)
        #         if img[shape_y_mid][shape_x_mid][2] == background_color:
        #             red_squares.append(shape)
        #         else:
        #             blue_squeares.append(shape)
        #     else:
        #         green_squares.append(shape)

            #[296 124] [341 125] [340 170] [295 169]


        cv2.drawContours( img, red_squares, -1, (0, 0, 255), 3 )
        cv2.drawContours( img, green_squares, -1, (0, 255, 0), 3 )
        cv2.drawContours( img, blue_squeares, -1, (255, 0, 0), 3 )
        # cv2.drawContours( img, squares, -1, (0, 255, 0), 3 )
        cv2.imshow('squares', img)
        ch = cv2.waitKey()
        if ch == 27:
            break
    cv2.destroyAllWindows()