from __future__ import annotations

import math
import typing
import logging
from dataclasses import dataclass
from functools import lru_cache, cache

import tool_funcs
import rpe_easing
import const
        
def _init_events(es: list[LineEvent]):
    aes = []
    for i, e in enumerate(es):
        if i != len(es) - 1:
            ne = es[i + 1]
            if e.endTime.value < ne.startTime.value:
                aes.append(LineEvent(e.endTime, ne.startTime, e.end, e.end, 1))
    es.extend(aes)
    es.sort(key = lambda x: x.startTime.value)
    if es: es.append(LineEvent(es[-1].endTime, Beat(31250000, 0, 1), es[-1].end, es[-1].end, 1))

def geteasing_func(t: int):
    try:
        if not isinstance(t, int): t = 1
        t = 1 if t < 1 else (len(rpe_easing.ease_funcs) if t > len(rpe_easing.ease_funcs) else t)
        return rpe_easing.ease_funcs[int(t) - 1]
    except Exception as e:
        logging.warning(f"geteasing_func error: {e}")
        return rpe_easing.ease_funcs[0]
        
@dataclass
class Beat:
    var1: int
    var2: int
    var3: int
    
    def __post_init__(self):
        self.value = self.var1 + (self.var2 / self.var3)
        self._hash = hash(self.value)
    
    def __hash__(self) -> int:
        return self._hash
    
@dataclass
class Note:
    type: int
    startTime: Beat
    endTime: Beat
    positionX: float
    above: int
    isFake: int
    speed: float
    yOffset: float
    visibleTime: float
    width: float
    alpha: int
    
    clicked: bool = False
    morebets: bool = False
    floorPosition: float = 0.0
    holdLength: float = 0.0
    show_effected: bool = False
    masterLine: JudgeLine|None = None
    master_index: int|None = None
    
    state: int = const.NOTE_STATE.MISS
    player_clicked: bool = False
    player_click_offset: float = 0.0
    player_click_sound_played: bool = False
    player_will_click: bool = False
    player_missed: bool = False
    player_badtime: float = float("nan")
    player_holdmiss_time: float = float("inf")
    player_last_testholdismiss_time: float = -float("inf")
    player_holdjudged: bool = False
    player_holdclickstate: int = const.NOTE_STATE.MISS
    player_holdjudged_tomanager: bool = False
    player_holdjudge_tomanager_time: float = float("nan") # init at note._init function
    player_drag_judge_safe_used: bool = False
    
    player_badtime_beat: float = float("nan")
    player_badjudge_floorp: float = float("nan")
    
    render_skiped: bool = False
    
    def __post_init__(self):
        self.phitype = {1:1, 2:3, 3:4, 4:2}[self.type]
        self.type_string = {
            const.Note.TAP: "Tap",
            const.Note.DRAG: "Drag",
            const.Note.HOLD: "Hold",
            const.Note.FLICK: "Flick"
        }[self.phitype]
        self.positionX2 = self.positionX / 1350
        self.float_alpha = (255 & int(self.alpha)) / 255
        self.ishold = self.type_string == "Hold"
    
    def _init(self, master: Rpe_Chart, avgBpm: float):
        self.secst = master.beat2sec(self.startTime.value, self.masterLine.bpmfactor)
        self.secet = master.beat2sec(self.endTime.value, self.masterLine.bpmfactor)
        self.player_holdjudge_tomanager_time = max(self.secst, self.secet - 0.2)
        
        self.effect_times = []
        
        self.effect_times.append((0.0, master.sec2beat(self.secst, self.masterLine.bpmfactor), tool_funcs.get_effect_random_blocks()))
        if self.ishold:
            bt = 1 / avgBpm * 30
            st = 0.0
            while True:
                st += bt
                if st >= self.secet - self.secst: break
                self.effect_times.append((st, master.sec2beat(self.secst + st, self.masterLine.bpmfactor), tool_funcs.get_effect_random_blocks()))
        
    def getNoteClickPos(self, time: float, master: Rpe_Chart, line: JudgeLine) -> tuple[float, float]:
        linePos = line.GetPos(time, master)
        lineRotate = sum([line.GetEventValue(time, layer.rotateEvents, 0.0) for layer in line.eventLayers])
        return tool_funcs.rotate_point(*linePos, lineRotate, self.positionX2)

    def __eq__(self, value): return self is value

@dataclass
class LineEvent:
    startTime: Beat
    endTime: Beat
    start: float|str|list[int]
    end: float|str|list[int]
    easingType: int
    easingFunc: typing.Callable[[float], float] = rpe_easing.ease_funcs[0]
    
    def __post_init__(self):
        self.easingFunc = geteasing_func(self.easingType)
    
@dataclass
class EventLayer:
    speedEvents: list[LineEvent]
    moveXEvents: list[LineEvent]
    moveYEvents: list[LineEvent]
    rotateEvents: list[LineEvent]
    alphaEvents: list[LineEvent]
    
    def __post_init__(self):
        self.speedEvents.sort(key = lambda x: x.startTime.value)
        self.moveXEvents.sort(key = lambda x: x.startTime.value)
        self.moveYEvents.sort(key = lambda x: x.startTime.value)
        self.rotateEvents.sort(key = lambda x: x.startTime.value)
        self.alphaEvents.sort(key = lambda x: x.startTime.value)
        
        _init_events(self.speedEvents)
        _init_events(self.moveXEvents)
        _init_events(self.moveYEvents)
        _init_events(self.rotateEvents)
        _init_events(self.alphaEvents)
        
@dataclass
class Extended:
    scaleXEvents: list[LineEvent]
    scaleYEvents: list[LineEvent]
    colorEvents: list[LineEvent]
    textEvents: list[LineEvent]
    
    def __post_init__(self):
        self.scaleXEvents.sort(key = lambda x: x.startTime.value)
        self.scaleYEvents.sort(key = lambda x: x.startTime.value)
        self.colorEvents.sort(key = lambda x: x.startTime.value)
        self.textEvents.sort(key = lambda x: x.startTime.value)

        _init_events(self.scaleXEvents)
        _init_events(self.scaleYEvents)
        _init_events(self.colorEvents)
        _init_events(self.textEvents)

@dataclass
class ControlItem:
    sval: float
    tval: float
    easing: int
    easingFunc: typing.Callable[[float], float] = rpe_easing.ease_funcs[0]
    next: ControlItem|None = None
    
    def __post_init__(self):
        self.easingFunc = geteasing_func(self.easing)

@dataclass
class ControlEvents:
    alphaControls: list[ControlItem]
    posControls: list[ControlItem]
    sizeControls: list[ControlItem]
    yControls: list[ControlItem]
    
    def __post_init__(self):
        self.alphaControls.sort(key = lambda x: x.sval)
        self.posControls.sort(key = lambda x: x.sval)
        self.sizeControls.sort(key = lambda x: x.sval)
        self.yControls.sort(key = lambda x: x.sval)
        self._inite(self.alphaControls)
        self._inite(self.posControls)
        self._inite(self.sizeControls)
        self._inite(self.yControls)
    
    def _inite(self, es: list[ControlItem]):
        for i, e in enumerate(es):
            if i != len(es) - 1:
                e.next = es[i + 1]
    
    def _gtvalue(self, s: float, es: list[ControlItem], default: float = 1.0):
        for e in es:
            if e.next is None:
                return e.sval
            if e.sval <= s <= e.next.sval:
                return e.easingFunc((s - e.sval) / (e.next.sval - e.sval)) * (e.next.tval - e.tval) + e.tval
        return default
    
    def gtvalue(self, x: float):
        return (
            self._gtvalue(x, self.alphaControls, 1.0),
            self._gtvalue(x, self.posControls, 0.0),
            self._gtvalue(x, self.sizeControls, 1.0),
            self._gtvalue(x, self.yControls, 0.0)
        )

@dataclass
class MetaData:
    RPEVersion: int
    offset: int
    name: str
    id: str
    song: str
    background: str
    composer: str
    charter: str
    level: str

@dataclass
class BPMEvent:
    startTime: Beat
    bpm: float

@dataclass
class JudgeLine:
    isCover: int
    Texture: str
    attachUI: str|None
    eventLayers: list[EventLayer]
    extended: Extended|None
    notes: list[Note]
    bpmfactor: float
    father: int|JudgeLine # in other object, __post_init__ change this value to a line
    zOrder: int
    controlEvents: ControlEvents
    
    playingFloorPosition: float = 0.0
    effectNotes: list[Note]|None = None
    
    def GetEventValue(self, t: float, es: list[LineEvent], default):
        for e in es:
            if e.startTime.value <= t <= e.endTime.value:
                if isinstance(e.start, float|int):
                    return tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start, e.end, e.easingFunc)
                elif isinstance(e.start, str):
                    return e.start
                elif isinstance(e.start, list):
                    r = tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[0], e.end[0], e.easingFunc)
                    g = tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[1], e.end[1], e.easingFunc)
                    b = tool_funcs.easing_interpolation(t, e.startTime.value, e.endTime.value, e.start[2], e.end[2], e.easingFunc)
                    return (r, g, b)
        return default
    
    @lru_cache
    def GetPos(self, t: float, master: Rpe_Chart) -> list[float, float]:
        linePos = [0.0, 0.0]
        for layer in self.eventLayers:
            linePos[0] += self.GetEventValue(t, layer.moveXEvents, 0.0)
            linePos[1] += self.GetEventValue(t, layer.moveYEvents, 0.0)
            
        if self.father != -1:
            try:
                sec = master.beat2sec(t, self.bpmfactor)
                fatherBeat = master.sec2beat(sec, self.father.bpmfactor)
                fatherPos = self.father.GetPos(fatherBeat, master)
                posabsValue = tool_funcs.getLineLength(*linePos, 0.0, 0.0)
                possitaValue = (
                    math.degrees(math.atan2(*linePos))
                    + sum([self.father.GetEventValue(fatherBeat, layer.rotateEvents, 0.0) for layer in self.father.eventLayers])
                )
                return list(map(lambda v1, v2: v1 + v2, fatherPos, tool_funcs.rotate_point(0.0, 0.0, 90 - possitaValue, posabsValue)))
            except IndexError:
                pass
            
        return linePos
    
    def GetSpeed(self, t: float):
        v = 0.0
        for layer in self.eventLayers:
            for e in layer.speedEvents:
                if e.startTime.value <= t <= e.endTime.value:
                    v += tool_funcs.linear_interpolation(t, e.startTime.value, e.endTime.value, e.start, e.end)
                    break # loop for other layers
        return v
    
    def GetState(self, t: float, defaultColor: tuple[int, int, int], master: Rpe_Chart) -> tuple[tuple[float, float], float, float, tuple[int, int, int], float, float, str|None]:
        "linePos, lineAlpha, lineRotate, lineColor, lineScaleX, lineScaleY, lineText"
        linePos = self.GetPos(t, master)
        lineAlpha = 0.0
        lineRotate = 0.0
        lineColor = defaultColor if not self.extended.textEvents else (255, 255, 255)
        lineScaleX = 1.0
        lineScaleY = 1.0
        lineText = None
        
        for layer in self.eventLayers:
            lineAlpha += self.GetEventValue(t, layer.alphaEvents, 0.0 if (t >= 0.0 or self.attachUI is not None) else -255.0)
            lineRotate += self.GetEventValue(t, layer.rotateEvents, 0.0)
        
        if self.extended:
            lineScaleX = self.GetEventValue(t, self.extended.scaleXEvents, lineScaleX)
            lineScaleY = self.GetEventValue(t, self.extended.scaleYEvents, lineScaleY)
            lineColor = self.GetEventValue(t, self.extended.colorEvents, lineColor)
            lineText = self.GetEventValue(t, self.extended.textEvents, lineText)
        
        return tool_funcs.conrpepos(*linePos), lineAlpha / 255, lineRotate, lineColor, lineScaleX, lineScaleY, lineText
    
    def GetNoteFloorPosition(self, t: float, n: Note, master: Rpe_Chart):
        l, r = master.beat2sec(t, self.bpmfactor), master.beat2sec(n.startTime.value, self.bpmfactor)
        return self.GetFloorPosition(*sorted((l, r)), master) * (-1.0 if l > r else 1.0)
    
    def GetFloorPosition(self, l: float, r: float, master: Rpe_Chart):
        fp = 0.0
        for layer in self.eventLayers:
            for e in layer.speedEvents:
                st, et = master.beat2sec(e.startTime.value, self.bpmfactor), master.beat2sec(e.endTime.value, self.bpmfactor)
                if l <= st <= r <= et:
                    v1, v2 = st, r
                elif st <= l <= et <= r:
                    v1, v2 = st, l
                elif l <= st <= et <= r:
                    v1, v2 = st, et
                elif st <= l <= r <= et:
                    v1, v2 = l, r
                else:
                    continue
                if e.start == e.end:
                    fp += (v2 - v1) * e.start
                else:
                    s1 = tool_funcs.linear_interpolation(v1, st, et, e.start, e.end)
                    s2 = tool_funcs.linear_interpolation(v2, st, et, e.start, e.end)
                    fp += (v2 - v1) * (s1 + s2) / 2
        return fp * 120 / 900

    def GetHoldLength(self, t: float, n: Note, master: Rpe_Chart):
        return (n.secet - n.secst) * self.GetSpeed(t) * 120 / 900

    def __hash__(self) -> int:
        return id(self)
    
    def __eq__(self, oth) -> bool:
        if isinstance(oth, JudgeLine):
            return self is oth
        return False

@dataclass
class Rpe_Chart:
    META: MetaData
    BPMList: list[BPMEvent]
    JudgeLineList: list[JudgeLine]
    
    combotimes: list[float]|None = None
    
    def __post_init__(self):
        self.BPMList.sort(key=lambda x: x.startTime.value)
        self.combotimes = []
        
        try: avgBpm = sum([e.bpm for e in self.BPMList]) / len(self.BPMList)
        except ZeroDivisionError: avgBpm = 140.0
        
        for line in self.JudgeLineList:
            for i, note in enumerate(line.notes):
                note.master_index = i
                note.masterLine = line
                note._init(self, avgBpm)
                if not note.isFake:
                    self.combotimes.append(note.secst if not note.ishold else max(note.secst, note.secet - 0.2))
                
            if line.father != -1:
                line.father = self.JudgeLineList[line.father]
            
            line.notes.sort(key=lambda x: x.startTime.value)
            line.effectNotes = [i for i in line.notes if not i.isFake]
        
        self.note_num = len([i for line in self.JudgeLineList for i in line.notes if not i.isFake])
        self.JudgeLineList.sort(key = lambda x: x.zOrder)
        self.combotimes.sort()
    
    def getCombo(self, t: float):
        l, r = 0, len(self.combotimes)
        while l < r:
            m = (l + r) // 2
            if self.combotimes[m] < t: l = m + 1
            else: r = m
        return l
    
    @cache
    def sec2beat(self, t: float, bpmfactor: float):
        beat = 0.0
        for i, e in enumerate(self.BPMList):
            bpmv = e.bpm * bpmfactor
            if i != len(self.BPMList) - 1:
                et_beat = self.BPMList[i + 1].startTime.value - e.startTime.value
                et_sec = et_beat * (60 / bpmv)
                
                if t >= et_sec:
                    beat += et_beat
                    t -= et_sec
                else:
                    beat += t / (60 / bpmv)
                    break
            else:
                beat += t / (60 / bpmv)
        return beat
    
    @cache
    def beat2sec(self, t: float, bpmfactor: float):
        sec = 0.0
        for i, e in enumerate(self.BPMList):
            bpmv = e.bpm * bpmfactor
            if i != len(self.BPMList) - 1:
                et_beat = self.BPMList[i + 1].startTime.value - e.startTime.value
                
                if t >= et_beat:
                    sec += et_beat * (60 / bpmv)
                    t -= et_beat
                else:
                    sec += t * (60 / bpmv)
                    break
            else:
                sec += t * (60 / bpmv)
        return sec

    def __hash__(self) -> int:
        return id(self)
    
    def __eq__(self, oth) -> bool:
        if isinstance(oth, JudgeLine):
            return self is oth
        return False
    
del typing, dataclass