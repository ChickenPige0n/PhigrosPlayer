from tkinter import Tk,Toplevel,Canvas
from threading import Thread
from ctypes import windll
from os import chdir,environ,listdir,popen ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from os.path import exists,abspath,dirname
from sys import argv
from time import time,sleep
from math import cos,sin,radians,pi
from json import loads
from queue import Queue
from shutil import rmtree
from tempfile import gettempdir
import typing
import csv

from PIL import Image,ImageTk,ImageDraw,ImageFilter,ImageEnhance
from win32gui import GetWindowLong,SetWindowLong,SetParent
from pygame import mixer
import win32con
import win32ui

try: import Chart_Objects
except SyntaxError: import Chart_Objects_Low_Python_Ver as Chart_Objects
import Find_Files
import PlaySound
import ConsoleWindow

if "-hideconsole" in argv:
    ConsoleWindow.Hide()

windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = windll.shcore.GetScaleFactorForDevice(0)
Tk_Temp = Tk
Toplevel_Temp = Toplevel
class Tk(Tk_Temp):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.tk.call("tk","scaling",ScaleFactor / 75)
class Toplevel(Toplevel_Temp):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.tk.call("tk","scaling",ScaleFactor / 75)
del Tk_Temp,Toplevel_Temp

selfdir = dirname(argv[0])
if selfdir == "": selfdir = "."
chdir(selfdir)

if not exists(".\\7z.exe"):
    print("7z.exe Not Found.")
    windll.kernel32.ExitProcess(1)

temp_dir = f"{gettempdir()}\\phigros_chart_temp_{time()}"
for item in [item for item in listdir(gettempdir()) if item.startswith("phigros_chart_temp_")]:
    item = f"{gettempdir()}\\{item}"
    try:
        rmtree(item)
        print(f"Remove Temp Dir: {item}")
    except Exception as e:
        print(f"Warning: {e}")
print(f"Temp Dir: {temp_dir}")

if "-clear" in argv:
    windll.kernel32.ExitProcess(0)

debug = False
if "-debug" in argv:
    debug = True

if len(argv) < 2 or not exists(argv[1]):
    dlg = win32ui.CreateFileDialog(1)
    dlg.DoModal()
    argv = [argv[0]] + [dlg.GetPathName()] + argv[0:]
    if argv[1] == "":
        windll.kernel32.ExitProcess(1)

note_id = -1

print("Loading Font...")
def remove_font():
    while windll.gdi32.RemoveFontResourceW(".\\font.ttf"): pass
remove_font()
windll.gdi32.AddFontResourceW(".\\font.ttf")

print("Init Pygame Mixer...")
mixer.init()

print("Unpack Chart...")
popen(f".\\7z.exe e \"{argv[1]}\" -o\"{temp_dir}\" >> nul").read()

print("Loading All Files of Chart...")
chart_files = Find_Files.Get_All_Files(temp_dir)
chart_files_dict = {
    "charts":[],
    "images":[],
    "audio":[],
}
for item in chart_files:
    try:
        chart_files_dict["images"].append([item,Image.open(item).convert("RGB")])
        name = item.replace(temp_dir+"\\","")
        print(f"Add Resource (image): {name}")
    except Exception:
        try:
            mixer.music.load(item)
            chart_files_dict["audio"].append(item)
            name = item.replace(temp_dir+"\\","")
            print(f"Add Resource (audio): {name}")
        except Exception:
            try:
                with open(item,"r",encoding="utf-8") as f:
                    chart_files_dict["charts"].append([item,loads(f.read())])
                    name = item.replace(temp_dir+"\\","")
                    print(f"Add Resource (chart): {name}")
            except Exception:
                name = item.replace(temp_dir+"\\","")
                print(f"Warning: Unknown Resource Type. Path = {name}")
if len(chart_files_dict["charts"]) == 0:
    print("No Chart File Found.")
    windll.kernel32.ExitProcess(1)
if len(chart_files_dict["audio"]) == 0:
    print("No Audio File Found.")
    windll.kernel32.ExitProcess(1)
if len(chart_files_dict["images"]) == 0:
    print("No Image File Found.")
    windll.kernel32.ExitProcess(1)
defualt_information = {
    "Name":"Unknow",
    "Artist":"Unknow",
    "Level":"Unknow",
    "Charter":"Unknow",
    "BackgroundDim":0.6
}
phigros_chart_index = 0
chart_image_index = 0
audio_file_index = 0
if len(chart_files_dict["charts"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["charts"]):
        index += 1
        name = chart_file[0].split("/")[-1].split("\\")[-1]
        print(f"{index}. {name}")
    phigros_chart_index = int(input("请选择谱面文件: "))-1
    phigros_chart = chart_files_dict["charts"][phigros_chart_index][1]
else:
    phigros_chart = chart_files_dict["charts"][phigros_chart_index][1]
phigros_chart_filepath = chart_files_dict["charts"][phigros_chart_index][0]
if len(chart_files_dict["images"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["images"]):
        index += 1
        name = chart_file[0].split("/")[-1].split("\\")[-1]
        print(f"{index}. {name}")
    chart_image_index = int(input("请选择谱面图片: "))-1
    chart_image = chart_files_dict["images"][chart_image_index][1]
else:
    chart_image = chart_files_dict["images"][chart_image_index][1]
chart_image_filepath = chart_files_dict["images"][chart_image_index][0]
if len(chart_files_dict["audio"]) > 1:
    for index,chart_file in enumerate(chart_files_dict["audio"]):
        index += 1
        name = chart_file.split("/")[-1].split("\\")[-1]
        print(f"{index}. {name}")
    audio_file_index = int(input("请选择音频文件: "))-1
    audio_file = chart_files_dict["audio"][audio_file_index]
else:
    audio_file = chart_files_dict["audio"][audio_file_index]
mixer.music.load(audio_file)
audio_length = mixer.Sound(audio_file).get_length()
all_inforamtion = {}
print("Loading Chart Information...")
if not exists(f"{temp_dir}\\info.csv"):
    print("No info.csv Found.")
    chart_information = defualt_information
else:
    path_head = f"{temp_dir}\\"
    _process_path = lambda path:abspath(path_head+path)
    _process_path2 = lambda path:abspath(path)
    info_csv_map = {
        name:None for name in "Chart,Music,Image,AspectRatio,ScaleRatio,GlobalAlpha,Name,Level,Illustrator,Designer".split(",")
    }
    with open(f"{temp_dir}\\info.csv","r",encoding="utf-8") as f:
        reader = csv.reader(f)
        for index,row in enumerate(reader):
            if index == 0:
                for index_csv_map,item in enumerate(row):
                    if item in info_csv_map:
                        info_csv_map[item] = index_csv_map
                break
        for row in reader:
            try:
                all_inforamtion[
                    (
                        _process_path(row[info_csv_map["Chart"] if info_csv_map["Chart"] is not None else 0]),
                        _process_path(row[info_csv_map["Music"] if info_csv_map["Music"] is not None else 1]),
                        _process_path(row[info_csv_map["Image"] if info_csv_map["Image"] is not None else 2])
                    )
                ] = {
                    name:row[info_csv_map[name]] for name in info_csv_map.keys() if info_csv_map[name] is not None and info_csv_map[name] < len(row)
                }
            except Exception as e:
                print(f"Warning: {e} in info.csv.")
    now_key = (
        _process_path2(phigros_chart_filepath),
        _process_path2(audio_file),
        _process_path2(chart_image_filepath)
    )
    for keys in all_inforamtion.keys():
        if keys == now_key:
            chart_information = {
                "Name":all_inforamtion[keys]["Name"] if "Name" in all_inforamtion[keys] else "Unknow",
                "Artist":all_inforamtion[keys]["Artist"] if "Artist" in all_inforamtion[keys] else "Unknow",
                "Level":all_inforamtion[keys]["Level"] if "Level" in all_inforamtion[keys] else "SP Lv.?",
                "Charter":all_inforamtion[keys]["Charter"] if "Charter" in all_inforamtion[keys] else "Unknow",
                "BackgroundDim":float(all_inforamtion[keys]["BackgroundDim"] if "BackgroundDim" in all_inforamtion[keys] else 0.6)
            }
        # print(keys,now_key)
    try:
        chart_information
    except NameError:
        print("info.cvs Found. But cannot find information of this chart.")
        chart_information = defualt_information
print("Loading Chart Information Successfully.")
print("Inforamtions: ")
print("              Name:",chart_information["Name"])
print("              Artist:",chart_information["Artist"])
print("              Level:",chart_information["Level"])
print("              Charter:",chart_information["Charter"])
print("              BackgroundDim:",chart_information["BackgroundDim"])

del chart_files,chart_files_dict

def Get_Animation_Gr(fps:float,t:float):
    gr_x = int(fps * t) + 1
    gr = [cos(x / gr_x) + 1 for x in range(int(gr_x * pi))]
    gr_sum = sum(gr)
    step_time = t / len(gr)
    return [item / gr_sum for item in gr],step_time

def rotate_point(x,y,θ,r):
    xo = r * cos(radians(θ))
    yo = r * sin(radians(θ))
    return x + xo,y + yo

def Get_A_New_NoteId():
    global note_id
    note_id += 1
    return note_id

def loger():
    while True:
        while not loger_queue.empty():
            print(loger_queue.get())
        sleep(0.01)

def unpack_pos(number:int) -> tuple[int,int]:
    return (number - number % 1000) // 1000,number % 1000

loger_queue = Queue()
clickeffect_cache = []

def Load_Chart_Object():
    global phigros_chart_obj
    print("Loading Chart Object...")
    phigros_chart_obj = Chart_Objects.Phigros_Chart(
        formatVersion=phigros_chart["formatVersion"],
        offset=phigros_chart["offset"],
        judgeLineList=[
            Chart_Objects.judgeLine(
                id=index,
                bpm=judgeLine_item["bpm"],
                notesAbove=[
                    Chart_Objects.note(
                        type=notesAbove_item["type"],
                        time=notesAbove_item["time"],
                        positionX=notesAbove_item["positionX"],
                        holdTime=notesAbove_item["holdTime"],
                        speed=notesAbove_item["speed"],
                        floorPosition=notesAbove_item["floorPosition"],
                        clicked=False,
                        morebets=False,
                        id=Get_A_New_NoteId(),
                        rendered=False
                    )
                    for notesAbove_item in judgeLine_item["notesAbove"]
                ],
                notesBelow=[
                    Chart_Objects.note(
                        type=notesBelow_item["type"],
                        time=notesBelow_item["time"],
                        positionX=notesBelow_item["positionX"],
                        holdTime=notesBelow_item["holdTime"],
                        speed=notesBelow_item["speed"],
                        floorPosition=notesBelow_item["floorPosition"],
                        clicked=False,
                        morebets=False,
                        id=Get_A_New_NoteId(),
                        rendered=False
                    )
                    for notesBelow_item in judgeLine_item["notesBelow"]
                ],
                speedEvents=[
                    Chart_Objects.speedEvent(
                        startTime=speedEvent_item["startTime"],
                        endTime=speedEvent_item["endTime"],
                        value=speedEvent_item["value"],
                        floorPosition=speedEvent_item["floorPosition"] if "floorPosition" in speedEvent_item else None
                    )
                    for speedEvent_item in judgeLine_item["speedEvents"]
                ],
                judgeLineMoveEvents=[
                    Chart_Objects.judgeLineMoveEvent(
                        startTime=judgeLineMoveEvent_item["startTime"],
                        endTime=judgeLineMoveEvent_item["endTime"],
                        start=judgeLineMoveEvent_item["start"],
                        end=judgeLineMoveEvent_item["end"],
                        start2=judgeLineMoveEvent_item["start2"],
                        end2=judgeLineMoveEvent_item["end2"]
                    )
                    for judgeLineMoveEvent_item in judgeLine_item["judgeLineMoveEvents"]
                ] if len(judgeLine_item["judgeLineMoveEvents"]) > 0 and "start2" in judgeLine_item["judgeLineMoveEvents"][0] and "end2" in judgeLine_item["judgeLineMoveEvents"][0] else [
                    Chart_Objects.judgeLineMoveEvent(
                        startTime=judgeLineMoveEvent_item["startTime"],
                        endTime=judgeLineMoveEvent_item["endTime"],
                        start=unpack_pos(judgeLineMoveEvent_item["start"])[0] / 880,
                        end=unpack_pos(judgeLineMoveEvent_item["end"])[0] / 880,
                        start2=unpack_pos(judgeLineMoveEvent_item["start"])[1] / 520,
                        end2=unpack_pos(judgeLineMoveEvent_item["end"])[1] / 520
                    )
                    for judgeLineMoveEvent_item in judgeLine_item["judgeLineMoveEvents"]
                ],
                judgeLineRotateEvents=[
                    Chart_Objects.judgeLineRotateEvent(
                        startTime=judgeLineRotateEvent_item["startTime"],
                        endTime=judgeLineRotateEvent_item["endTime"],
                        start=judgeLineRotateEvent_item["start"],
                        end=judgeLineRotateEvent_item["end"]
                    )
                    for judgeLineRotateEvent_item in judgeLine_item["judgeLineRotateEvents"]
                ],
                judgeLineDisappearEvents=[
                    Chart_Objects.judgeLineDisappearEvent(
                        startTime=judgeLineDisappearEvent_item["startTime"],
                        endTime=judgeLineDisappearEvent_item["endTime"],
                        start=judgeLineDisappearEvent_item["start"],
                        end=judgeLineDisappearEvent_item["end"]
                    )
                    for judgeLineDisappearEvent_item in judgeLine_item["judgeLineDisappearEvents"]
                ]
            )
            for index,judgeLine_item in enumerate(phigros_chart["judgeLineList"])
        ]
    )
    for judgeLine in phigros_chart_obj.judgeLineList:
        judgeLine.set_master_to_notes()
    phigros_chart_obj.cal_note_num()
    print("Finding Chart More Bets...")
    notes = []
    for judgeLine in phigros_chart_obj.judgeLineList:
        for note in judgeLine.notesAbove + judgeLine.notesBelow:
            notes.append(note)
    note_times = {}
    for note in notes:
        note:Chart_Objects.note
        if note.time not in note_times:
            note_times[note.time] = 1
        else:
            note_times[note.time] += 1
    for note in notes:
        if note_times[note.time] > 1:
            note.morebets = True
    del notes,note_times
    print("Load Chart Object Successfully.")

Load_Chart_Object()

def Replace_Image_Color(im:Image.Image,color):
    for x in range(im.width):
        for y in range(im.height):
            im.putpixel((x,y),(color[0],color[1],color[2],im.getpixel((x,y))[-1]))
    return im

def Load_Resource():
    global ClickEffect_Size
    print("Loading Resource...")
    Note_width = int(min(w,h) / 7.5)
    Note_height_Tap = int(Note_width / 989 * 100)
    Note_height_Tap_dub = int(Note_width / 1089 * 200)
    Note_height_Drag = int(Note_width / 989 * 60)
    Note_height_Drag_dub = int(Note_width / 1089 * 160)
    Note_height_Flick = int(Note_width / 989 * 200)
    Note_height_Flick_dub = int(Note_width / 1089 * 300)
    ClickEffect_Size = int(Note_width*1.5)
    Resource = {
        "Notes":{
            "Tap":ImageTk.PhotoImage(Image.open("./Resources/Notes/Tap.png").resize((Note_width,Note_height_Tap))),
            "Tap_dub":ImageTk.PhotoImage(Image.open("./Resources/Notes/Tap_dub.png").resize((Note_width,Note_height_Tap_dub))),
            "Drag":ImageTk.PhotoImage(Image.open("./Resources/Notes/Drag.png").resize((Note_width,Note_height_Drag))),
            "Drag_dub":ImageTk.PhotoImage(Image.open("./Resources/Notes/Drag_dub.png").resize((Note_width,Note_height_Drag_dub))),
            "Flick":ImageTk.PhotoImage(Image.open("./Resources/Notes/Flick.png").resize((Note_width,Note_height_Flick))),
            "Flick_dub":ImageTk.PhotoImage(Image.open("./Resources/Notes/Flick_dub.png").resize((Note_width,Note_height_Flick_dub))),
            "Hold":ImageTk.PhotoImage(Image.open("./Resources/Notes/Hold.png").resize((Note_width,int(min(w,h)/75)))),
            "Hold_dub":ImageTk.PhotoImage(Image.open("./Resources/Notes/Hold_dub.png").resize((Note_width,int(min(w,h)/75))))
        },
        "Note_Click_Effect":{
            "Perfect":[
                ImageTk.PhotoImage(Image.open(f"./Resources/Note_Click_Effect/Perfect/{i}.png").resize((ClickEffect_Size,)*2))
                for i in range(1,31)
            ],
            "Good":[
                ImageTk.PhotoImage(Image.open(f"./Resources/Note_Click_Effect/Good/{i}.png").resize((ClickEffect_Size,)*2))
                for i in range(1,31)
            ]
        },
        "Note_Click_Audio":{
            "1":open("./Resources/Note_Click_Audio/Tap.wav","rb").read(),
            "2":open("./Resources/Note_Click_Audio/Drag.wav","rb").read(),
            "3":open("./Resources/Note_Click_Audio/Hold.wav","rb").read(),
            "4":open("./Resources/Note_Click_Audio/Flick.wav","rb").read()
        },
        "ProcessBar":Image.new("RGB",(w,int(h / 125)),(145,)*3),
        "Start":ImageTk.PhotoImage(Image.open("./Resources/Start.png").resize((w,h)))
    }
    ImageDraw.Draw(Resource["ProcessBar"]).rectangle((w * 0.998,0,w,int(h / 125)),fill=(255,)*3)
    Resource["ProcessBar"] = ImageTk.PhotoImage(Resource["ProcessBar"])
    print("Loading Resource Successfully.")
    root.configure(cursor="arrow")
    show_start_toplevel.configure(cursor="arrow")
    root.deiconify()
    return Resource

def Show_Start():
    show_start_toplevel.overrideredirect(True)
    show_start_cv = Canvas(show_start_toplevel,width=w,height=h,bg="white",highlightthickness=0)
    show_start_cv.create_image(0,0,image=Resource["Start"],anchor="nw")
    show_start_cv.pack()
    show_start_toplevel.update()
    show_start_toplevel_hwnd = int(show_start_toplevel.frame(),16)
    Style = GetWindowLong(show_start_toplevel_hwnd,win32con.GWL_STYLE)
    Style = Style &~win32con.WS_CAPTION &~win32con.WS_SYSMENU &~win32con.WS_SIZEBOX | win32con.WS_CHILD
    SetWindowLong(show_start_toplevel_hwnd,win32con.GWL_STYLE,Style) ; del Style
    SetParent(show_start_toplevel_hwnd,window_hwnd)
    show_start_toplevel.geometry("+0+0")
    gr,step_time = Get_Animation_Gr(60,1.25)
    alpha = 0.0
    for step in gr:
        alpha += step
        show_start_toplevel.attributes("-alpha",alpha)
        sleep(step_time)
    cv.create_image(0,0,image=background_image,anchor="nw")
    cv.create_image(-w,0,image=Resource["ProcessBar"],anchor="nw",tags=["ProcessBar","top"])
    cv.create_text(w * 0.99,h * 0.005,text="0000000",anchor="ne",tags=["score","top"],fill="white",font=("Source Han Sans & Saira Hybrid",int((w + h) / 75)))
    cv.create_text(w / 2,h * 0.001,text="0",anchor="n",fill="white",tags=["combo","top"],font=("Source Han Sans & Saira Hybrid",int((w + h) / 70)),state="hidden")
    cv.create_text(w / 2,h * 0.055,text="Autoplay" if "-combotips" not in argv else argv[argv.index("-combotips") + 1],anchor="n",fill="white",tags=["combo_under_tips","top"],font=("Source Han Sans & Saira Hybrid",int((w + h) / 100)),state="hidden")
    cv.create_text(0,h * 0.00075,text="0:00/0:00",anchor="nw",fill="white",tags=["time","top"],font=("Source Han Sans & Saira Hybrid",int((w + h) / 175)))
    cv.create_text(w * 0.01,h * 0.98,text=chart_information["Name"],anchor="sw",tags=["chart_name","top"],fill="white",font=("Source Han Sans & Saira Hybrid",int((w + h) / 125)))
    cv.create_text(w * 0.99,h * 0.99,text=chart_information["Level"],anchor="se",tags=["level","top"],fill="white",font=("Source Han Sans & Saira Hybrid",int((w + h) / 125)))
    sleep(0.5)
    for step in gr:
        alpha -= step
        show_start_toplevel.attributes("-alpha",alpha)
        sleep(step_time)
    show_start_cv.destroy()
    show_start_toplevel.destroy()
    Thread(target=PlayerStart,daemon=True).start()

def Show_Note_Click_Effect(x,y,t:typing.Literal["Perfect","Good"]):
    last_id = None
    effect_time = 0.5
    effect_ims = Resource["Note_Click_Effect"][t]
    effect_step_time = effect_time / len(effect_ims)
    def nocache_create_a_cache():
        nonlocal last_id
        ids = []
        for im in effect_ims:
            st = time()
            id_ = cv.create_image(x,y,image=im,anchor="center")
            if last_id is not None:
                cv.moveto(last_id,-w,-h)
                ids.append(last_id)
            last_id = id_
            sleep(effect_step_time - min(time() - st,effect_step_time))
        cv.moveto(last_id,-w,-h)
        ids.append(last_id)
        clickeffect_cache.append([ids,t,False])
    if not any([not item[2] and item[1] == t for item in clickeffect_cache]):
        nocache_create_a_cache()
    else:
        try:
            index = [item[2] for item in clickeffect_cache].index(False)
        except ValueError:
            nocache_create_a_cache()
            return None
        clickeffect_cache[index][2] = True #using
        last_imid = None
        for imid in clickeffect_cache[index][0]:
            st = time()
            cv.moveto(imid,x - ClickEffect_Size / 2,y - ClickEffect_Size / 2)
            if last_imid is not None:
                cv.moveto(last_imid,-w,-h)
            last_imid = imid
            sleep(effect_step_time - min(time() - st,effect_step_time))
        cv.moveto(last_imid,-w,-h)
        clickeffect_cache[index][2] = False

def Update_JudgeLine_Configs(judgeLine_Configs,T_dws,now_t:int|float):
    for judgeLine_cfg_key in judgeLine_Configs:
        judgeLine_cfg = judgeLine_Configs[judgeLine_cfg_key]
        judgeLine_cfg["time"] = now_t / T_dws[judgeLine_cfg_key]
        judgeLine:Chart_Objects.judgeLine = judgeLine_cfg["judgeLine"]
        for rotate_event in judgeLine.judgeLineRotateEvents:
            if rotate_event.startTime <= judgeLine_cfg["time"] <= rotate_event.endTime:
                try: judgeLine_cfg["Rotate"] = rotate_event.start + (rotate_event.end - rotate_event.start) * ((judgeLine_cfg["time"] - rotate_event.startTime) / (rotate_event.endTime - rotate_event.startTime))
                except ZeroDivisionError: judgeLine_cfg["Rotate"] = rotate_event.start
        for disappear_event in judgeLine.judgeLineDisappearEvents:
            if disappear_event.startTime <= judgeLine_cfg["time"] <= disappear_event.endTime:
                try: judgeLine_cfg["Disappear"] = disappear_event.start + (disappear_event.end - disappear_event.start) * ((judgeLine_cfg["time"] - disappear_event.startTime) / (disappear_event.endTime - disappear_event.startTime)) 
                except ZeroDivisionError: judgeLine_cfg["Disappear"] = disappear_event.start
        for move_event in judgeLine.judgeLineMoveEvents:
            if move_event.startTime <= judgeLine_cfg["time"] <= move_event.endTime:
                try:
                    judgeLine_cfg["Pos"] = [
                        move_event.start + (move_event.end - move_event.start) * ((judgeLine_cfg["time"] - move_event.startTime) / (move_event.endTime - move_event.startTime)),
                        move_event.start2 + (move_event.end2 - move_event.start2) * ((judgeLine_cfg["time"] - move_event.startTime) / (move_event.endTime - move_event.startTime))
                    ]
                    judgeLine_cfg["Pos"] = [
                        judgeLine_cfg["Pos"][0] * w,
                        judgeLine_cfg["Pos"][1] * h
                    ]
                except ZeroDivisionError:
                    judgeLine_cfg["Pos"] = [
                        move_event.start * w,
                        move_event.start2 * h
                    ]
                judgeLine_cfg["Pos"][1] = h - judgeLine_cfg["Pos"][1]
        for speed_event in judgeLine.speedEvents:
            if speed_event.startTime <= judgeLine_cfg["time"] <= speed_event.endTime:
                judgeLine_cfg["Speed"] = speed_event.value

def Format_Time(t:int|float) -> str:
    m,s = t // 60,t % 60
    m,s = int(m),int(s)
    return f"{m}:{s:>2}".replace(" ","0")

def Cal_judgeLine_NoteDy(judgeLine_cfg,T:int|float) -> float:
    judgeLine:Chart_Objects.judgeLine = judgeLine_cfg["judgeLine"]
    if judgeLine.speedEvents == []: return 0
    dy = 0
    t = judgeLine_cfg["time"]
    if judgeLine.speedEvents[0].floorPosition is not None:
        for speed_event in judgeLine.speedEvents:
            if speed_event.startTime <= t <= speed_event.endTime:
                dy = speed_event.floorPosition * PHIGROS_Y + (
                    t - speed_event.startTime
                ) * T * speed_event.value * PHIGROS_Y
                return dy
        last_speed_event = sorted(judgeLine.speedEvents,key=lambda x:x.startTime)[-1]
        dy = last_speed_event.floorPosition * PHIGROS_Y + (t - last_speed_event.endTime) * T * last_speed_event.value * PHIGROS_Y
        return dy
    else:
        for speed_event in judgeLine.speedEvents:
            if speed_event.startTime < t and speed_event.endTime < t:
                dy += (speed_event.endTime - speed_event.startTime) * T * speed_event.value * PHIGROS_Y
            elif speed_event.startTime <= t <= speed_event.endTime:
                dy += (t - speed_event.startTime) * T * speed_event.value * PHIGROS_Y
            else:
                pass
        return dy

def Get_judgeLine_Color() -> str:
    return "#feffa9" if "-nofcapline" not in argv else "#ffffff"

def PlayerStart(again:bool=False,again_toplevel:None|Toplevel=None):
    print("Player Start")
    root.title("Phigros Chart Player")
    def judgeLine_Animation():
        gr,step_time = Get_Animation_Gr(60,0.5)
        last_id = None
        val = 0.0
        for step in gr:
            st = time()
            val += step
            last_id_ = cv.create_line(
                w / 2 - (val * w / 2),h / 2,
                w / 2 + (val * w / 2),h / 2,
                fill=Get_judgeLine_Color(),
                width=(0.05625 * w) / 17.5,
                smooth=True,
                tag="judgeLine_start_animation"
            )
            if last_id is not None:
                cv.delete(last_id)
            last_id = last_id_
            sleep(step_time - min(time() - st,step_time))
    if again:
        again_toplevel.overrideredirect(True)
        again_toplevel.update()
        again_toplevel_hwnd = int(again_toplevel.frame(),16)
        Style = GetWindowLong(again_toplevel_hwnd,win32con.GWL_STYLE)
        Style = Style &~win32con.WS_CAPTION &~win32con.WS_SYSMENU &~win32con.WS_SIZEBOX | win32con.WS_CHILD
        SetWindowLong(again_toplevel_hwnd,win32con.GWL_STYLE,Style) ; del Style
        SetParent(again_toplevel_hwnd,window_hwnd)
        again_toplevel.geometry("+0+0")
        again_toplevel.deiconify()
        root.focus_force()
        gr,step_time = Get_Animation_Gr(60,0.75)
        alpha = 0.0
        for step in gr:
            alpha += step
            again_toplevel.attributes("-alpha",alpha)
            sleep(step_time)
        cv.delete("note")
        cv.delete("judgeLine")
        cv.itemconfigure("score",text="0000000")
        cv.itemconfigure("combo",text="0")
        cv.itemconfigure("time",text="0:00/0:00")
        cv.itemconfigure("combo",state="hidden")
        cv.itemconfigure("combo_under_tips",state="hidden")
        cv.move("ProcessBar",-w,0)
        sleep(0.2)
        Thread(target=judgeLine_Animation,daemon=True).start()
        for step in gr:
            alpha -= step
            again_toplevel.attributes("-alpha",alpha)
            sleep(step_time)
        again_toplevel.destroy()
    else:
        judgeLine_Animation()

    show_start_time = time()
    now_t = 0
    T_dws = {judgeLine_item.__hash__():1.875/judgeLine_item.bpm for judgeLine_item in phigros_chart_obj.judgeLineList}
    judgeLine_Configs = {
        judgeLine_item.__hash__():{
            "judgeLine":judgeLine_item,
            "Rotate":0.0,
            "Disappear":1.0,
            "Pos":[0,0],
            "Speed":1.0,
            "Note_dy":0.0,
            "time":None
        }
        for judgeLine_item in phigros_chart_obj.judgeLineList
    }
    Thread(target=lambda:[sleep(max(0,phigros_chart_obj.offset)),mixer.music.play()],daemon=True).start()
    fps = 120
    if "-fps" in argv:
        fps = eval(argv[argv.index("-fps") + 1])
    ids = {}
    combo = 0
    combo_and_combo_under_tips_showed = False
    last_time_text = "0:00/0:00"
    deleted_start_animation_judgeLine = False
    this_function_call_st = time()
    process_xpos = 0
    judgeLine_last_cfg_dict = {item:None for item in judgeLine_Configs.keys()}
    judgeLine_draw_ids_dict = {item:None for item in judgeLine_Configs.keys()}
    while True:
        st = time()
        now_t = time() - show_start_time
        Update_JudgeLine_Configs(judgeLine_Configs,T_dws,now_t)
        for judgeLine_cfg_key in judgeLine_Configs:
            judgeLine_cfg = judgeLine_Configs[judgeLine_cfg_key]
            judgeLine:Chart_Objects.judgeLine = judgeLine_cfg["judgeLine"]
            judgeLine_cfg["Note_dy"] = Cal_judgeLine_NoteDy(judgeLine_cfg,T_dws[judgeLine_cfg_key])
            judgeLine_DrawPos = [
                *rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],5.76 * h),
                *rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"] + 180,5.76 * h)
            ]
            last_cfg = judgeLine_last_cfg_dict[judgeLine_cfg_key]
            draw_cfg = {
                "fill":Get_judgeLine_Color(),
                "width":h * 0.0075 * judgeLine_cfg["Disappear"],
                "smooth":True,
                "tag":"judgeLine"
            }
            if last_cfg != (judgeLine_DrawPos,draw_cfg):
                will_delete_id = judgeLine_draw_ids_dict[judgeLine_cfg_key]
                if draw_cfg["width"] != 0.0:
                    judgeLine_draw_ids_dict.update({
                        judgeLine_cfg_key:[
                            cv.create_line(
                                *judgeLine_DrawPos,**draw_cfg
                            ),
                            cv.create_rectangle(
                                judgeLine_cfg["Pos"][0] - PHIGROS_X / 12.5,
                                judgeLine_cfg["Pos"][1] - PHIGROS_X / 12.5,
                                judgeLine_cfg["Pos"][0] + PHIGROS_X / 12.5,
                                judgeLine_cfg["Pos"][1] + PHIGROS_X / 12.5,
                                fill="#ee82ee",outline="",tag="judgeLine"
                            ) if debug else None,
                            cv.create_text(
                                *rotate_point(*judgeLine_cfg["Pos"],- 90 - judgeLine_cfg["Rotate"],PHIGROS_X / 3.5),
                                text=f"{judgeLine.id}",fill="#feffa9",
                                font=("Source Han Sans & Saira Hybrid",int((w + h) / 100)),
                                tag="judgeLine"
                            ) if debug else None
                        ]
                    })
                if will_delete_id is not None:
                    cv.delete(*will_delete_id)
            if not deleted_start_animation_judgeLine:
                cv.delete("judgeLine_start_animation")
                deleted_start_animation_judgeLine = True
            judgeLine_notes_above = judgeLine.notesAbove
            judgeLine_notes_below = judgeLine.notesBelow
            def process(notes_list:list[Chart_Objects.note],t:int):
                nonlocal combo,combo_and_combo_under_tips_showed
                for note_item in notes_list:
                    if note_item.clicked:
                        continue
                    cfg = {
                        "note":note_item,
                        "now_floorPosition":note_item.floorPosition * PHIGROS_Y - judgeLine_cfg["Note_dy"]
                    }
                    rotatenote_at_judgeLine_pos = rotate_point(
                        *judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],note_item.positionX * PHIGROS_X
                    )
                    rotated_x,rotated_y = rotate_point(
                        *rotatenote_at_judgeLine_pos,90 - judgeLine_cfg["Rotate"] - (180 if t == 1 else 0),cfg["now_floorPosition"] #why? -> (180 if t == 1 else 0)
                    )
                    x,y = rotated_x,rotated_y
                    note_type = {1:"Tap",2:"Drag",3:"Hold",4:"Flick"}[note_item.type]
                    render_range = 1.2
                    if (
                            -w * (render_range - 1.0) < x < render_range * w
                            and -h * (render_range - 1.0) < y < render_range * h
                        ) or note_item.rendered:
                        if not T_dws[judgeLine_cfg_key] * note_item.time < now_t:
                            if note_item.morebets:
                                note_type += "_dub"
                            if note_item.__hash__() not in ids:
                                ids.update(
                                    {
                                        note_item.__hash__():[cv.create_image(
                                            x,y,
                                            image=Resource["Notes"][note_type],
                                            anchor="center",tag=f"note_{note_item.id}"
                                        ),t,
                                        Resource["Notes"][note_type].width(),
                                        Resource["Notes"][note_type].height(),
                                        x,y]
                                    }
                                )
                                if debug:
                                    cv.create_rectangle(
                                        x - PHIGROS_X / 12.5,y - PHIGROS_X / 12.5,
                                        x + PHIGROS_X / 12.5,y + PHIGROS_X / 12.5,
                                        fill="#00ff00",outline="",tag=f"note_{note_item.id}"
                                    )
                                    cv.create_text(
                                        x,y - PHIGROS_X / 3.5,
                                        text=f"{note_item}",fill="#00ffff",
                                        font=("Source Han Sans & Saira Hybrid",int((w + h) / 100)),
                                        tags=[f"note_{note_item.id}",f"note_{note_item.id}_debug_id"]
                                    )
                                loger_queue.put(f"Create New Note: {note_item}")
                                note_item.rendered = True
                            else:
                                try:
                                    data = ids[note_item.__hash__()]
                                    if data[4] != x or data[5] != y:
                                        cv.moveto(
                                            f"note_{note_item.id}",
                                            x - data[2] / 2,
                                            y - data[3] / 2
                                        )
                                        data[4],data[5] = x,y
                                except KeyError:
                                    pass
                    if (
                            (not note_item.clicked)
                            and (T_dws[judgeLine_cfg_key] * note_item.time <= now_t)
                        ):
                        try:
                            cv.delete(f"note_{note_item.id}")
                            ids.pop(note_item.__hash__())
                        except KeyError:
                            pass
                        combo += 1
                        loger_queue.put(f"Destroy Note: {note_item}")
                        score = phigros_chart_obj.cal_score(combo)
                        cv.itemconfigure("score",text=f"{score}")
                        cv.itemconfigure("combo",text=f"{combo}")
                        if not combo_and_combo_under_tips_showed:
                            if combo >= 3:
                                cv.itemconfigure("combo",state="normal")
                                cv.itemconfigure("combo_under_tips",state="normal")
                        elif combo < 3:
                            combo_and_combo_under_tips_showed = False
                            cv.itemconfigure("combo",state="hidden")
                            cv.itemconfigure("combo_under_tips",state="hidden")
                        Thread(target=PlaySound.Play,args=(Resource["Note_Click_Audio"][str(note_item.type)],),daemon=True).start()
                        Thread(
                                target=Show_Note_Click_Effect,
                                args=(
                                    *rotate_point(*judgeLine_cfg["Pos"],-judgeLine_cfg["Rotate"],note_item.positionX * PHIGROS_X),
                                    "Perfect"
                                )
                               ).start()
                        note_item.clicked = True
            process(judgeLine_notes_above,1)
            process(judgeLine_notes_below,-1)
        music_pos = time() - this_function_call_st
        now_process_xpos = int((music_pos / audio_length) * w)
        if now_process_xpos != process_xpos:
            process_xpos = now_process_xpos
            cv.moveto("ProcessBar",process_xpos - w,0)
        time_text = f"{Format_Time(music_pos)}/{Format_Time(audio_length)}"
        if time_text != last_time_text:
            last_time_text = time_text
            cv.itemconfigure("time",text=time_text)
        cv.tag_raise("top")
        if not mixer.music.get_busy():
            break
        sleep(1 / fps - min(time() - st,1 / fps))
        if "-showfps" in argv: root.title(f"Phigros Chart Player - FPS: {round(1 / (time() - st))}")
    print("Player Stopped")
    if "-loop" in argv:
        Load_Chart_Object()
        again_toplevel = Toplevel(root)
        again_toplevel.geometry(f"{w}x{h}+99999+99999")
        again_toplevel.withdraw()
        again_toplevel.protocol("WM_DELETE_WINDOW",lambda:[root.destroy(),remove_font()])
        again_toplevel.configure(cursor="watch")
        again_toplevel.bind("<FocusIn>",lambda e:root.focus_force())
        again_toplevel["bg"] = "#0078d7"
        Thread(target=PlayerStart,args=(True,again_toplevel),daemon=True).start()
    else:
        sleep(1.25)
        process_quit()

print("Loading Window...")
root = Tk()
root.withdraw()
root["bg"] = "black"
root.title(f"Phigros Chart Player")
root.iconbitmap(".\\icon.ico")
root.configure(cursor="watch")
if "-fullscreen" in argv:
    w,h = root.winfo_screenwidth(),root.winfo_screenheight()
    root.attributes("-fullscreen",True)
else:
    w,h = int(root.winfo_screenwidth() * 0.61803398874989484820458683436564),int(root.winfo_screenheight() * 0.61803398874989484820458683436564)
root.geometry(f"{w}x{h}+{int(root.winfo_screenwidth() / 2 - w / 2)}+{int(root.winfo_screenheight() / 2 - h / 2)}")
root.resizable(False,False)
print("Createing Canvas...")
cv = Canvas(root,width=w,height=h,bg="black",highlightthickness=0)
background_image = ImageTk.PhotoImage(ImageEnhance.Brightness(chart_image.resize((w,h)).filter(ImageFilter.GaussianBlur((w + h) / 300))).enhance(1.0 - chart_information["BackgroundDim"]))
cv.pack()
if "-hidemouse" in argv:
    cv.configure(cursor="none")
root.update()
PHIGROS_X,PHIGROS_Y = 0.05625 * w,0.6 * h
window_hwnd = int(root.frame(),16)
print(f"Window Hwnd: {window_hwnd}")
window_style = GetWindowLong(window_hwnd,win32con.GWL_STYLE)
SetWindowLong(window_hwnd,win32con.GWL_STYLE,window_style & ~win32con.WS_SYSMENU) ; del window_style
process_quit = lambda:[root.destroy(),remove_font(),exec("raise SystemExit"),windll.kernel32.ExitProcess(0)]
show_start_toplevel = Toplevel(root)
show_start_toplevel.geometry(f"{w}x{h}+99999+99999")
show_start_toplevel.protocol("WM_DELETE_WINDOW",process_quit)
show_start_toplevel.configure(cursor="watch")
root.protocol("WM_DELETE_WINDOW",process_quit)
show_start_toplevel.bind("<FocusIn>",lambda e:root.focus_force())
root.focus_force()
Resource = Load_Resource()
Thread(target=Show_Start,daemon=True).start()
Thread(target=loger,daemon=True).start()
root.mainloop()