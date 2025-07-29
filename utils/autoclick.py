import sys
from time import sleep
import pyautogui as py
import cv2
import win32gui
import win32con
def get_xy(img_model_path,match_threshold=0.1,check_exist=False):
    """
    用来判定游戏画面的点击坐标
    :param img_model_path:用来检测的图片
    :return:以元组形式返回检测到的区域中心的坐标
    """
    # 将图片截图并且保存
    py.screenshot().save("./pic/screenshot.png")
    # 待读取图像
    img = cv2.imread("./pic/screenshot.png")
    # 图像模板
    img_terminal = cv2.imread(img_model_path)
    # 读取模板的高度宽度
    height, width = img_terminal.shape[:2]
    # 使用matchTemplate进行模板匹配（标准平方差匹配）
    result = cv2.matchTemplate(img, img_terminal, cv2.TM_SQDIFF_NORMED)
    # 解析出匹配区域的最小值和其位置（左上角）
    min_val,temp1,upper_left= cv2.minMaxLoc(result)[:3]
    if min_val>match_threshold:
        if not check_exist:
            print(f"Warning: 与模板照片：{img_model_path}匹配度太低, min_val={min_val}")
        return None
    # 计算出匹配区域右下角图标（左上角坐标加上模板的长宽即可得到）
    lower_right = (upper_left[0] + width, upper_left[1] + height)
    # 计算中心坐标并将其返回
    avg = (int((upper_left[0] + lower_right[0]) / 2), int((upper_left[1] + lower_right[1]) / 2))
    return avg


def auto_click(var_avg):
    """
    输入一个元组，自动点击
    :param var_avg: 坐标元组 
    :return: None
    """
    if var_avg==None:
        print("坐标为空，无法点击！\n结束运行！")
        sys.exit(0)
    py.click(var_avg[0], var_avg[1], button='left')
    sleep(1)


def routine(img_model_path, name,hint=True):
    avg = get_xy(img_model_path)
    if not hint:
        if avg==None:
            print(f"未能找到{name}的坐标,结束运行")
            sys.exit(0)
        auto_click(avg)
        return
    if avg:
        print(f"点击{name}")
        auto_click(avg)
    else:
        print(f"未能找到{name}的坐标,结束运行")
        sys.exit(0)


def over_jb(tl=0):
    """"
    结束运行并退出副本
    """
    if tl==0:
        routine("./pic/back.png", "取消")
    routine("./pic/over.png", "退出战斗")
    sleep(3)
    py.press('esc')
    print("结束程序运行")
    sys.exit(0)

def qh_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        print(f"找不到窗口: {window_title}")
        sys.exit(0)

    print(f"切换{window_title}")
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 恢复窗口（如果最小化）
    win32gui.SetForegroundWindow(hwnd)  # 设置为前台窗口
    sleep(0.5)

def start_fb():
    qh_window("崩坏：星穹铁道")
    xy_began=get_xy("./pic/begantz.png")
    auto_click(xy_began)
    print("进入副本了！")

def check_doen():
    """"
    持续监测，直到本次刷取结束弹出结算页面；然后点击再来一次开始下一次
    return : 返回再来一次的坐标
    """
    xy_agan = None
    while xy_agan == None:
        xy_agan = get_xy("./pic/agan.png", check_exist=True)
        sleep(2)
    auto_click(xy_agan)
    return xy_agan

def use_tly(per_count,xy_tly):
    """
    使用指定数量的体力药
    per_count : 每次使用的数量
    xy_tly : 体力药的坐标
    """
    print(f"正在使用{per_count}瓶体力药")
    if xy_tly==None:
        print("已经没有体力药了，结束运行！")
        over_jb()
    auto_click(xy_tly)
    routine("./pic/yes.png","确认",hint=False)
    xy_jia=get_xy("./pic/+.png")
    for x in range(1,per_count):
        auto_click(xy_jia)
    routine("./pic/yes.png", "确认",hint=False)
    py.click(button='left')
    print(f"使用了{per_count}瓶体力！")

def xh_tly(tly_count,per_count):
    count=0
    for i in range(0,tly_count):
        xy_xq=None
        while xy_xq==None:
            xy_agan=check_doen()
            count+=1
            xy_xq=get_xy("./pic/xq.png",check_exist=True)
        use_tly(per_count,xy_tly=get_xy("./pic/tly.png",check_exist=True))
        auto_click(xy_agan)
    print(f"完成任务，已使用{tly_count}次体力药")
    xy_xq=None
    while xy_xq==None:
        check_doen()
        count+=1
        xy_xq = get_xy("./pic/xq.png", check_exist=True)
    count-=tly_count
    print(f"已刷取{count}次")
    over_jb()

def xh_common(count):
    for i in range(0, count):
        print(f"正在进行第{i+1}次")
        check_doen()
        xy_xq = get_xy("./pic/xq.png", check_exist=True)
        if xy_xq:
            print("已无足够的体力！")
            over_jb()
    print(f"完成任务，已刷取{count}次副本")
    over_jb(tl=1)

def xhtz(count,per_count):
    print("开启自动作战")
    py.press('v')
    print("开始挂机刷本")
    if per_count:
        xh_tly(count,per_count)
    else:
        xh_common(count)

def fjn(x):
    print("开始放技能")
    py.keyDown('w')
    sleep(1.8)
    py.keyUp('w')
    for i in str(x)[:5]:
        py.press(i)
        sleep(1)
        py.press('e')
        sleep(2)
    py.click()

def richang(count,per_count):
    start_fb()
    sleep(6)
    xhtz(count,per_count)

def neiqvan(count,x,per_count):
    start_fb()
    sleep(5)
    fjn(x)
    sleep(6)
    xhtz(count,per_count)

#测试代码
if __name__ == '__main__':
    for i in range(0,1):
        print(i)
