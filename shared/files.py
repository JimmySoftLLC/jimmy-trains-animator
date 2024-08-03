import os
import json

def log_item(item):
    print(item)

def print_directory(p, t=0):
    itm_nme = ""
    str_s = ""
    log_item("Files on filesystem:")
    log_item("====================")
    for f in os.listdir(p):
        sts = os.stat(p + "/" + f)
        f_sz = sts[6]
        is_dir = sts[0] & 0x4000

        if f_sz < 1000:
            str_s = str(f_sz) + " by"
        elif f_sz < 1000000:
            str_s = "%0.1f KB" % (f_sz / 1000)
        else:
            str_s = "%0.1f MB" % (f_sz / 1000000)

        itm_nme = ""
        for _ in range(t):
            itm_nme += "   "
        itm_nme += f
        if is_dir:
            itm_nme += "/"
        log_item('{0:<40} Size: {1:>10}'.format(itm_nme, str_s))

        # recursively files.log_item directory contents
        if is_dir:
            print_directory(p + "/" + f, t + 1)

def return_directory(pfx, p, type):
    file_list = []
    for file in os.listdir(p):  
        if "._" not in file and type in file:
            file_name = pfx + file.replace(type, '')
            file_list.append(file_name)
    file_list.sort()
    return file_list
 
def write_file_lines(f, ls):
    with open(f, "w") as f:
        for l in ls:
            f.write(l + "\n")

def read_file_lines(f):
    with open(f, "r") as f:
        ls = f.readlines()
        o_ls = [] 
        for l in ls:
            o_ls.append(l.strip())
        return o_ls
    
def write_file_line(f, l):
    with open(f, "w") as f:
        f.write(l + "\n")

def read_file_line(f):
    with open(f, "r") as f:
        l = f.read()
        o_l=l.strip()
        return o_l
    
def json_stringify(dict):
    json_s = json_s.dumps(dict)
    return json_s

def json_parse(obj):
    dict = json.loads(obj)
    return dict

def write_json_file(f, dict):
    json_s=json_stringify(dict)
    write_file_line(f, json_s)
    
def read_json_file(f):
    json_s=read_file_line(f)
    dict=json_parse(json_s)
    return dict
