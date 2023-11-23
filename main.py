import os.path
import subprocess
import time
import random
import sys
import _thread

def get_xmax_and_ymax():
    order = 'adb shell getevent -p'  # 获取连接设备
    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    data = str(pi.stdout.read())
    l = data.find('0035', 0)
    l = data.find('max ', l)
    l += 4
    r = l
    while data[r] != ',':
        r += 1
    xmax = int(data[l:r])
    l = data.find('0036')
    l = data.find('max ', l)
    l += 4
    r = l
    while data[r] != ',':
        r += 1
    ymax = int(data[l:r])
    return xmax, ymax


def get_xsize_and_ysize():
    order = 'adb shell wm size'  # 获取连接设备
    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    data = str(pi.stdout.read())
    l, n = data.find(': '), len(data)
    l += 2
    r = l
    while r < n and data[r] != 'x':
        r += 1
    xsize = int(data[l:r])
    l = r + 1
    r = l
    while r < n and data[r].isnumeric():
        r += 1
    ysize = int(data[l:r])
    return xsize, ysize


def get_package_name():
    order = 'adb shell dumpsys activity activities'  # 获取连接设备
    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    data = str(pi.stdout.read())
    r = data.find('mResumedActivity')
    r = data.find('/', r)
    l = r
    while data[l] != ' ':
        l -= 1
    l += 1
    package_name = data[l:r]
    return package_name


def get_phy_x_and_y():
    xmax, ymax = get_xmax_and_ymax()
    xsize, ysize = get_xsize_and_ysize()

    order = 'adb shell getevent'

    pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)

    x, y = 0, 0
    phy_x, phy_y = 0, 0
    for line in iter(pi.stdout.readline, 'b'):
        pass
        data = str(line)
        if data.find(' 0035 ') != -1:
            l = data.find(' 0035 ')
            l += 6
            r = l
            while data[r] != '\\':
                # print('r: ', data[r])
                r += 1
            x = int('0x' + data[l:r], 16)
        if data.find(' 0036 ') != -1:
            l = data.find(' 0036 ')
            l += 6
            r = l
            while data[r] != '\\':
                r += 1
            y = int('0x' + data[l:r], 16)

            phy_x = (x - 0) * xsize / (xmax - 0)
            phy_y = (y - 0) * ysize / (ymax - 0)
            pi.kill()
            break
    return phy_x, phy_y



def get_random_str():
    str = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], 10))
    return str


def get_screen_data(file_name: str, path: str):
    # 获取截屏
    order = 'adb shell screencap -p  > {}.png'.format(os.path.join(path, file_name))
    subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)

    # # 获取xml
    # order = 'adb shell uiautomator dump /sdcard/{}.xml'.format(file_name)
    # subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    # print(order)
    # while True:
    #     order = 'adb shell ls /sdcard/{}.xml'.format(file_name)
    #     pi = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     data = str(pi.stdout.read())
    #     if data.find('/sdcard/{}.xml'.format(file_name)) != -1:
    #         pi.stdout.close()
    #         pi.stderr.close()
    #         break
    #
    # order = 'adb pull /sdcard/{}.xml {}'.format(file_name, path)
    # subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    # order = 'adb shell rm /sdcard/{}.xml'.format(file_name)
    # subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)


'''
1、获取当前的app packagename
2、点击1：获取当前屏幕信息
3、点击2：获取当前手指点击的坐标
4、循环往复
5、点击0结束测试，后台总结信息
6、后台总结的信息：
    各个界面数据：截屏+xml，以10为随机字符命名
    图数据： 每行的数据结构为： 界面A 界面B 点击的坐标
'''
if __name__ == '__main__':
    package_name = get_package_name()
    millis = int(round(time.time() * 1000))

    data_path = os.path.join(os.getcwd(), 'data', package_name + "_" + str(millis))
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    print("请打开需要测试的app，并处理好登录之类的操作后，完成以下步骤：")

    guide = "\033[33m点击1：获取当前屏幕信息\033[0m\n" \
            "\033[33m点击2：获取当前手指点击的坐标\033[0m\n" \
            "\033[33m点击0：结束测试，等待后台总结好数据后，再做下一步操作\033[0m\n"

    ui_names = []
    ui_relations = []
    has_relation = False
    phy_x, phy_y = 0.0, 0.0
    while True:
        print(guide)
        intruction = int(input())
        print('intruction: ', intruction)
        if intruction == 1:
            ui_name = get_random_str()
            ui_names.append(ui_name)
            get_screen_data(ui_name, data_path)
            if has_relation:
                has_relation = False
                ui_relation = [ui_names[-1], ui_names[-2], str(phy_x), str(phy_y)]
                ui_relations.append(ui_relation)
            pass
        elif intruction == 2:
            phy_x, phy_y = get_phy_x_and_y()
            has_relation = True
            pass
        elif intruction == 0:
            print('\033[31m停止测试，请等待程序总结好数据后再做下一步操作！\033[0m')
            with open(os.path.join(data_path, 'ui_relation.txt'), 'w') as f:
                for ui_relation in ui_relations:
                    line = ' '.join(ui_relation)
                    f.write(line + '\n')
            break
        else:
            print("\033[31m不明指令！\033[0m")

    print('结束测试！')
