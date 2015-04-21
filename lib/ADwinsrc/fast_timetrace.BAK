'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 25000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
dim data_177[2000000] as long
dim j, port as integer
dim new_timer, old_timer as long
dim temp as long


init:
  reset_event
  j = 1
  port = par_74
event:
  CNT_LATCH(port)
  new_timer = cnt_readlatch(port)
  temp =  old_timer - new_timer
  old_timer = new_timer
  if (j>1) then
    data_177[j-1] = temp 
  endif
  if(j=par_78+1) then
    end
  endif
  j = j+1
