'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 100
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
#include .\globals.inc

' Configuration array containing triplets
' [ counter-port count-threshold shutter-port ]
' terminated by -1
' counter ports are 1-indexed, shutter (digout) ports are 0-indexed.
Dim data_protection_shutter_params[48] as Long

dim data_current_count[4] as long

dim i as long
dim stoploop as long
dim port, threshold, shutter as long
dim count as long
dim button_bits, old_button_bits, buttons_pressed, to_be_changed as long

init:
  
  
event:
  ' Check protection shutters
  i = 1
  stoploop = 0
  
  do
    port = data_protection_shutter_params[i]
    threshold = data_protection_shutter_params[i+1]
    shutter = data_protection_shutter_params[i+2]
    
    if (port >= 1) then
      if (data_current_count[port] >= threshold) then
        ' Close the shutter!
        clear_digout(shutter)
        par_digout_status = Peek(204000C0h)
      endif
    else
      stoploop = 1
    endif
    
    i = i + 3
    if (i >= 49) then
      stoploop = 1
    endif
    until (stoploop = 1)
  
  
    ' Check the buttons
    button_bits = digin_word()
    buttons_pressed = button_bits AND (button_bits XOR old_button_bits)
    to_be_changed = buttons_pressed AND par_shutter_button_mask
    digout_word(par_digout_status XOR to_be_changed)
    par_digout_status = Peek(204000C0h)
  
