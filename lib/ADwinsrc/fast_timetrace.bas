'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 100
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 2
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
#include .\globals.inc
dim data_Timetrace[100000] as long 
dim data_QPDx[100000] as long 
dim j, i, port as integer
dim new_timer, old_timer as long
dim t1, t2 As Long

init:
  reset_event
  ' init the counters
  cnt_enable(0)
  cnt_clear(15)
  cnt_mode(0)
  cnt_set(15)
  cnt_inputmode(0)
  cnt_enable(15)
  j = 0
  i = 1
  port = par_Port
  do
    data_Timetrace[i] = 0
    data_QPDx[i] = 0
    Inc i
  until(i>=100000)
  i = 1
  old_timer = cnt_read(port)
  new_timer = cnt_read(port)
event:  
  Inc j
  new_timer = cnt_read(port)
  if (new_timer<>old_timer) then
    data_Timetrace[i] = old_timer-new_timer
    data_QPDx[i] = j
    old_timer = new_timer
    Inc i
  endif  
  if(j>=par_Num_ticks) then
    par_Pix_done = i
    end
  endif


