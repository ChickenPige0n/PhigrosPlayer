import check_bin as _

import sys
import time
from os.path import dirname
from json import load
from functools import cache

import numpy as np
from pydub import AudioSegment

import const
import chartfuncs_rpe

FR, SW, CH = 44100, 2, 2

def normalize(seg: AudioSegment):
    if seg.channels != CH: seg = seg.set_channels(CH)
    if seg.frame_rate != FR: seg = seg.set_frame_rate(FR)
    if seg.sample_width != SW: seg = seg.set_sample_width(SW)
    return seg

@cache
def seg2arr(seg: AudioSegment):
    return np.array(normalize(seg).get_array_of_samples()).astype(np.int32)
        
class AudioMixer:
    def __init__(self, base: AudioSegment):
        self.data = seg2arr(base)
    
    def mix(self, seg: AudioSegment, pos: float):
        arr = seg2arr(seg)
        start_pos = int(pos * FR * CH)
        end_pos = start_pos + len(arr)
        
        if end_pos > len(self.data):
            arr = arr[:len(self.data) - start_pos]
        
        self.data[start_pos:end_pos] += arr
    
    def get(self):
        return AudioSegment(
            data=self.data.clip(-32768, 32767).astype(np.int16).tobytes(),
            sample_width=SW,
            frame_rate=FR,
            channels=CH
        )

NoteClickAudios: dict[int, AudioSegment] = {
    const.NOTE_TYPE.TAP: AudioSegment.from_file("./resources/resource_default/click.ogg"),
    const.NOTE_TYPE.DRAG: AudioSegment.from_file("./resources/resource_default/drag.ogg"),
    const.NOTE_TYPE.HOLD: AudioSegment.from_file("./resources/resource_default/click.ogg"),
    const.NOTE_TYPE.FLICK: AudioSegment.from_file("./resources/resource_default/flick.ogg"),
}

ExtendedAudios: dict[str, AudioSegment] = {}

with open(sys.argv[1], "r", encoding="utf-8") as f:
    Chart = load(f)

if "META" in Chart and "formatVersion" not in Chart:
    rpeobj = chartfuncs_rpe.loadChartObject(Chart)
    Chart = {
        "formatVersion": 3,
        "offset": rpeobj.META.offset / 1000,
        "judgeLineList": [
            {
                "bpm": 1.875,
                "notesAbove": [
                    {
                        "time": note.secst,
                        "type": note.phitype,
                        "hitsound": note.hitsound
                    }
                    for note in line.notes if not note.isFake
                ],
                "notesBelow": []
            }
            for line in rpeobj.judgeLineList
        ]
    }

for line in Chart["judgeLineList"]:
    for note in line["notesAbove"] + line["notesBelow"]:
        if "hitsound" not in note: note["hitsound"] = None
        if note["hitsound"] is not None:
            if note["hitsound"] in ExtendedAudios: continue
            try:
                ExtendedAudios[note["hitsound"]] = AudioSegment.from_file(f"{dirname(sys.argv[1])}/{note["hitsound"]}")
            except Exception as e:
                print(f"Failed to load extended audio: {repr(e)}")
                ExtendedAudios[note["hitsound"]] = AudioSegment.silent(0)

delay = (-float(sys.argv[sys.argv.index("--delay") + 1])) if "--delay" in sys.argv else 0.0
delay += Chart["offset"]
Chart["offset"] = 0.0
for line in Chart["judgeLineList"]:
    for note in line["notesAbove"]:
        note["time"] += delay / (1.875 / line["bpm"])
    for note in line["notesBelow"]:
        note["time"] += delay / (1.875 / line["bpm"])

mainMixer = AudioMixer(AudioSegment.from_file(sys.argv[2]))
notesNum = sum(len(line["notesAbove"]) + len(line["notesBelow"]) for line in Chart["judgeLineList"])

getprogresstext = lambda n: f"\rprogress: {(n / notesNum * 100):.2f}%    {n}/{notesNum}"
print_once = lambda n, end="": print((text := getprogresstext(n)) + " " * (maxlength - len(text)), end=end)
maxlength = len(getprogresstext(notesNum))

st = time.perf_counter()
processed = 0
printtime = 1 / 15
lastprint = time.time() - printtime

for line_index, line in enumerate(Chart["judgeLineList"]):
    T = 1.875 / line["bpm"]
    notes = (line["notesAbove"] + line["notesBelow"]) if (line["notesAbove"] and line["notesBelow"]) else (
        line["notesAbove"] if line["notesAbove"] else line["notesBelow"]
    )
    for note_index, note in enumerate(notes):
        nt = note["time"] * T
        mainMixer.mix(NoteClickAudios[note["type"]] if note["hitsound"] is None else ExtendedAudios[note["hitsound"]], nt)
        processed += 1
        
        if time.time() - lastprint >= printtime:
            getprogresstext(processed)
            lastprint = time.time()

print_once(processed, end="\n")
    
print(f"Usage time: {(time.perf_counter() - st):.2f}s")
print("Exporting...")
mainMixer.get().export(sys.argv[3])
print("Done.")
