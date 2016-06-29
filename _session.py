from lib.adq_mod import adq

time = 1
accuracy = 2
apdacc = 100E-6
apdtime = 1
lockInTime = 1
lockInAcc = 100E-6
device = {}
adw = adq(debug = 0)
runs = True # Continuous runs of the acquisition
timetrace_time = 15 # In seconds