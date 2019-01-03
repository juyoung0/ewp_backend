import numpy as np
import re


# Functions for KEWP data analysis
# Made by Haedong Jeong
# SAI LAB. UNIST

def tag_prepro(tagfile):
    f = open(tagfile)
    taglist = []
    for i, temp in enumerate(f):
        split_temp = re.split(r'[;.,\s]\s*', temp)[:-1]
        out = 'KEWP_' + '_'.join(split_temp)
        taglist.append(out)
    f.close()
    return taglist


def daq(db, taglist):
    list_val = []
    data_list = []
    temp_tag = []

    for i in range(0, len(taglist)):
        tag = db[taglist[i]]
        for record in tag.find():
            if np.isnan(record['val']):
                list_val = []
                break
            else:
                list_val.append(record['val'])

        if list_val != []:
            temp_tag.append(taglist[i])
            temp_val = np.array(list_val)
            data_list.append(temp_val)

        list_val = []
    return np.array(data_list).T, temp_tag


def normalization(data):
    out = {}
    for i, name in enumerate(data):
        _buffer = []
        mean = np.mean(data[name], axis=0)
        for j in range(0, data[name].shape[-1]):
            temp = data[name][:, j] - mean[j]
            normalized_temp = (temp - np.min(temp)) / (np.max(temp) - np.min(temp)) * 2 - 1
            _buffer.append(normalized_temp)
        out[name] = np.array(_buffer).T
    return out