import requests
import numpy as np
import cv2
from colors import colors_earth
from io import BytesIO
from PIL import Image, ImageChops
from time import sleep

def get_chunk(x, y):
    y = ((65536 // 2) + int(y)) // 256
    x = ((65536 // 2) + int(x)) // 256
    # get data from the server
    data = requests.get(f'https://pixelplanet.fun/chunks/0/{x}/{y}.bmp').content
    # construct a numpy array from it
    arr = np.zeros((256, 256), np.uint8)
    if len(data) != 65536:
        return arr
    for i in range(65536):
        c = data[i]
        # protected pixels are shifted up by 128
        if c >= 128:
            c = c - 128
        arr[i // 256, i % 256] = c
    return arr

def get_chunks(xs, ys, w, h):
    xs, ys, w, h = int(xs), int(ys), int(w), int(h)
    c_start_y = ((65536 // 2) + ys) // 256
    c_start_x = ((65536 // 2) + xs) // 256
    c_end_y = ((65536 // 2) + ys + h) // 256
    c_end_x = ((65536 // 2) + xs + w) // 256
    c_occupied_y = c_end_y - c_start_y + 1
    c_occupied_x = c_end_x - c_start_x + 1
    print(c_occupied_x, c_occupied_y)
    # the final image
    data = np.zeros((0, c_occupied_x * 256), np.uint8)
    # go through the chunks
    for y in range(c_occupied_y):
        # the row
        row = np.zeros((256, 0), np.uint8)
        for x in range(c_occupied_x):
            # append the chunk to the row
            row = np.concatenate((row, get_chunk((int(x) * 256) + int(xs), (int(y) * 256) + int(ys))), axis=1)
        # append the row to the image
        data = np.concatenate((data, row), axis=0)
    img = np.zeros((256 * c_occupied_y, 256 * c_occupied_x, 3), np.uint8)
    for y in range(256 * c_occupied_y):
        for x in range(256 * c_occupied_x):
            r, g, b = colors_earth[data[y, x]]
            img[y, x] = (b, g, r)
    h, w, rd = img.shape
    cv2.imwrite('multiplos.png', img)
    return h, w, c_occupied_x, c_occupied_y

def differ(xs, ys, img):
    c_start_x = ((65536 // 2) + int(xs)) // 256
    c_start_y = ((65536 // 2) + int(ys)) // 256
    start_in_d_x = int(xs) + ((65536 // 2) - (int(c_start_x) * 256))
    start_in_d_y = int(ys) + ((65536 // 2) - (int(c_start_y) * 256))
    #print(start_in_d_x)
    #print(start_in_d_y)
    data_im = Image.open("multiplos.png")
    #print(img.size[0], img.size[1])
    kek = data_im.crop((start_in_d_x, start_in_d_y, start_in_d_x + img.size[0], start_in_d_y + img.size[1])).convert('RGBA')

    datas3 = img.getdata()
    datas4 = kek.getdata()

    toTransparent = []
    index = 0
    print(img.size)
    print(datas3)
    for item in datas3:
        if item[3] == 0:
            toTransparent.append((255, 255, 255, 17))
            index += 1
        else:
            toTransparent.append((datas4[index][0], datas4[index][1], datas4[index][2]))
            index += 1

    kek.putdata(toTransparent)

    diff = ImageChops.difference(img, kek)
    datas = diff.getdata()

    errors = 0
    non_transp = 0
    newData = []

    diff.save('b4.png')

    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0 and item[3] == 0:
            non_transp += 1
            newData.append((255, 255, 255, 0))
        elif item[3] == 17:
            newData.append((255, 255, 255, 0))
        else:
            non_transp += 1
            errors += 1
            newData.append((255, 0, 0, 255))

    diff.putdata(newData)

    diff.save('after.png')

    ungrayed = img.convert('LA')
    ungrayed.save('ungrayed.png')
    new_grayed = Image.open('ungrayed.png').convert('RGBA')
    new_grayed.paste(diff, (0,0), diff)
    return errors, non_transp, new_grayed

def render_chunk(x, y):
    data = get_chunk(x, y)
    img = np.zeros((256, 256, 3), np.uint8)
    colors = colors_earth
    # go through the data
    pixels = 0
    for y in range(256):
        for x in range(256):
            r, g, b = colors[data[y, x]]
            img[y, x] = (r, g, b)
    img = Image.fromarray(img)
    return img

def get_image_data(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert('RGBA')
    w, h = img.size
    return w, h

def get_image(url):
    response = requests.get(url, stream=True)
    img = Image.open(BytesIO(response.content)).convert('RGBA')
    return img