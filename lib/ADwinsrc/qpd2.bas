'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 8
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = MEETPC113  MEETPC113\LION
'<Header End>
'Short routine for acquiring two analog signals in parallel or a single one with a high temporal resolution.
' The employed ADC is 14-bit
dim data_176[500000] as long
dim data_175[500000] as long
dim data_174[500000] as long

dim i as integer
dim j as integer
init:
  i = 0
  j = 1
event:
  SelectCase j
    case 1 'Acquires X and Y channels
      Par_80 = 1
      if (i<Par_78+1) then
        data_176[i] = ADC12(1,4) 'QPDx
        i = i + 1
      else
        j = 2
        i = 0
      endif
    case 2 'Acquires X and Y channels
      Par_80 = 2
      if (i<Par_78+1) then
        data_175[i] = ADC12(4,4) 'QPDy
        i = i + 1
      else
        j = 3
        i = 0
      endif
    case 3 ' Acquiring Z
      Par_80 = 3
      if (i<Par_78+1) then
        data_174[i] = ADC12(7,2) 'QPDz
        i = i + 1
      else
        end
      endif
  EndSelect
