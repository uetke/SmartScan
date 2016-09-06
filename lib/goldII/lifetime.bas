'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
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
#include .\globals.inc
dim data_Counter1[1000000] as long as fifo
dim data_Counter2[1000000] as long as fifo 
dim j, m, port, portt as integer
dim aom, aom_ON, aom_OFF as integer
dim new_timer, old_timer as long
dim new_timerr, old_timerr as long

init:
  ' init the counters
  cnt_enable(0000b)
  cnt_mode(1,0)
  cnt_mode(2,0)
  cnt_mode(3,0)
  cnt_mode(4,0)
  cnt_enable(1111b)
  j = 0
  m = 0
  port = par_Port
  portt = par_Portt
  aom = par_Aom
  aom_ON = 65536
  aom_OFF = 32768
  FIFO_Clear(178)
  FIFO_Clear(179)
  old_timer = cnt_read(port)
  new_timer = cnt_read(port)
  old_timerr = cnt_read(portt)
  new_timerr = cnt_read(portt)
event:  
  Inc j
  
  if(j=1) then
    dac(aom,aom_ON)
  else 
    if (j=par_Square) then
      dac(aom,aom_OFF)
      old_timer = cnt_read(port)
      old_timerr = cnt_read(portt)
    else 
      if (j>par_Square) then
        new_timer = cnt_read(port)
        new_timerr = cnt_read(portt)
        data_Counter1 = old_timer-new_timer
        data_Counter2 = old_timerr-new_timerr
        old_timer = new_timer
        old_timerr = new_timerr
        'Inc i
        ' Par_1 = i        
        if(j>=par_Num_ticks) then
          j=0
          Inc m
          if(m>=par_LifetimeIterations) then
            dac(aom,aom_OFF)
            end
          endif         
        endif
      endif
    endif
  endif
  
    

  

