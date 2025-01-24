import fix_workpath as _
import init_logging as _

import typing
from os.path import exists, isfile, isdir

import yaml
from PIL import Image, ImageChops

import const
import dxsound

DEFAULT_PATH = "./resources/resource_default"
globalPack = None

class LoadResourcePackError(Exception): ...

def validFile(fp: str) -> bool:
    return exists(fp) and isfile(fp)

def validDir(fp: str) -> bool:
    return exists(fp) and isdir(fp)

def loadImage(fp: str) -> Image.Image:
    try:
        result = Image.open(fp)
        return result if result.mode == "RGBA" else result.convert("RGBA")
    except Exception as e:
        raise LoadResourcePackError(f"Load image \"{fp}\" fail: {repr(e)}")

def loadAudio(dir: str, fn: str) -> bytes:
    fp = f"{dir}/{fn}"
    if not validFile(fp): fp = f"{DEFAULT_PATH}/{fn}"
    
    try:
        return open(fp, "rb").read()
    except Exception as e:
        raise LoadResourcePackError(f"Load audio \"{fp}\" fail: {repr(e)}")

def cuthold(img: Image.Image, a: int, b: int):
    b = img.height - b
    end = img.crop((0, 0, img.width, a))
    body = img.crop((0, a, img.width, b))
    head = img.crop((0, b, img.width, img.height))
    return head, body, end

def putColor(color: tuple, im: Image.Image):
    return ImageChops.multiply(im, Image.new("RGBA", im.size, color))

def cutHitEffect(im: Image.Image, a: int, b: int):
    result = []

    for i in range(b):
        for j in range(a):
            result.append(im.crop((
                int(j * im.width / a),
                int(i * im.height / b),
                int((j + 1) * im.width / a),
                int((i + 1) * im.height / b),
            )))
    
    return result

def int2argb(x: int):
    return (
        (x >> 24) & 0xFF,
        (x >> 16) & 0xFF,
        (x >> 8) & 0xFF,
        x & 0xFF
    )

def argb2rgba(x: tuple):
    return (x[1], x[2], x[3], x[0] if x[0] != 0 else 255)

DEFAULT_PERFECT = 0xe1ffec9f
DEFAULT_GOOD = 0xebb4e1ff

class PhiraResourcePack:
    def __init__(self, fp: typing.Optional[str] = None):
        self.loaded = False
        if fp is not None: self.load(fp)
            
    def load(self, directory: str):
        if not validDir(directory):
            raise LoadResourcePackError(f"Resource pack directory \"{directory}\" not found.")
        
        image_names = (
            "click.png", "click_mh.png",
            "drag.png", "drag_mh.png",
            "flick.png", "flick_mh.png",
            "hold.png", "hold_mh.png",
            "hit_fx.png"
        )
        
        for i in image_names:
            if not validFile(f"{directory}/{i}"):
                raise LoadResourcePackError(f"Resource pack file \"{i}\" not found.")
        
        self.resource = {}
        
        self.resource["img"] = {
            k: loadImage(f"{directory}/{k}")
            for k in image_names
        }

        self.resource["audio"] = {
            k: loadAudio(directory, k)
            for k in ("click.ogg", "drag.ogg", "flick.ogg")
        }
        
        self.resource["endpath"] = f"{directory}/ending.mp3"
        if not validFile(self.resource["endpath"]):
            self.resource["endpath"] = f"{DEFAULT_PATH}/ending.mp3"

        info: dict = yaml.load(open(f"{directory}/info.yml", "r", encoding="utf-8"), Loader=yaml.FullLoader)
        
        self.resource["name"] = info.get("name", "name")
        self.resource["author"] = info.get("author", "author")
        self.resource["description"] = info.get("description", "description")
        self.resource["hitFx"] = info.get("hitFx", [5, 6])
        self.resource["holdAtlas"] = info.get("holdAtlas", [50, 50])
        self.resource["holdAtlasMH"] = info.get("holdAtlasMH", [65, 65])
        self.resource["hitFxDuration"] = info.get("hitFxDuration", 0.5)
        self.resource["hitFxScale"] = info.get("hitFxScale", 1.0)
        self.resource["hitFxRotate"] = info.get("hitFxRotate", False)
        self.resource["hitFxTinted"] = info.get("hitFxTinted", True)
        self.resource["hideParticles"] = info.get("hideParticles", False)
        self.resource["holdKeepHead"] = info.get("holdKeepHead", False)
        self.resource["holdRepeat"] = info.get("holdRepeat", False)
        self.resource["holdCompact"] = info.get("holdCompact", False)
        self.resource["colorPerfect"] = info.get("colorPerfect", 0xe1ffec9f)
        self.resource["colorGood"] = info.get("colorGood", 0xebb4e1ff)
        
        self.loaded = True
        self.effectDuration = self.resource["hitFxDuration"]
        self.effectScale = self.resource["hitFxScale"]
        self.effectRotate = self.resource["hitFxRotate"]
        self.hideParticles = self.resource["hideParticles"]
        self.holdKeepHead = self.resource["holdKeepHead"]
        self.holdCompact = self.resource["holdCompact"]
        self.effectFrameCount = self.resource["hitFx"][0] * self.resource["hitFx"][1]
        
        self.perfectColor = argb2rgba(int2argb(self.resource["colorPerfect"]))
        self.goodColor = argb2rgba(int2argb(self.resource["colorGood"]))
        self.perfectRGB = self.perfectColor[:-1]
        self.goodRGB = self.goodColor[:-1]
        self.perfectAlpha = self.perfectColor[-1]
        self.goodAlpha = self.goodColor[-1]
        
        self.isdefault_perfect = self.resource["colorPerfect"] == DEFAULT_PERFECT
        self.isdefault_good = self.resource["colorGood"] == DEFAULT_GOOD
        
    def createResourceDict(self) -> dict:
        result = {
            "Notes": {},
            "Note_Click_Effect": {},
            "Note_Click_Audio": {}
        }
        
        holdimg = self.resource["img"]["hold.png"]
        holdimg_mh = self.resource["img"]["hold_mh.png"]
        holdcroped = cuthold(holdimg, *self.resource["holdAtlas"])
        holdcroped_mh = cuthold(holdimg_mh, *self.resource["holdAtlasMH"])
        
        result["Notes"].update({
            "Tap": self.resource["img"]["click.png"],
            "Tap_dub": self.resource["img"]["click_mh.png"],
            "Drag": self.resource["img"]["drag.png"],
            "Drag_dub": self.resource["img"]["drag_mh.png"],
            "Flick": self.resource["img"]["flick.png"],
            "Flick_dub": self.resource["img"]["flick_mh.png"],
            "Hold_Head": holdcroped[0],
            "Hold_Head_dub": holdcroped_mh[0],
            "Hold_Body": holdcroped[1],
            "Hold_Body_dub": holdcroped_mh[1],
            "Hold_End": holdcroped[2],
            "Hold_End_dub": holdcroped_mh[2],
        })
        result["Notes"]["Bad"] = putColor((90, 60, 70), result["Notes"]["Tap"])
        
        hiteffects = cutHitEffect(self.resource["img"]["hit_fx.png"], *self.resource["hitFx"])
        
        if self.resource["hitFxTinted"]:
            result["Note_Click_Effect"].update({
                "Perfect": [putColor(self.perfectRGB, i) for i in hiteffects],
                "Good": [putColor(self.goodRGB, i) for i in hiteffects]
            })
        else:
            result["Note_Click_Effect"].update({
                "Perfect": hiteffects.copy(),
                "Good": hiteffects.copy()
            })
        
        result["Note_Click_Audio"].update({
            const.NOTE_TYPE.TAP: dxsound.directSound(self.resource["audio"]["click.ogg"]),
            const.NOTE_TYPE.DRAG: dxsound.directSound(self.resource["audio"]["drag.ogg"]),
            const.NOTE_TYPE.HOLD: dxsound.directSound(self.resource["audio"]["click.ogg"]),
            const.NOTE_TYPE.FLICK: dxsound.directSound(self.resource["audio"]["flick.ogg"])
        })
        
        return result

    def setToGlobal(self):
        global globalPack
        globalPack = self
        