import os
import json

def log_item(item):
    print(item)

def print_directory(path, tabs=0):
    log_item_name = ""
    size_str = ""
    log_item("Files on filesystem:")
    log_item("====================")
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            size_str = str(filesize) + " by"
        elif filesize < 1000000:
            size_str = "%0.1f KB" % (filesize / 1000)
        else:
            size_str = "%0.1f MB" % (filesize / 1000000)

        log_item_name = ""
        for _ in range(tabs):
            log_item_name += "   "
        log_item_name += file
        if isdir:
            log_item_name += "/"
        log_item('{0:<40} Size: {1:>10}'.format(log_item_name, size_str))

        if isdir:
            print_directory(path + "/" + file, tabs + 1)

def return_directory(prefix='', path='.', fileType='', remove_ext=True, replace_ext_with=''):
    file_list = []
    
    for file in os.listdir(path):
        if "._" in file:
            continue
        if fileType and fileType not in file:
            continue


        if remove_ext and file.endswith(fileType):
            name = file[:-len(fileType)]
        elif replace_ext_with and file.endswith(fileType):
            name = file[:-len(fileType)] + replace_ext_with
        else:
            name = file
        file_list.append(prefix + name)

    def natural_key(s):
        key = []
        num = ''
        for c in s:
            if c.isdigit():
                num += c
            else:
                if num:
                    key.append(int(num))
                    num = ''
                key.append(c.lower())
        if num:
            key.append(int(num))
        return key

    file_list.sort(key=natural_key)
    return file_list
 
def write_file_lines(file_name, lines):
    with open(file_name, "w") as f:
        for line in lines:
            f.write(line + "\n")

def read_file_lines(file_name):
    with open(file_name, "r") as f:
        lines = f.readlines()
        output_lines = [] 
        for line in lines:
            output_lines.append(line.strip())
        return output_lines
    
def write_file_line(file_name, line):
    with open(file_name, "w") as f:
        f.write(line + "\n")

def read_file_line(file_name):
    with open(file_name, "r") as f:
        line = f.read()
        output_line=line.strip()
        return output_line
    
def json_stringify(python_dictionary):
    json_string = json.dumps(python_dictionary)
    return json_string

def json_parse(my_object):
    python_dictionary = json.loads(my_object)
    return python_dictionary

def write_json_file(file_name, python_dictionary):
    json_string=json_stringify(python_dictionary)
    write_file_line(file_name, json_string)
    
def read_json_file(file_name):
    json_string=read_file_line(file_name)
    python_dictionary=json_parse(json_string)
    return python_dictionary

def strip_path_and_extension(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    return file_name

