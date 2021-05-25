win_width, win_height = 1600, 900
win_title = 'Smart PhotoSorter'
img_ext = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.j2k', '.j2p', '.jpx',
    '.dib', '.eps', '.psd', '.svg', '.tga', '.raw', '.ari', '.dpx', '.arw',
    '.srf', '.sr2', '.bay', '.crw', '.cr2', '.cr3', '.dng', '.dcr', '.kdc',
    '.erf', '.3fr', '.mef', '.mrw', '.nef', '.nrw', '.orf', '.ptx', '.pef',
    '.raf', '.rwl', '.dng', '.rw2', '.r3d', '.srw', '.x3f']

video_ext = [
    '.3g2', '.3gp', '.3gp2', '.3gpp', '.3gpp2', '.asf', '.asx', '.avi',
    '.bin', '.dat', '.drv', '.f4v', '.flv', '.gtp', '.h264', '.m4v', '.mkv',
    '.mod', '.moov', '.mov', '.mp4', '.mpeg', '.mpg', '.mts', '.rm', '.rmvb',
    '.spl', '.srt', '.stl', '.swf', '.ts', '.vcd', '.vid',
    '.vob', '.webm', '.wm', '.wmv', '.yuv']
ignor_ext = [".db"]
lang = "ru"

log_file = "log.txt"


def log_save(msg):
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"{msg}\n")
