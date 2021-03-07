import get_data
from PIL import Image
import os
import json
from datetime import date


def add_template(name, x, y, img, user):
    l=os.listdir('templates_folder')
    file_names = [y.split('_')[1] for y in l]
    print(file_names)
    print(l)
    if name in file_names:
        print('repeated')
        return 'repeated'
    else:
        img.save(f'templates_folder/_{name}_{str(x)}_{str(y)}_{user}_.png')

def find_template_data(name):
    l=os.listdir('templates_folder')
    file_names = [y.split('_')[1] for y in l]
    if name in file_names:
        index = file_names.index(name)
        x = [y.split('_')[2] for y in l][index]
        y = [y.split('_')[3] for y in l][index]
        id_ = [y.split('_')[4] for y in l][index]
    print(name, x, y, id_)

    return x, y, id_, f'{l[index]}'
