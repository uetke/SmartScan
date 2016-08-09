'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 5
' Initial_Processdelay           = 1000
' Eventsource                    = External
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
' external_scan.bas
'
' trigger: external clock
' high priority

#include c:\adwin\adbasic\inc\adwgcnt.inc
#include .\globals.inc

dim new_timer as integer
dim data_Scan_params[15] as long
dim data_Scan_data[500000] as long as FIFO
dim data_dev_params[1000] as long
dim free as long
dim pix_done, temp as integer
dim i,j, port as integer
dim n_pixels as integer
dim old_timer[4] as long

Function input(dev_type,port) as long
  if (dev_type=21314873) then '21314873 is decimal for count
    CNT_LATCH(port)
    new_timer = cnt_readlatch(port)
    temp =  old_timer[port] - new_timer
    old_timer[port] = new_timer
    input = temp
  else
    if (dev_type=17882988) then '17882988 is decimal for analo
      input = adc(port)
    endif
  endif
EndFunction

init:
  pix_done = -1
  n_pixels = par_Scan_length
event:
  
  ' There should be one more trigger than pixels
  if (pix_done < 0) then
    ' At time 0 we do nothing apart from resetting the counters
    for j=1 to 4
      old_timer[j] = input(21314873,j)
      free = input(21314873,j)
    NEXT j
    j = 1
    pix_done = 0
  else
    ' At later triggers [time = (pix_done + 1) * delta_t] send the acquired data
    ' into the FIFO and check whether the scan is over.
    for i=1 to par_Num_devs
      data_Scan_data = input(data_dev_params[2*i-1],data_dev_params[2*i])
    NEXT i
    pix_done = pix_done + 1
    par_Pix_done = pix_done
    if (pix_done >= n_pixels) then
      end
    endif
  endif

