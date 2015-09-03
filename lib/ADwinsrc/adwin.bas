'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 9
' Initial_Processdelay           = 25000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = MN97  PHYSICS\carattino
'<Header End>
#include c:\adwin\adbasic\inc\adwgcnt.inc
dim new_timer as integer
dim data_200[500000] as long as FIFO
dim data_198[1000] as long
dim value, free, garbage as long
dim i,j,dev_type, port, m, k as integer
dim data_199[15] as long
dim start[3], port[3], pix_dims[3], cur_pix[3], increment[3], old_timer[4] as long 'format is [x,y,z]" 
dim pix_done, output , temp as integer

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
  i = 1
  k = 1
  for j=1 to 4
    old_timer[j] = 0
    free = input(21314873,j)
  NEXT j
  pix_done = -1
  for j=1 to 3
    port[j]=data_199[j]
    start[j]=data_199[j+3]
    pix_dims[j]=data_199[j+6]
    cur_pix[j] = 0
    increment[j] = data_199[j+9]
  NEXT j
event:
  SelectCase par_80
    case 1
      dac(par_74, par_75)
      end
      
    case 2 
      par_73 = adc(par_74)
      end
      
    case 3
      for j=1 to par_71
        data_200 = input(data_198[2*j-1],data_198[2*j])
      NEXT j 
      if (i = par_78) then
        end
      endif
      i = i + 1
    
    case 33
      'For acquiring signals of several devices, but keeping in mind higher temporal accuracy'
      'The acquisition is done in series (first one device, then another, etc.'
      for j=1 to par_71
        do 
          data_200 = input(data_198[2*j-1],data_198[2*j])
          Inc i
        until (i = par_78)
        i = 1  
      next j
      
      
    case 4
      'doing a scan'
      if (pix_done < 0) then
        dac(port[1],start[1])
        if (start[2]>-1) then
          dac(port[2],start[2])
        endif
        if (start[3]>-1) then   
          dac(port[3],start[3])
        endif
        pix_done = 0
      else
        if (k = 2) then
          k = 1
          for i=1 to par_71
            data_200 = input(data_198[2*i-1],data_198[2*i])
          NEXT i
          pix_done = pix_done + 1
          par_79 = pix_done
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
              par_77 = cur_pix[1]
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
        else
          for i=1 to par_71
            garbage = input(data_198[2*i-1],data_198[2*i])
          NEXT i
          k = 2
        endif
      endif
     
    
    case 5
      par_73 = digin_word()
      end
    
    case 6
      set_digout(par_74)
      end
    
    case 7 
      clear_digout(par_74)
      end
    
  EndSelect
