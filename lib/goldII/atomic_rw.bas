'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 6
' Initial_Processdelay           = 2000
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
#include c:\adwin\adbasic\Inc\ADwinGoldII.inc
#include .\globals.inc

'
' atomic_rw.bas
''''''''''''''''
' simple atomic operations reading or writing from analog or
' digital ports 
' 
' This functionality is duplicated in adwin.bas. This process uses
' different registers to transmit parameters to avoid conflict
' (postfix "6")

init:
  
event:
  SelectCase par_Case6
      
    case CASE_DAC
      dac(par_Port6, par_Input_value6)
      end

    case CASE_ADC
      par_Output_value6 = adc(par_Port6)
      end
      
    case CASE_DIG_IN
      par_Output_value6 = digin_word1()
      end

    case CASE_DIG_OUT
      par_digout_status = par_digout_status Or Shift_Left(1, par_Port6)
      Digout_Word2(par_digout_status)
      par_Output_value6 = par_digout_status
      'Digout(par_Port6,1)
      end

    case CASE_DIG_CLEAR
      par_digout_status = par_digout_status And Not(Shift_Left(1, par_Port6))
      Digout_Word2(par_digout_status)
      'Digout(par_Port6,0)
      par_Output_value6 = par_digout_status
      end
  EndSelect



