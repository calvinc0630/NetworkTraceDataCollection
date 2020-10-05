import json
import os
import pathlib
import time

def parse_config(path):
    with open(path) as json_data_file:
        data = json.load(json_data_file)
    return data


def make_public_dir(dir_path):
    # if not exist, create,
    # Always change to 777
    if not os.path.exists(dir_path):
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    os.system("sudo chmod -R 777 {}".format(dir_path))


def remake_public_dir(dir_path):
    if os.path.exists(dir_path):
        os.system("sudo rm -rf {}".format(dir_path))
    make_public_dir(dir_path)


def init_dir():
    make_public_dir("result")
    make_public_dir("trace")



def dict_key_to_ordered_list(input_dict):
    newlist = list()
    for i in input_dict.keys():
        newlist.append(i)
    newlist.sort()
    return newlist


def fail_and_wait(fail_reason, timeout = 60):
    print(fail_reason)
    time.sleep(timeout)


def init_apache_dir():
    pass
