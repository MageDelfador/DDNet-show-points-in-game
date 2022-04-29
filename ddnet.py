import win32process
import win32con
import win32api
import ctypes
import win32gui

import urllib.parse
import urllib.request
import urllib.error

import string
import time
import _thread

thread_count = 4
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

lock=_thread.allocate_lock()
points={}
asm_addr=0x004D3D90
str_addr=0
blank_addr=0x006E20EB
str_dis=0x1158
def getpoints():
    while 1:
        lock.acquire()
        while lock.locked():
            sl=1
            for pname in points.keys():
                if points[pname] < -7:
                    points[pname]+=5
                    lock.release()
                    sl=0
                    response=None
                    try:
                        response = urllib.request.urlopen('https://ddnet.tw/players/'+urllib.parse.quote(pname)+'/',timeout = 10)
                    except urllib.error.HTTPError as e:
                        if e.code==404:
                            points[pname]=0
                        else:
                            points[pname]+=1-5
                        break
                    except:
                        points[pname]+=1-5
                        break
                    txt=response.read().decode('utf-8')
                    if(txt.find('Player not found')>=0):
                        points[pname]=0
                        break
                    tn=txt.find('<h2>Global')
                    if tn <0:
                        points[pname]+=1-5
                        break
                    tn=txt.find('with',tn)
                    if tn <0:
                        points[pname]+=1-5
                        break
                    tn+=5
                    sn=txt.find(' ',tn)
                    if sn <0:
                        points[pname]+=1-5
                        break
                    points[pname]=int(txt[tn:sn])
                    break
            if sl==1:
                time.sleep(1)

data = ctypes.c_long(0)
mydll.ReadProcessMemory(int(phand),asm_addr,ctypes.byref(data),2,None)
if data.value!=37008 and data.value!=19080:
    print('游戏已升级，当前版本不可使用，请使用steam更新游戏或前往github获取本程序更新')
    print("https://github.com/MageDelfador/DDNet-show-points-in-game")
    print('error:game file unmatch')
    while 1:
        time.sleep(1)
print("程序成功加载，游戏中按tab键查看所有玩家分数")
print("press TAB to view the scores of all players")
print("作者ID：410164263，如果你在游戏中遇到我，一定要带我恰分哦")
#不更新战队显示
data = ctypes.c_long(2425393296) #nop
mydll.WriteProcessMemory(int(phand),asm_addr,ctypes.byref(data),3,None)
asm_addr+=0x0C
mydll.WriteProcessMemory(int(phand),asm_addr,ctypes.byref(data),3,None)
asm_addr+=0x0C
mydll.WriteProcessMemory(int(phand),asm_addr,ctypes.byref(data),3,None)
asm_addr+=0x0A
mydll.WriteProcessMemory(int(phand),asm_addr,ctypes.byref(data),3,None)

asm_addr-=0x03
mydll.WriteProcessMemory(int(phand),asm_addr,ctypes.byref(data),3,None)
asm_addr-=0x04
data = ctypes.c_long(0x0020E33C)
mydll.WriteProcessMemory(int(phand),asm_addr,ctypes.byref(data),4,None)
asm_addr-=0x03
data = ctypes.c_long(0x001D8948)
mydll.WriteProcessMemory(int(phand),asm_addr,ctypes.byref(data),3,None)

wait_s=1
while str_addr == 0:
    data = ctypes.c_long(0)
    mydll.ReadProcessMemory(int(phand),blank_addr,ctypes.byref(data),4,None)
    if data.value > 0:
        str_addr = data.value + 0x30CF14 - 0x10
    time.sleep(1)
for i in range(0,thread_count):
    _thread.start_new_thread(getpoints,())
while 1:
    wait_s+=1
    if wait_s>5:
        wait_s=1
    for clientid in range(0,64):
        data = ctypes.c_long(0)
        mydll.ReadProcessMemory(int(phand),str_addr+str_dis*clientid,ctypes.byref(data),3,None)
        name=data.value.to_bytes(3, byteorder='little')
        if name[0]==0:
            continue
        for i in range(1,6):
            mydll.ReadProcessMemory(int(phand),str_addr+i*3+str_dis*clientid,ctypes.byref(data),3,None)
            name+=data.value.to_bytes(3, byteorder='little')
        for i in range(0,18):
            if name[i]==0:
                name=name[0:i]
                break
        if len(name)>0:
            #print(urllib.parse.quote(name))
            if name in points:
                point=points[name]
                if point<-5:
                    data = ctypes.c_long(0)
                    mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10,ctypes.byref(data),1,None)
                elif point<0:
                    data = ctypes.c_long(0x2e)
                    for i in range(0,wait_s):
                        mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10+i,ctypes.byref(data),1,None)
                    data = ctypes.c_long(0)
                    mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10+wait_s,ctypes.byref(data),1,None)
                elif point>=1000:
                    data = ctypes.c_long(int.from_bytes(str(point//1000).encode(encoding='UTF-8'),byteorder='little'))
                    mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10,ctypes.byref(data),len(str(point//1000)),None)
                    data = ctypes.c_long(int.from_bytes(str(point-point//1000*1000).zfill(3).encode(encoding='UTF-8'),byteorder='little'))
                    mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10+len(str(point//1000)),ctypes.byref(data),3,None)
                    data = ctypes.c_long(0)
                    mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10+len(str(point)),ctypes.byref(data),1,None)
                else:
                    data = ctypes.c_long(int.from_bytes(str(point).encode(encoding='UTF-8'),byteorder='little'))
                    mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10,ctypes.byref(data),len(str(point)),None)
                    data = ctypes.c_long(0)
                    mydll.WriteProcessMemory(int(phand),str_addr+str_dis*clientid+0x10+len(str(point)),ctypes.byref(data),1,None)
            else:
                points[name]=-10
    time.sleep(0.2)

