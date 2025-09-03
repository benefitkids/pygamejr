import tkinter as tk

def get_curr_screen_geometry():
    """
    Workaround to get the size of the current screen in a multi-screen setup.

    Returns:
        geometry (str): The standard Tk geometry string.
            [width]x[height]+[left]+[top]
    """
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    scaling_factor = root.tk.call('tk', 'scaling')
    root.destroy()
    return [ int(value) for value in geometry.split('+')[0].split('x')]
