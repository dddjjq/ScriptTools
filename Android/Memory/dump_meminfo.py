# 持续dump内存 并保存到文件中
# python -u "f:\dump_meminfo.py" test.log 
# 支持绝对路径和相对路径
import os
import subprocess
import time
import re
import sys

package_name = "com.tencent.mm"
command = "adb shell dumpsys meminfo " + package_name

# -t total
# -g graphics
# -j Java heap
# -n Native heap
# -c Code
dump_type = "-t"

save_file = None

def dump():
    global save_file
    save_file = get_path()
    if save_file is not None:
        save_file = open(save_file,"r+")
    update_type()
    write_line("time is : " + str(time.time()))
    count = 0
    while count < 50:
        content = exec_command()
        total = get_total(content,"-t")
        graphics = get_total(content,"-g")
        java = get_total(content,"-j")
        native = get_total(content,"-n")
        code = get_total(content,"-c")
        res = "Total  :  " + total + "  Graphics  :  " + graphics + "  Java  :  " + java + "  Native  :  " + native + "  Code  :  " + code
        write_line(res)
        time.sleep(1)
        count += 1


def write_line(content):
    if save_file is not None:
        save_file.writelines(content + "\n")
    print(content)

def get_path():
    if (len(sys.argv) <2):
        return
    file = sys.argv[1]
    if os.path.isabs(file):
        if not os.path.exists(file):
            fd = os.open(file, os.O_RDWR|os.O_CREAT)
            os.close(fd)
        return file
    cur = os.getcwd()
    res = cur + os.path.sep + file
    if not os.path.exists(res):
        fd = os.open(res, os.O_RDWR|os.O_CREAT)
        os.close(fd)
    return res

def update_type():
    if len(sys.argv) > 2:
        global dump_type
        type = sys.argv[2]
        dump_type = type


def save(result,file):
    pass

def exec_command():
    try:
        commands = command.split(" ")
        out_bytes = subprocess.check_output(commands)
        out_text = out_bytes.decode('utf-8')
        return out_text
    except subprocess.CalledProcessError as e:
        out_bytes = e.output       # Output generated before error
        code      = e.returncode   # Return code

def get_total(content,type):
    lines = content.split('\n')
    for line in lines:
        key_word = "TOTAL"
        if type == '-t':
            key_word = "TOTAL"
        elif type == '-g':
            key_word = "Graphics:"
        elif type == '-j':
            key_word = "Java Heap:"
        elif type == '-n':
            key_word = "Native Heap:"
        elif type == '-c':
            key_word = "Code:"
        if key_word in line:
            chars = line.split(key_word)
            chars = re.split(r"[ ]+", chars[1])
            return chars[1]

dump()