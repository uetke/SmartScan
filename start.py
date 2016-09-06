import sys, os, inspect
from lib.adq_mod import adq
from lib.xml2dict import device
from lib import ScanApplication
from _private.set_debug import debug

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
    adding_to_path(['GUI', 'lib', '_private', 'special_tasks'])

    from GUI.MainWindow import App
    global app

    scan_app = ScanApplication()

    ### Initialize the adwin class ###
    session = scan_app.session
    # These variables should be erased. They are being kept for legacy support.
    dev_conf = 'config/config_devices.xml'
    session['dev_conf'] = 'config/config_devices.xml'
    session['device_names'] = device()
    ad = device(type='',name='Adwin') # Get the Adwin model from the config file
    model = ad.properties['model']
    dev_num = int(ad.properties['device_number'])
    session['adw'] = adq(dev_num,model,debug)
    if session['adw'].adw.Test_Version() != 0: 
        session['adw'].boot()
        
        print('Booting the ADwin...')
    if model == 'gold':
        session['adw'].init_port7()
        session['adw'].load('lib/adbasic/init_adwin.T98')
        session['adw'].start(8)
        session['adw'].wait(8)
        session['adw'].load('lib/adbasic/monitor.T90')
        session['adw'].load('lib/adbasic/atomic_rw.T96')
        session['adw'].load('lib/adbasic/adwin.T99')
    elif model == 'goldII':
        session['adw'].load('lib/adbasic/init_adwin.TB8')
        session['adw'].start(8)
        session['adw'].wait(8)
        session['adw'].load('lib/adbasic/monitor.TB0')
        session['adw'].load('lib/adbasic/atomic_rw.TB6')
        session['adw'].load('lib/adbasic/adwin.TB9')
    else:
        raise Exception('Model of ADwin not recognized')
    app = App(session,sys.argv)
    app.exec_()
