'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 200
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC113  MEETPC113\Aquiles
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
dim data_177[200000] as long
dim data_176[200000] as long
dim j, i, port as integer
dim new_timer, old_timer as long
dim temp as long


init:
  reset_event
  ' init the counters
  cnt_enable(0)
  cnt_clear(15)
  cnt_mode(0)
  cnt_set(15)
  cnt_inputmode(0)
  cnt_enable(15)
  j = 1
  i = 1
  port = par_74
event:
  CNT_LATCH(port)
  new_timer = cnt_readlatch(port)
  temp =  old_timer - new_timer
  par_73 = new_timer
  old_timer = new_timer
  if (j>1) then
    if (temp>0) then
      data_177[i] = temp 
      data_176[i] = j
      i = i+1
    endif
  endif
  if(j=par_78+1) then
    par_78 = i
    end
  endif
  j = j+1
  par_77 = j
  par_76 = i
