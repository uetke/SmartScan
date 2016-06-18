from devices.flipper import Flipper

# Initialize the motorized flipper mirror
try:
    flipper = Flipper(SerialNum=b'37863346')
    flipper_apd = 1 # Position going to the APD
    flipper_spec = 2 # Position going to the spectrometer
    flip = True
except:
    print('Problem initializing the flipper mirror')
    flip = False

    
  
if flip:
    if flipper_spec != flipper.getPos():
        flipper.goto(flipper_spec)
        print('flipp changed')
        print('take spectra')  


if flip:
    if flipper_spec != flipper.getPos():
        flipper.goto(flipper_apd)
        print('flipp changed')
        print('take time trace')
