'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = MN96  PHYSICS\kruidenberg
'<Header End>
' background log
' process ID: 7
' low  priority

'#include d:\lv work\hw interfaces\adwin\adbasic\global defs.bas
#include c:\adwin\adbasic\inc\adwgcnt.inc
'#include d:\lv work\hw interfaces\adwin\adbasic\sub-progs.bas

dim value as long
dim index, i as long
dim n1, c1 as long
dim old, new, change as long

#define local_adc_log            data_24
dim local_adc_log[50] as integer

#define global_adc_log            data_25
dim global_adc_log[50] as integer

#define cnt_log            data_26
dim cnt_log[4] as long

#define local_cnt_old            data_27
dim local_cnt_old[4] as long

#define cnt_old_pixel            data_28
dim  cnt_old_pixel[5] as long

#define local_adc_trace         data_29
dim local_adc_trace[16000] as integer

#define local_adc_sum           data_40
dim local_adc_sum[16] as integer

#define local_last_adc           data_41
dim local_last_adc[16] as integer

#define averages   20

init:

  globaldelay = 50 '= 5 ms
 
  index = 0
  conf_dio(12)
  
  ' init the counters
  cnt_enable(0)
  cnt_clear(15)
  cnt_mode(0)
  cnt_set(15)
  cnt_inputmode(0)
  cnt_enable(15)

  for i = 0 to 16000-1 
    local_adc_trace[i] = 0
  next i
  for i = 0 to 15 
    local_adc_sum[i] = 0
  next i
    
    
  
  
event:
  
  ' NB: aliasing in ADbasic parameter display of par_1 !!
  ' loop time does _not_ slow down ...
  inc(index)

  
  ' take every millisec the value fo all 16 ADCs with 12 bit resol.
  ' sum up to get the average and look for min and max value
  for c1 = 0 to 7
    set_mux(c1 + c1*8)   'channel 2i+1 and 2i+2
    sleep(600)           ' wait 60 us to settle MUX
    start_conv(11000b)   ' start bith 12 bit ADCs
    wait_eoc(11000b)     ' wait for both 12 bit ADCs
  
    '   start_conv(00011b)   ' start bith 16 bit ADCs
    '   wait_eoc(00011b)     ' wait for both 16 bit ADCs
  
   
    for n1 = 1 to 2      ' feed bith ADC values in corresponding arrays
      value = n1
      if (n1=1) then
        '       value = readadc(1)
        value = readadc12(1)
      else
        '      value = readadc(2)   
        value = readadc12(2)   
      endif
      '   value =readdac(n) 'adc12 gives cross talk (is too fast ?)
      i = c1 * 2 + (n1-1) 
         
      local_adc_sum[i] = local_adc_sum[i] + value - local_adc_trace[i*averages + index]
      local_adc_trace[i*averages + index] = value
      local_last_adc[i] = value
          
      '   local_adc_log[i*3 + 1] =  value + local_adc_log[i*3 + 1] 
      local_adc_log[i*3 + 1] =   local_adc_sum[i] /averages
      if (value < local_adc_log[i*3 +2]) then local_adc_log[i*3 +2] = value
      if (value > local_adc_log[i*3 +3]) then local_adc_log[i*3 +3] = value
    next n1
    
  next c1
  
  ' every "averages" iteration (= every 100 ms)
  '   a) get all counter values
  '   b) transfer local_adc_log (which changes every ms) to more static global adc_log and
  '      calculate average
  
  if (index = averages) then
  
    index = 0
    cnt_latch(15)
  
    for i = 1 to 4 
      value = cnt_readlatch(i)
      cnt_log[i] = -1 *(value - local_cnt_old[i])
      local_cnt_old[i] = value
    next i

    ' par_1 = local_adc_log[4]   ' i = 1
    ' par_2 = local_adc_log[10]   ' i = 3
    ' par_3 = local_adc_log[16]  ' i = 5


    for i = 0 to 15
      global_adc_log[i*3 + 1] = local_adc_log[i*3 + 1] ' / 100
      global_adc_log[i*3 + 2] = local_adc_log[i*3 + 2] 
      global_adc_log[i*3 + 3] = local_adc_log[i*3 + 3] 
       
      '   local_adc_log[i*3 + 1] = 0
      local_adc_log[i*3 + 2] = 65535
      local_adc_log[i*3 +3] = 0
    next i
  

  endif     
 
