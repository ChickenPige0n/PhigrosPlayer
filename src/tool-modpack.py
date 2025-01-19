import fix_workpath as _

import json
import typing
from sys import argv
from os import popen

import UnityPy
import UnityPy.classes
import UnityPy.files
import UnityPy.streams
from pydub import AudioSegment
from PIL import Image, ImageFilter

import tempdir

if len(argv) < 6:
    print("Usage: tool-modpack <mod-list> <info> <extended-info> <apk-unpack-dir> <output-dir>")
    raise SystemExit

def loadbundle(fn: str) -> UnityPy.files.BundleFile:
    fp = f"{argv[4]}/assets/aa/Android/{fn}"
    env = UnityPy.load(fp)
    return list(env.files.values())[0]

def savebundle(bundle: UnityPy.files.BundleFile, fn: str):
    fp = f"{argv[5]}/{fn}"
    with open(fp, "wb") as f:
        f.write(bundle.save("lz4"))

def findinfo_byname(name: str):
    for i in info:
        if i["songName"] == name:
            return i
    return None

def findexinfo_byinfo(iitem: dict, key: str):
    for i in extended_info:
        if i["key"] == iitem["soundIdBak"] + "/" + key:
            return i
    return None

def putimto_bundle(bundle: typing.Optional[UnityPy.files.BundleFile], im: Image.Image, pid: int):
    if bundle is None: return
    for name, f in bundle.files.items():
        if isinstance(f, UnityPy.files.SerializedFile):
            for pid2, asset in f.files.items():
                    asset: UnityPy.files.ObjectReader
                    realasset = asset.read()
                    if isinstance(realasset, UnityPy.classes.Texture2D):
                        realasset.image = im

def fail(mod: dict):
    print(f"Failed to process mod: {mod["name"]}")

modlist = json.load(open(argv[1], "r", encoding="utf-8"))
info = json.load(open(argv[2], "r", encoding="utf-8"))
extended_info = json.load(open(argv[3], "r", encoding="utf-8"))

for mod in modlist:
    match mod["type"]:
        case "Chart":
            iitem = findinfo_byname(mod["name"])
            if iitem is None:
                fail(mod)
                continue
            
            exiitem = findexinfo_byinfo(iitem, f"Chart_{mod["level"]}.json")
            if exiitem is None:
                fail(mod)
                continue
            
            bundle = loadbundle(exiitem["fn"])
            for name, f in bundle.files.items():
                f: UnityPy.files.SerializedFile
                for pid, asset in f.files.items():
                    asset: UnityPy.files.ObjectReader
                    if pid == exiitem["path_id"]:
                        textasset: UnityPy.classes.TextAsset = asset.read()
                        rawchart = textasset.script.tobytes()
                        rawdata: bytes = asset.get_raw_data().tobytes()
                        content = open(mod["content_path"], "rb").read()
                        moded = rawdata.replace(rawchart, content)
                        size = len(rawchart).to_bytes(4, "little")
                        newsize = len(content).to_bytes(4, "little")
                        asset.set_raw_data(memoryview(moded.replace(size, newsize, 1)))
                        
            savebundle(bundle, exiitem["fn"])
        
        case "Audio":
            iitem = findinfo_byname(mod["name"])
            if iitem is None:
                fail(mod)
                continue

            exiitem = findexinfo_byinfo(iitem, "music.wav")
            if exiitem is None:
                fail(mod)
                continue
            
            tdir = tempdir.createTempDir()
            AudioSegment.from_file(mod["content_path"]).export(f"{tdir}/music.ogg", format="ogg")
            popen(f".\\oggvorbis2fsb5.exe \"{tdir}/music.ogg\" \"{tdir}/music.fsb\"").read()

            bundle = loadbundle(exiitem["fn"])
            for name, f in bundle.files.items():
                if isinstance(f, UnityPy.streams.EndianBinaryReader):
                    f.view = memoryview(open(f"{tdir}/music.fsb", "rb").read())
            
            savebundle(bundle, exiitem["fn"])
            
        case "Ill":
            iitem = findinfo_byname(mod["name"])
            if iitem is None:
                fail(mod)
                continue
            
            im = Image.open(mod["content_path"])
            if im.width / im.height != 2048 / 1080:
                print(f"Warning: Image aspect ratio is not 2048:1080 for mod: {mod["name"]}.")
                im = im.resize((2048, 1080))
            
            i1, i2, i3 = (
                findexinfo_byinfo(iitem, "IllustrationBlur.png"),
                findexinfo_byinfo(iitem, "Illustration.png"),
                findexinfo_byinfo(iitem, "IllustrationLowRes.png"),
            )
            b1, b2, b3 = loadbundle(i1["fn"]), loadbundle(i2["fn"]), loadbundle(i3["fn"])
            
            putimto_bundle(b1, im.filter(ImageFilter.GaussianBlur(10)).resize((256, 135)), i1["path_id"])
            putimto_bundle(b2, im, i2["path_id"])
            putimto_bundle(b3, im.resize((512, 270)), i3["path_id"])
            
            savebundle(b1, i1["fn"])
            savebundle(b2, i2["fn"])
            savebundle(b3, i3["fn"])
            
        case _:
            print(f"Unknown mod type: {mod["type"]}")
            