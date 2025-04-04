import os

# class ClassName(ExtendFromClassName): << you learn new things everyday, inheritance.

class UnknownOSError(Exception):
    """OS is neither NT nor POSIX"""

def xpfp(path, verbose=False):
    print(f"OS: [ {str(os.name).upper()} ]") if verbose == True else ''
    print(f"{path} to {os.name}-path") if verbose == True else ''
    # \\ = windows ss
    # /  = unix
    # replace \\ (windows) to / (unix)
    match os.name:
        case "nt":
            return path.replace("/","\\")
        case "posix":
            return path.replace("\\","/")
        case _:
            raise UnknownOSError('OS is neither NT nor POSIX, this is unlikely but it\'s funny that I have this here :skull:')