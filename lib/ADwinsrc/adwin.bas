'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 25000
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
#include c:\adwin\adbasic\inc\adwgcnt.inc
#include .\globals.inc
dim new_timer as integer
dim data_Scan_data[500000] as long as FIFO
dim data_dev_params[1000] as long
dim value, free, garbage as long
dim i,j,dev_type, port, m, k as integer
dim data_Scan_params[15] as long
dim start[3], port[3], pix_dims[3], cur_pix[3], increment[3], old_timer[4] as long 'format is [x,y,z]"
dim pix_done, output , temp as integer
dim ltemp as long
dim nopcount as integer

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
  'Conf_DIO(1100b)
  'reset_event
  ' init the counters
  'cnt_enable(0)
  'cnt_clear(15)
  'cnt_mode(0)
  'cnt_set(15)
  'cnt_inputmode(0)
  'cnt_enable(15)
  'FIFO_Clear(200)
  i = 0
  k = 1
  'for j=1 to 4
  '  old_timer[j] = 0
  '  free = input(21314873,j)
  'NEXT j
  pix_done = -1
  for j=1 to 3
    port[j]=data_Scan_params[j]
    start[j]=data_Scan_params[j+3]
    pix_dims[j]=data_Scan_params[j+6]
    cur_pix[j] = 0
    increment[j] = data_Scan_params[j+9]
  NEXT j
  j = 1
event:
  SelectCase par_Case
    case CASE_DAC
      dac(par_Port, par_Input_value)
      end

    case CASE_ADC
      par_Output_value = adc(par_Port)
      end

    case CASE_ACQ
      if (pix_done < 0) then
        for j=1 to 4
          old_timer[j] = input(21314873,j)
          free = input(21314873,j)
        NEXT j
        pix_done = 0
      else
        for j=1 to par_Num_devs
          data_Scan_data = input(data_dev_params[2*j-1],data_dev_params[2*j])
        NEXT j
        pix_done = pix_done + 1
        par_Pix_done = pix_done
        if (pix_done = par_Num_ticks) then
          end
        endif
      endif
      
    case CASE_ACQ_MULTI
      'For acquiring signals of several devices, but keeping in mind higher temporal accuracy'
      'The acquisition is done in series (first one device, then another, etc.'

      data_Scan_data = input(data_dev_params[2*j-1],data_dev_params[2*j])
      Inc i
      if(i = par_Num_ticks+1) then
        Inc j
        i = 1
        if (j=Par_71+1) then
          end
        endif
      endif


    case CASE_SCAN
      'doing a scan'
      if (pix_done < 0) then
        dac(port[1],start[1])
        for j=1 to 4
          old_timer[j] = input(21314873,j)
          free = input(21314873,j)
        NEXT j
        j = 1
        if (start[2]>-1) then
          dac(port[2],start[2])
        endif
        if (start[3]>-1) then
          dac(port[3],start[3])
        endif
        pix_done = 0
        nopcount = 0
      else
        if (( cur_pix[1] = 0 ) and ( nopcount < NEWLINE_DELAY )) then
          ' don't move, throw away the pixel.
          ' we do this NEWLINE_DELAY times at the start of each line in order to
          ' compensate for the jump.
          for i=1 to par_Num_devs
            ltemp = input(data_dev_params[2*i-1],data_dev_params[2*i])
          NEXT i
          nopcount = nopcount + 1
        else
          ' now we're moving normally (again). Send data to the FIFO (and so on)
          nopcount = 0
          for i=1 to par_Num_devs
            data_Scan_data = input(data_dev_params[2*i-1],data_dev_params[2*i])
          NEXT i
          pix_done = pix_done + 1
          par_Pix_done = pix_done
          if (pix_done = pix_dims[1] * pix_dims[2] * pix_dims[3]) then
            end
          endif
          if (cur_pix[1] < pix_dims[1]-1) then
            cur_pix[1] = cur_pix[1] + 1
            output = start[1] + increment[1]*cur_pix[1]
            dac(port[1],output)
          else
            if (cur_pix[2] < pix_dims[2]-1) then
              cur_pix[2] = cur_pix[2] + 1
              par_mystery = cur_pix[1]
              output = start[2] + increment[2]*cur_pix[2]
              cur_pix[1] = 0
              dac(port[1],start[1])
              dac(port[2],output)
            else
              if (cur_pix[3] < pix_dims[3]-1) then
                cur_pix[3] = cur_pix[3] + 1
                output = start[3] + increment[3]*cur_pix[3]
                cur_pix[1] = 0
                cur_pix[2] = 0
                dac(port[1],start[1])
                dac(port[2],start[2])
                dac(port[3],output)
              endif
            endif
          endif
        endif
      endif


    case CASE_DIG_IN
      par_Output_value = digin_word()
      end

    case CASE_DIG_OUT
      set_digout(par_Port)
      end

    case CASE_DIG_CLEAR
      clear_digout(par_Port)
      end

  EndSelect
