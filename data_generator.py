# encoding=utf-8
import json

import jieba
import numpy as np
from scipy.misc import imread, imresize
from torch.utils.data import Dataset

from config import *


def encode_caption(word_map, c):
    return [word_map['<start>']] + [word_map.get(word, word_map['<unk>']) for word in c] + [
        word_map['<end>']] + [word_map['<pad>']] * (max_len - len(c))


class CaptionDataset(Dataset):
    """
    A PyTorch Dataset class to be used in a PyTorch DataLoader to create batches.
    """

    def __init__(self, split, transform=None):
        """
        :param split: split, one of 'TRAIN', 'VAL', or 'TEST'
        :param transform: image transform pipeline
        """
        self.split = split
        assert self.split in {'train', 'valid'}

        if split == 'train':
            json_path = train_annotations_filename
            self.image_folder = train_image_folder
        else:
            json_path = valid_annotations_filename
            self.image_folder = valid_image_folder

        # Read JSON
        with open(json_path, 'r') as j:
            self.samples = json.load(j)
        # with open('./txt/samples.txt','w',encoding='utf8') as f:
        #     print(self.samples,file=f)

        # Read wordmap
        with open(os.path.join(data_folder, 'WORDMAP.json'), 'r') as j:
            self.word_map = json.load(j)

        # PyTorch transformation pipeline for the image (normalizing, etc.)
        self.transform = transform

        # Total number of datapoints #图像的个数 × captions每个图像
        self.dataset_size = len(self.samples * captions_per_image)

    def __getitem__(self, i):
        # Remember, the Nth caption corresponds to the (N // captions_per_image)th image
        sample = self.samples[i // captions_per_image]
        # print('First sample--------------')
        # print(sample)
        # with open('./txt/sample_.txt','w',encoding='utf8') as f:
        #     print(sample,file=f)

        path = os.path.join(self.image_folder, sample['image_id'])
        # print(path)
        # print('First sample over=================')

        #path = train_image_files
        # Read images
        img = imread(path)
        if len(img.shape) == 2:
            img = img[:, :, np.newaxis]
            img = np.concatenate([img, img, img], axis=2)
        img = imresize(img, (256, 256))
        img = img.transpose(2, 0, 1)
        assert img.shape == (3, 256, 256)
        assert np.max(img) <= 255
        img = torch.FloatTensor(img / 255.)
        if self.transform is not None:
            img = self.transform(img)

        # Sample captions
        captions = sample['caption']
        with open('./txt/captions.txt','w',encoding='utf8') as f:
            print(captions,file=f)
        # Sanity check
        assert len(captions) == captions_per_image
        c = captions[i % captions_per_image]
        with open('./txt/captions_c.txt','w',encoding='utf8') as f:
            print(c,file=f)
        c = list(jieba.cut(c))
        with open('./txt/c.txt','w',encoding='utf8') as f:
            print(c,file=f)
        # Encode captions
        enc_c = encode_caption(self.word_map, c)
        with open('./txt/enc_c.txt','w',encoding='utf8') as f:
            print(enc_c,file=f)
        print("***********ENCODE_CAPTION**********")
        caption = torch.LongTensor(enc_c)
        print("LONGTENSOR_CAPTION")
        print(caption)
        caplen = torch.LongTensor([len(c) + 2])
        print("CAPLEN")
        print(caplen)
        print("-----------OVER0-00000000000000")
        if self.split is 'train':
            return img, caption, caplen

        else:
            # For validation of testing, also return all 'captions_per_image' captions to find BLEU-4 score
            all_captions = torch.LongTensor([encode_caption(self.word_map, list(jieba.cut(c))) for c in captions])
            return img, caption, caplen, all_captions

    def __len__(self):
        return self.dataset_size
