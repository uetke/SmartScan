'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 10
' Initial_Processdelay           = 400
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 2
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
#include .\globals.inc

dim data_Counter1[2003] as long as fifo 'counters
dim data_Counter2[2003] as long as fifo
dim data_Counter3[2003] as long as fifo
dim data_Counter4[2003] as long as fifo
dim data_Analog1[2003] as long as fifo 'adc
dim data_Analog2[2003] as long as fifo
dim data_Analog3[2003] as long as fifo
dim data_Analog4[2003] as long as fifo
dim data_Analog5[2003] as long as fifo
dim data_Analog6[2003] as long as fifo
dim data_Analog7[2003] as long as fifo
dim data_Analog8[2003] as long as fifo
dim data_Analog9[2003] as long as fifo
dim data_Analog10[2003] as long as fifo
dim data_Analog11[2003] as long as fifo
dim data_Analog12[2003] as long as fifo
dim data_Analog13[2003] as long as fifo
dim data_Analog14[2003] as long as fifo
dim data_Analog15[2003] as long as fifo
dim data_Analog16[2003] as long as fifo
dim old_timer[4], new_timer[4] as long
dim data_current_count[4] as long
dim value_adc[16], average[16] as long
dim c,j,n as integer

init:
  'reset_event
  'globaldelay = 400 '= 40 ms
  ' init the counters
  'cnt_enable(0)
  'cnt_clear(15)
  'cnt_mode(0)
  'cnt_set(15)
  'cnt_inputmode(0)
  'cnt_enable(15) 
  'for j=1 to 4
  '  CNT_LATCH(j)
  '  old_timer[j] = cnt_readlatch(j)
  'NEXT j
  
event:
  CNT_LATCH(15)
  for j=1 to 4
    new_timer[j] = cnt_readlatch(j)
    data_current_count[j] = old_timer[j] - new_timer[j]
    old_timer[j] = new_timer[j]
  NEXT j  
  
  data_Counter1 = data_current_count[1]
  data_Counter2 = data_current_count[2]
  data_Counter3 = data_current_count[3]
  data_Counter4 = data_current_count[4]
  ' data_Digin1 = digin(0)
  ' data_Digin2 = digin(1)
  ' data_Digin3 = digin(2)
  ' data_Digin4 = digin(3)
  ' data_Digin5 = digin(4)
  ' data_Digin6 = digin(5)
  ' data_Digin7 = digin(6)
  ' data_Digin8 = digin(7)
  ' data_165 = digin(8)
  for j = 1 to 16
    average[j] = 0
  NEXT j
  
  ' take every millisec the value fo all 16 ADCs with 12 bit resol.
  ' sum up to get the average and look for min and max value
  
  
  for c = 0 to 7
    set_mux(c + c*8)   'channel 2i+1 and 2i+2
    sleep(600)           ' wait 60 us to settle MUX
    start_conv(11000b)   ' start bith 12 bit ADCs
    wait_eoc(11000b)     ' wait for both 12 bit ADCs
    for j = 1 to 20
      
      for n = 1 to 2      ' feed bith ADC values in corresponding arrays
        if (n=1) then
          '       value = readadc(1)
          value_adc[2*c+1] = readadc12(1)
        else
          '      value = readadc(2)   
          value_adc[2*c+2] = readadc12(2)   
        endif
        '   value =readdac(n) 'adc12 gives cross talk (is too fast ?)
      NEXT n
      average[2*c+1] = average[2*c+1] + value_adc[2*c+1]
      average[2*c+2] = average[2*c+2] + value_adc[2*c+2]
      sleep(600)
    NEXT j
    average[2*c+1] = average[2*c+1]/20
    average[2*c+2] = average[2*c+2]/20
  NEXT c 
  
  'maybe little overkill
  data_Analog1 = average[1]
  data_Analog2 = average[2]
  data_Analog3 = average[3]
  data_Analog4 = average[4]
  data_Analog5 = average[5]
  data_Analog6 = average[6]
  data_Analog7 = average[7]
  data_Analog8 = average[8]
  data_Analog9 = average[9]
  data_Analog10 = average[10]
  data_Analog11 = average[11]
  data_Analog12 = average[12]
  data_Analog13 = average[13]
  data_Analog14 = average[14]
  data_Analog15 = average[15]
  data_Analog16 = average[16]

      
