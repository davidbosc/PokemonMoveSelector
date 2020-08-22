import win32gui

def enum_win(windows_handle_id, result):
    win_text = win32gui.GetWindowText(windows_handle_id)
    result.append((windows_handle_id, win_text))

def getWindowHandleFromTitle(windowTitle):
    handle = 0
    out = []
    win32gui.EnumWindows(enum_win, out)
    for(windows_handle_id, win_text) in out:
        if windowTitle in win_text:
            handle = windows_handle_id
    return handle