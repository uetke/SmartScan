'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 1000
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
#include .\globals.inc

'Short routine for acquiring two analog signals in parallel or a single one with a high temporal resolution.
' The employed ADC is 14-bit
dim data_QPDx[500000] as long
dim data_QPDy[500000] as long
dim data_QPDz[500000] as long

dim i as integer
dim j as integer
init:
  Set_Mux(1111111111b) 'Gain 8 = range -1.255V to 1.25V
  Sleep(100)
  i = 0
  j = 1
event:
  SelectCase j
    case CASE_DAC 'Acquires X and Y channels
      Par_80 = 1
      if (i<Par_78) then
        Start_Conv(11000b)
        Wait_EOC(11000b)
        data_QPDx[i] = ReadADC12(1) 'QPDx
        data_QPDy[i] = ReadADC12(2) 'QPDy
        i = i + 1
      else
        j = 2
        i = 0
      endif
      
    case CASE_ADC ' Acquiring Z
      Par_79 = i
      if (i=0) then
        Set_Mux(0000110111b) '
        Sleep(100)
      endif
      if (i<Par_78) then
        start_Conv(10000b)
        Wait_EOC(10000b)
        data_QPDz[i] = ReadADC12(2) 'QPDz
        i = i + 1
      else
        end
      endif
  EndSelect
