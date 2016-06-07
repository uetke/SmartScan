'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 10
' Initial_Processdelay           = 30000000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 2
' Stacksize                      = 1000
' Info_Last_Save                 = MEETPC166  MEETPC166\LION
'<Header End>
#include c:\adwin\adbasic\inc\ADwinGoldII.inc

dim data_178[2003] as float as fifo 'counters
dim data_179[2003] as long as fifo
dim data_180[2003] as long as fifo
dim data_181[2003] as long as fifo
dim data_182[2003] as long as fifo 'adc
dim data_183[2003] as long as fifo
dim data_184[2003] as long as fifo
dim data_185[2003] as long as fifo
dim data_186[2003] as long as fifo
dim data_187[2003] as long as fifo
dim data_188[2003] as long as fifo
dim data_189[2003] as long as fifo
dim data_190[2003] as long as fifo
dim data_191[2003] as long as fifo
dim data_192[2003] as long as fifo
dim data_193[2003] as long as fifo
dim data_194[2003] as long as fifo
dim data_195[2003] as long as fifo
dim data_196[2003] as long as fifo
dim data_197[2003] as long as fifo
dim old_timer[4], new_timer[4], count[4] as long
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
  for j=1 to 4
    CNT_LATCH(j)
    new_timer[j] = cnt_read_latch(j)
    count[j] = old_timer[j] - new_timer[j]
    old_timer[j] = new_timer[j]
  
  NEXT j  
  
  data_178 = count[1]
  data_179 = count[2]
  data_180 = count[3]
  data_181 = count[4]
  
  for j = 1 to 16
    average[j] = 0
  NEXT j
  
  ' take every millisec the value fo all 16 ADCs with 12 bit resol.
  ' sum up to get the average and look for min and max value
  
  
  for c = 0 to 7
    set_mux1(c)  ' channel 2i +1, gain = 1
    set_mux2(c)  ' channel 2i +2, gain = 1
    io_sleep(200)' wait 60 us to settle MUX
    

    for j = 1 to 20
      start_conv(11b)   ' start bith 12 bit ADCs
      wait_eoc(11b)     ' wait for both 12 bit ADCs
      for n = 1 to 2      ' feed bith ADC values in corresponding arrays

        value_adc[2*c+n] = read_adc(n)
        '   value =readdac(n) 'adc12 gives cross talk (is too fast ?)
      NEXT n
      average[2*c+1] = average[2*c+1] + value_adc[2*c+1]
      average[2*c+2] = average[2*c+2] + value_adc[2*c+2]
      'io_sleep(200)
    NEXT j
    average[2*c+1] = average[2*c+1]/20
    average[2*c+2] = average[2*c+2]/20
  NEXT c 
  
  'maybe little overkill
  data_182 = average[1]
  data_183 = average[2]
  data_184 = average[3]
  data_185 = average[4]
  data_186 = average[5]
  data_187 = average[6]
  data_188 = average[7]
  data_189 = average[8]
  data_190 = average[9]
  data_191 = average[10]
  data_192 = average[11]
  data_193 = average[12]
  data_194 = average[13]
  data_195 = average[14]
  data_196 = average[15]
  data_197 = average[16]

      
