def ensure_root ():
    import os

    euid = os.geteuid ()
    if euid != 0: raise Exception ("run as root")