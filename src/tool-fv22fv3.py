import json
from sys import argv

import light_tool_funcs

if len(argv) < 3:
    print("Usage: tool-fv22fv3 <input> <output>")
    raise SystemExit

with open(argv[1], "r", encoding="utf-8") as f:
    fv2 = json.load(f)

fv3 = light_tool_funcs.SaveAsNewFormat(fv2)

json.dump(fv3, open(argv[2], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
