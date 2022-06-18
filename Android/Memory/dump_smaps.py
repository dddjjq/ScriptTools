# 根据smaps文件读取进程占用的内存，并将大于[threshold]的占用都罗列出来，便于分析到底是哪个模块占用内存过多
# 目前只有Code模块
# 需要root权限

# python -u "f:\parse_smaps.py" temp.log

import os
import sys
import re
import subprocess

# 可以配置的内容
# smaps_temp指的是smaps文件
# package_name remote_name代表包名
# threshold代表最小统计大小
smaps_temp = r"F:\smaps.txt"
package_name = "com.tencent.mm"
remote_name = package_name + ":remote"
threshold = 1000

ps_cmd = "adb shell ps -A | grep " + package_name

# android.os.Debug getSummaryCode -> android_os_Debug android_os_Debug_getMemInfo
# getOtherPrivate(OTHER_SO)
#   + getOtherPrivate(OTHER_JAR)
#   + getOtherPrivate(OTHER_APK)
#   + getOtherPrivate(OTHER_TTF)
#   + getOtherPrivate(OTHER_DEX)
#   + getOtherPrivate(OTHER_OAT)
#   + getOtherPrivate(OTHER_DALVIK_OTHER_ZYGOTE_CODE_CACHE)
#   + getOtherPrivate(OTHER_DALVIK_OTHER_APP_CODE_CACHE);
end_list = [
    ".so",
    ".jar",
    ".apk",
    ".ttf",
    ".odex",
    ".vdex",
    ".oat",
    ".art",".art]",
]

start_list = [
    "/memfd:jit-cache",
    "[anon:dalvik-jit-code-cache",
    "[anon:dalvik-data-code-cache",
    "/dev/ashmem/jit-zygote-cache",
    "/memfd:jit-zygote-cache",
    ".dex"
]

save_file = None

def get_pid():
    res = exec_command(ps_cmd)
    lines = res.split('\n')
    for line in lines:
        if (remote_name not in line) and (package_name in line):
            pid = re.split(r"[ ]+", line)[1]
            return pid

def exec_command(command):
    try:
        commands = command.split(" ")
        out_bytes = subprocess.check_output(commands)
        out_text = out_bytes.decode('utf-8')
        return out_text
    except subprocess.CalledProcessError as e:
        out_bytes = e.output       # Output generated before error
        code      = e.returncode   # Return code

def parse():
    pid = get_pid()
    print(pid)
    global save_file
    save_file = get_path()
    if save_file is not None:
        save_file = open(save_file,"r+")
    save_info("pid is " + str(pid) + "\n")
    smaps = exec_command("adb shell cat /proc/" + pid + "/smaps")
    write_origin_smaps(smaps)
    smaps = smaps.split("\n")
    parse_code(smaps)

def write_origin_smaps(data):
    fd = os.open(smaps_temp, os.O_RDWR|os.O_CREAT)
    os.write(fd, data.encode())

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

# android_os_Debug.cpp [load_maps]
def parse_code(lines):
    count = 0
    total = 0
    pending_line = None
    for line in lines:
        if count <= 0:
            for filter in end_list:
                if line.strip().endswith(filter):
                    count = 2
                    pending_line = line
            for start in start_list:
                if start in line:
                    count = 2
                    pending_line = line
        if count > 0 and (line.startswith("Private_Clean") or line.startswith("Private_Dirty")):
            value = get_value(line)
            if int(value) > threshold and pending_line is not None:
                save_info(pending_line)
                save_info(line)
                pass
            total = total + int(value)
            count = count - 1
            if count == 0:
                pending_line = None
    save_info("total code is " + str(total))
    if save_file is not None:
        save_file.close()

def save_info(line):
    print(line)
    if save_file is not None:
        save_file.writelines(line)

def get_value(line):
    return re.split(r"[ ]+", line)[1]

if __name__ == "__main__":
    parse()