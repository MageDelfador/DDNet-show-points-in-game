import win32process
import win32con
import win32api
import ctypes
import win32gui
import time



hook_enable = False
hover_height = 0
print('悬停钩子辅助（测试）已启用，游戏中按E开启/关闭，按F提高悬停高度，按G降低高度')
def on_press(key):
    global hook_enable,hover_height
    try:
        if(key.char == 'e'):
            hook_enable = not hook_enable
        if(key.char == 'f'):
            hover_height = hover_height - 16
        if(key.char == 'g'):
            hover_height = hover_height + 16
    except:
        pass
def hover_hook():
    from pynput.keyboard import Key, Controller as c_keyboard
    from pynput.mouse import Button, Controller as c_mouse
    from pynput import keyboard
    global hook_enable,hover_height
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    keyboard = c_keyboard()
    mouse= c_mouse()

    PROCESS_ALL_ACCESS=(0x000F0000|0x00100000|0xFFF)
    window=win32gui.FindWindow(None,"DDNet Client")
    if window==0:
        print("游戏没有运行，请打开游戏")
        print("game not running")
        while window==0:
            window=win32gui.FindWindow(None,"DDNet Client")
            time.sleep(1)
    hid,pid=win32process.GetWindowThreadProcessId(window)
    phand=win32api.OpenProcess(PROCESS_ALL_ACCESS,False,pid)
    mydll = ctypes.windll.LoadLibrary("C:\\Windows\\System32\\kernel32.dll")
    module_handles = win32process.EnumProcessModules(phand)
    module_handle = module_handles[0]

    data = ctypes.c_long(0)
    #x_addr = module_handle + 0x3D3770
    y_addr = module_handle + 0x3D376C
    #hook_ptr = module_handle + 0x405100
    #mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(hook_ptr),ctypes.byref(data),3,None)
    #hook_addr = data.value
    #mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(hook_ptr+3),ctypes.byref(data),3,None)
    #hook_addr = (data.value << 24) + hook_addr + 0x35C

    hook_start_once = True
    ysumerr = 0
    press_time = 0
    press_time_clean = False
    while(1):
        if(hook_enable):
            if(hook_start_once):
                mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(y_addr),ctypes.byref(data),4,None)
                lasty = data.value
                hover_height = data.value
                ysumerr = 0
                hook_start_once = False
            yerr = data.value - hover_height
            ysumerr = ysumerr + yerr
            if(ysumerr > 500):
                ysumerr = 500
            if(ysumerr < -500):
                ysumerr = -500
            yd = data.value - lasty
            ys = ysumerr * 0.004
            ct = yerr * 0.25 + yd * 4 + ys
            if(ct > 0):
                mouse.press(Button.right)
                if(press_time_clean == False):
                    press_time_clean = True
                    press_time = 0
            else:
                mouse.release(Button.right)
                press_time = 0
                press_time_clean = False
            if(press_time > 10):
                mouse.release(Button.right)
                press_time = 0;
            press_time = press_time + 1
            time.sleep(0.001)
            lasty = data.value
            mydll.ReadProcessMemory(int(phand),ctypes.c_void_p(y_addr),ctypes.byref(data),4,None)
        else:
            if(hook_start_once == False):
                hook_start_once = True
                mouse.release(Button.right)
            time.sleep(0.000001)
hover_hook()