'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 10000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC166  MEETPC166\LION
'<Header End>
#include c:\adwin\adbasic\Inc\ADwinGoldII.inc

init:
  globaldelay = 400 '= 40 ms
  ' init the counters
  cnt_mode(1,0)
  cnt_mode(2,0)
  cnt_mode(3,0)
  cnt_mode(4,0)
  
  
  Conf_DIO(1100b)
  FIFO_Clear(200)
  
event:
  end
