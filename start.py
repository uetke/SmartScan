import sys, os, inspect

def adding_to_path(folder):
    """ Simple function for adding a folder to the path of Python in order to have available for import.
    Each folder needs an __init__.py file to be considered as a module.
    """

    # realpath() will make your script run, even if you symlink it :)
    # Adds the current folder to the path
    cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    # Adds the specified subfolder
    if type(folder) is list:
        for i in range(len(folder)):
            cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], folder[i])))
            if cmd_subfolder not in sys.path:
                sys.path.insert(0, cmd_subfolder)

        return True
    else:
        cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], folder)))
        if cmd_subfolder not in sys.path:
            sys.path.insert(0, cmd_subfolder)
        return True

if __name__ == "__main__":
    adding_to_path(['GUI', 'lib', '_private'])

    from GUI.MainWindow import App
    global app
    app = App(sys.argv)
    app.exec_()
