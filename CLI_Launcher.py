#
# Chat GPT Generated code because I'm too lazy
# to look for what available terminal emulators
# 
# This is to cover Linux/MacOS side of things
#

import shutil, subprocess, platform, xpfpath, sys
from shlex import quote
def cliLauncher(command, verbose=True):
    """
    ## Syntax:
    - /path/to/executable --flag value
    > --> ["/path/to/executable", "--flag", "value"]
    """
    system = platform.system()

    # Normalize command to string
    # convert / to \\ and vice versa
    if isinstance(command, (list, tuple)):
        command = xpfpath.xpfp(" ".join(quote(str(arg)) for arg in command))
    elif not isinstance(command, str):
        raise TypeError("command must be str or list/tuple of str")

    if verbose:
        print(f"[INFO] Detected OS: {system}")
        print(f"[INFO] Command to run: {command}")

    match system:
        case "Linux":
            # Extended list of Linux terminals
            terminals = ["gnome-terminal","konsole","xfce4-terminal","lxterminal","xterm","tilix","alacritty","mate-terminal","terminator","kitty","eterm","st","rxvt","urxvt","hyper","wezterm","cool-retro-term","deepin-terminal","qterminal","guake","tilda","yakuake",
            ]

            terminal = next((t for t in terminals if shutil.which(t)), None)

            if terminal:
                if verbose:
                    print(f"[INFO] Using terminal emulator: {terminal}")
            else:
                print("[WARN] No supported terminal emulator found. Running in current shell...")
                subprocess.run(["bash", "-c", command])
                return

            match terminal:
                case "gnome-terminal" | "xfce4-terminal" | "mate-terminal" | "tilix":
                    subprocess.Popen([terminal, "--", "bash", "-c", command])
                case "konsole":
                    subprocess.Popen([terminal, "-e", f"bash -c '{command}'"])
                case "xterm" | "lxterminal" | "terminator" | "alacritty" | "kitty" | "st" | "rxvt" | "urxvt" | "qterminal":
                    subprocess.Popen([terminal, "-e", f"bash -c '{command}'"])
                case "wezterm":
                    subprocess.Popen([terminal, "start", "--", "bash", "-c", command])
                case "guake" | "tilda" | "yakuake":
                    subprocess.Popen([terminal, "-e", f"bash -c '{command}'"])
                case "hyper" | "cool-retro-term" | "deepin-terminal" | "eterm":
                    subprocess.Popen([terminal, "-e", f"bash -c '{command}'"])
                case _:
                    print(f"[WARN] Terminal {terminal} is detected but not fully supported. Running in current shell...")
                    subprocess.run(["bash", "-c", command])

        case "Darwin":  # macOS
            try:
                if verbose:
                    print("[INFO] Launching macOS Terminal.app")
                apple_script = f'''
                tell application "Terminal"
                    do script "{command}"
                    activate
                end tell
                '''
                subprocess.Popen(["osascript", "-e", apple_script])
            except Exception as e:
                print(f"[ERROR] macOS Terminal failed: {e}\n[INFO] Running directly instead.")
                subprocess.run(["bash", "-c", command])

        case "Windows":
            if verbose:
                print("[INFO] Windows detected — running command directly in current console")
            subprocess.run(command, shell=True)

        case _:
            print(f"[WARN] Unsupported OS: {system}. Running in current shell...")
            subprocess.run(command, shell=True)
            
sys.argv.remove(sys.argv[0])
if sys.argv != []:
    cliLauncher(sys.argv)
else:
    print('[ERROR] No Arguments provided.')