# PySoundBoard
Soundboard written in python as a hobby project.

I've always wanted a soundboard but I cant find one that is free to use.
So I made my own! Lmao.

Please refer to the issues tab.
# Disclaimer
Do note that **I do not own ANY OF THE AUDIO FILES** in SoundFiles Folder.

**However**, I made the "start.wav" myself. I'm Proud of it! :)

**Sounds/Music/Audio are owned by their respective owners.**

# Pre-Requisites
Requires **python** to be installed. **(Python 3.x+ & make sure you have Ttk/TKinter Ticked!)**

Requires **ttkthemes** to be installed for DarkMode. **OPTIONAL (pip install ttkthemes)**

Requires **pygame** to be installed. **(pip install pygame)**

For **ListAudioDevices.py**, it requires **sounddevice** to be installed. **OPTIONAL (pip install sounddevice)**

This is the default way of making this soundboard to work and it requires 2 things to be installed.

[VoiceMeeter - For routing multiple "mic" inputs to a virtual mic output](https://vb-audio.com/Voicemeeter/index.htm)

[VB-Cable Audio Device - Virtual Cable for PySoundBoard to output audio to.](https://vb-audio.com/Cable/index.htm)

# Setup VoiceMeeter

We first have to set these as our default Devices.
**Right-click** the **sound icon** on your taskbar and click **"Sounds"** (or **Volume Mixer** then click **system sounds icon**)

Click **"Recording"** Tab and set **"VoiceMeeter Output"** as your **Default Microphone**
![alt text](https://cdn.discordapp.com/attachments/903492607932518440/938089246672158790/unknown.png "Windows Recording Devices")

Once this is done let's move to setting up VoiceMeeter.

==========================================================

Look for **"HARDWARE INPUT 1"** and click **"Select Input Device"**

Choose the **device that you are using as a mic.** In my case, I am using my **headset's Microphone**, **"Epic G432 Mic (Logitech G432 Gaming Headset)"**

Worry not, you can choose any of them, **WDM** or **MME** or **KS**

If it doesn't work, switch to a different one. e.g. You selected **MME** and doesn't work, choose either **WDM** or **KS** if available.

==========================================================

Next is look for **"HARDWARE INPUT 2"** and click **"Select Input Device"**

Choose **KS : VB-Audio Point**

Next is to set an output device so you can hear the soundboard.

Look for **A1** at the **Top Right** of **VoiceMeeter Banana** and select your Headset or Speakers.

Worry not, you can choose any of them, **WDM** or **MME** or **KS**

If it doesn't work, switch to a different one. e.g. You selected **MME** and doesn't work, choose either **WDM** or **KS** if available.

==========================================================

Lastly, Below is an image of **MY VoiceMeeter Banana Setup**

You currently see **B1** in **Microphone (Hardware Input 1)** and **A1 & B1** in **SoundBoard (Hardware Input 2)** Enabled.

**B1** is the VIRTUAL Output Device, **"VoiceMeeter Output"**, we set as the Default Microphone earlier.

**A1** is the PHYSICAL Output Device, e.g. Speakers, Headset(s)

Copy the **B1, A1** Setup Shown in the image below.

![alt text](https://cdn.discordapp.com/attachments/903492607932518440/938077262027317279/unknown.png "VoiceMeeter Banana Completed Setup")

You're Done! (Hopefully, if everything went as described)

All you have to do now is run **SoundBoard_Main.py** and you should be able to hear something! Fingers Crossed! :D
