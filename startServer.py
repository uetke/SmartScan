import sys, os, inspect
from lib.adq_mod import adq
from _private.set_debug import debug
from bottle import route, run, template, install, static_file, get
from start import adding_to_path
from lib.xml2dict import device

@route('/')
def index():
    """ Displays the index page. 
    """
    adding_to_path(['GUI', 'lib', '_private'])

    from GUI.MainWindow import App
    global app

    ### Initialize the adwin class ###
    session = {}
    # These variables should be erased. They are being kept for legacy support.
    dev_conf = 'config/config_devices.xml'
    session['dev_conf'] = 'config/config_devices.xml'
    par_conf = 'config/config_variables.xml'
    session['par_conf'] = 'config/config_variables.xml'
    session['device_names'] = device()
    ad = device(type='',name='Adwin') # Get the Adwin model from the config file
    model = ad.properties['model']
    model = 'gold'
    dev_num = ad.properties['device_number']
    session['adw'] = adq(dev_num,model,debug)
#     if session['adw'].adw.Test_Version() != 1: 
#         session['adw'].boot()
#         session['adw'].init_port7()
#         print('Booting the ADwin...')
#     if model == 'gold':
#         session['adw'].load('lib/adbasic/init_adwin.T98')
#         session['adw'].start(8)
#         session['adw'].wait(8)
#         session['adw'].load('lib/adbasic/monitor.T90')
#         session['adw'].load('lib/adbasic/adwin.T99')
#     elif model == 'goldII':
#         session['adw'].load('lib/adbasic/init_adwin.TB8')
#         session['adw'].start(8)
#         session['adw'].wait(8)
#         session['adw'].load('lib/adbasic/monitor.TB0')
#         session['adw'].load('lib/adbasic/adwin.TB9')
#     else:
#         raise Exception('Model of ADwin not recognized')
    app = App(session,sys.argv)
    app.exec_()    
    return template('index')

run(host='localhost', port=8080,reloader=True)
