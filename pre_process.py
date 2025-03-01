import json
import zipfile
from collections import Counter

import jieba
from tqdm import tqdm

from config import *
from utils import ensure_folder

#zip文件打开， 读取图像数据和caption数据
def extract(folder):
    filename = '{}.zip'.format(folder)
    print('Extracting {}...'.format(filename))
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('data')


def create_input_files():
    json_path = train_annotations_filename

    # Read JSON
    with open(json_path, 'r') as j:
        samples = json.load(j)

    # Read image paths and captions for each image
    word_freq = Counter()

    for sample in tqdm(samples):
        caption = sample['caption']
        for c in caption:
            seg_list = jieba.cut(c, cut_all=True)
            # Update word frequency
            #单词出现的次数
            word_freq.update(seg_list)
    with open('./txt/word_freq.txt','w',encoding='utf8') as f:
        print(word_freq,file=f)

    # Create word map ： 单词
    words = [w for w in word_freq.keys() if word_freq[w] > min_word_freq]
    word_map = {k: v + 1 for v, k in enumerate(words)}
    word_map['<unk>'] = len(word_map) + 1
    word_map['<start>'] = len(word_map) + 1
    word_map['<end>'] = len(word_map) + 1
    word_map['<pad>'] = 0
    with open('./txt/word_map.txt','w',encoding='utf8') as f:
        print(word_map,file=f)
    # print(word_map)
    # print(len(word_map))
    # print(words[:10])

    # Save word map to a JSON
    with open(os.path.join(data_folder, 'WORDMAP.json'), 'w') as j:
        json.dump(word_map, j)


if __name__ == '__main__':
    # parameters
    ensure_folder('data')#创建一个data文件夹

    if not os.path.isdir(train_image_folder):
        extract(train_folder)

    if not os.path.isdir(valid_image_folder):
        extract(valid_folder)

    if not os.path.isdir(test_a_image_folder):
        extract(test_a_folder)

    if not os.path.isdir(test_b_image_folder):
        extract(test_b_folder)

    create_input_files()
