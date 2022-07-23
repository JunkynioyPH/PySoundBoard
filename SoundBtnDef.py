import AudioDef as AD
# from AudioDef import *
import time

# Structure ["DisplayName,AD.DisplayName"]

ComDispName = []

for Files in AD.AudioFilesIndex:
    x, y = [], ""
    for letter in Files:
        if letter == ".":
            break
        else:
            x += letter
    y += "".join(x)
    print(y)

    ComDispName += [f"{y}","a"]

time.sleep(1)

print(ComDispName)

time.sleep(5)
