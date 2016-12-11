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
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
#include .\globals.inc
dim j as integer
dim old_timer[4] as long
init:
  reset_event
  globaldelay = 400 '= 40 ms
  ' init the counters
  cnt_enable(0)
  cnt_clear(15)
  cnt_mode(0)
  cnt_set(15)
  cnt_inputmode(0)
  cnt_enable(15) 
  for j=1 to 4
    CNT_LATCH(j)
    old_timer[j] = cnt_readlatch(j)
  NEXT j
  
  Conf_DIO(1100b)
  FIFO_Clear(200)
  
  
  
event:
  end
