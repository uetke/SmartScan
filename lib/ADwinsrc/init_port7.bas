'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
#include .\globals.inc

init:
  reset_event
  ' init the counters
  cnt_enable(0)
  cnt_clear(15)
  cnt_mode(0)
  cnt_set(15)
  cnt_inputmode(0)
  cnt_enable(15) 
  
  dac(7,32768)
event:
  end
