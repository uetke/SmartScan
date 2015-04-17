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
' Info_Last_Save                 = MN97  PHYSICS\carattino
'<Header End>
'Short routine for acquiring two analog signals in parallel or a single one with a high temporal resolution.
' The employed ADC is 14-bit
dim data_176[500000] as long
dim data_175[500000] as long
dim data_174[500000] as long

dim i as integer
dim j as integer
init:
  Set_Mux(1010111111b) 'Gain 4 = range -5V to 5V
  Sleep(65)
  i = 0
  j = 1
event:
  SelectCase j
    case 1 'Acquires X and Y channels
      if (i<Par_78) then
        Start_Conv(11000b)
        Wait_EOC(11000b)
        data_176[i] = ReadADC12(1) 'QPDx
        data_175[i] = ReadADC12(2) 'QPDy
        i = i + 1
      else
        j = 2
        i = 0
      endif
      
    case 2 ' Acquiring Z
      if (i=0) then
        Set_Mux(1010110111b) 'Gain 4 = range -5V to 5V
        Sleep(65)
      endif
      if (i<Par_78) then
        start_Conv(10000b)
        Wait_EOC(10000b)
        data_174[i] = ReadADC12(2) 'QPDz
        i = i + 1
      else
        end
      endif
  EndSelect