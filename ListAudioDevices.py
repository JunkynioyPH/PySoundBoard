import sounddevice

devs = sounddevice.query_devices()
print(devs) # Shows current output and input as well with "<" abd ">" tokens

for dev in devs:
    print(dev['name'])
input("\n\nPress any key(s) to exit")
