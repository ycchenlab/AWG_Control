# **************************************************************************
# Written in May, 2022
# Control program written by KHC in Spring, 2022 @ Lab330 in IAMS, AS
#
# **************************************************************************
# 
# This program handles the communication with the Spectrum Instrument AWG to output the desired RF signal
# to drive the 2D-AOD. The information of the signal waveform is input to the program as an external .txt file.
# In the future, the user may choose to integrate this program into some larger program that also generates the 
# required waveform information. In that case, the user may consider changing the data input to be some Python datatypes
# directly, instead of writing it to a .txt file and read it out again, which might take some additional time. 
# The current operation mode is cyclic replay. That is, after the data is finished being played, the program will
# replay the whole waveform (for both channels) over and over again until the user hit esc to terminate the program.
# If the user wants to modify how many times the signal waveform will be replayed, he or she may set llLoops to the desired value
# 
# Please note that prior to executing this program, the user should check that a .txt file describing the properties of the waveform
# is present and ready to be read by this program. 
#
# Documentation for the API as well as a detailed description of the hardware
# can be found in the manual for each device which can be found on our website:
# https://www.spectrum-instrumentation.com/products/details/M4i6622-x8.php
#
# Further information can be found online in the Knowledge Base:
# https://www.spectrum-instrumentation.com/en/knowledge-base-overview
#
# **************************************************************************

from pyspcm import *
from spcm_tools import *
from aux_functions_20220504 import read_setup_from_txt, cubic_interp_freq_list
import sys
import math 
import msvcrt

def lKbhit():
    return ord(msvcrt.getch()) if msvcrt.kbhit() else 0
# open card
# uncomment the second line and replace the IP address to use remote
hCard = spcm_hOpen (create_string_buffer (b'/dev/spcm0'))
if hCard == None:
    sys.stdout.write("no card found...\n")
    exit (1)

#reset
spcm_dwSetParam_i32 (hCard, SPC_M2CMD, M2CMD_CARD_RESET)
# (khc) read in the required testing parameters from the .txt file
txt_path = 'test_gen_mixed_freq_list_1_rel_phase.txt'
txt_path_2 = 'test_gen_mixed_freq_list_2_rel_phase.txt'
R, time, freq_list_1, freq_list_1_2, time_list, amp_list_1, phase_list_1 = read_setup_from_txt(txt_path)
R2, time2, freq_list_2, freq_list_2_2, time_list_2, amp_list_2, phase_list_2 = read_setup_from_txt(txt_path_2)

# read type, function and sn and check for D/A card
lCardType = int32 (0)
spcm_dwGetParam_i32 (hCard, SPC_PCITYP, byref (lCardType))
lSerialNumber = int32 (0)
spcm_dwGetParam_i32 (hCard, SPC_PCISERIALNO, byref (lSerialNumber))
lFncType = int32 (0)
spcm_dwGetParam_i32 (hCard, SPC_FNCTYPE, byref (lFncType))

sCardName = szTypeToName (lCardType.value)
if lFncType.value == SPCM_TYPE_AO:
    sys.stdout.write("Found: {0} sn {1:05d}\n".format(sCardName,lSerialNumber.value))
else:
    sys.stdout.write("This is an example for D/A cards.\nCard: {0} sn {1:05d} not supported by example\n".format(sCardName,lSerialNumber.value))
    spcm_vClose (hCard);
    exit (1)

# set sample rate, no clock output
if ((lCardType.value & TYP_SERIESMASK) == TYP_M4IEXPSERIES) or ((lCardType.value & TYP_SERIESMASK) == TYP_M4XEXPSERIES):
    spcm_dwSetParam_i64 (hCard, SPC_SAMPLERATE, MEGA(R))
    sys.stdout.write("Sample rate set by the user\n")
else:
    spcm_dwSetParam_i64 (hCard, SPC_SAMPLERATE, MEGA(1))
    sys.stdout.write("Sample rate 1 \n")
spcm_dwSetParam_i32 (hCard, SPC_CLOCKOUT,   0)

# (khc) compute the size of the required memory
total_sample_L = R * time
mem_size = 32 * ( 1 + (total_sample_L // 32)) # the smallest unit of buffer sample points is 32

# setup the mode
llMemSamples = int64 (mem_size) ## buffer length in number of data points
llLoops = int64 (0) # number of loops, 0 means continuously (replay mode)
spcm_dwSetParam_i32 (hCard, SPC_CARDMODE,    SPC_REP_STD_SINGLE)
spcm_dwSetParam_i64 (hCard, SPC_CHENABLE,    CHANNEL0 | CHANNEL1) # change here to output on two channels
spcm_dwSetParam_i64 (hCard, SPC_MEMSIZE,     llMemSamples)
spcm_dwSetParam_i64 (hCard, SPC_LOOPS,       llLoops)
spcm_dwSetParam_i64 (hCard, SPC_ENABLEOUT0,  1)
spcm_dwSetParam_i64 (hCard, SPC_ENABLEOUT1,  1) # add this line to enable output of channel 1

lSetChannels = int32 (0)
spcm_dwGetParam_i32 (hCard, SPC_CHCOUNT,     byref (lSetChannels))
sys.stdout.write("The number of activated channels is: {:d}\n".format(lSetChannels.value))
lBytesPerSample = int32 (0)
spcm_dwGetParam_i32 (hCard, SPC_MIINST_BYTESPERSAMPLE,  byref (lBytesPerSample))
sys.stdout.write("The number of bytes per sample is: {:d}\n".format(lBytesPerSample.value))

# setup the trigger mode
# (SW trigger, no output)
spcm_dwSetParam_i32 (hCard, SPC_TRIG_ORMASK,      SPC_TMASK_SOFTWARE)
spcm_dwSetParam_i32 (hCard, SPC_TRIG_ANDMASK,     0)
spcm_dwSetParam_i32 (hCard, SPC_TRIG_CH_ORMASK0,  0)
spcm_dwSetParam_i32 (hCard, SPC_TRIG_CH_ORMASK1,  0)
spcm_dwSetParam_i32 (hCard, SPC_TRIG_CH_ANDMASK0, 0)
spcm_dwSetParam_i32 (hCard, SPC_TRIG_CH_ANDMASK1, 0)
spcm_dwSetParam_i32 (hCard, SPC_TRIGGEROUT,       0)
# set the output amplitude (in mV)
lChannel = int32 (0)
spcm_dwSetParam_i32 (hCard, SPC_AMP0 , int32 (1000))
spcm_dwSetParam_i32 (hCard, SPC_AMP1 , int32 (1000))

# setup software bufferlSetChannels
qwBufferSize = uint64 (llMemSamples.value * lBytesPerSample.value * lSetChannels.value)
sys.stdout.write("The buffer size is: {:d}\n".format(qwBufferSize.value))
# we try to use continuous memory if available and big enough
pvBuffer = c_void_p ()
qwContBufLen = uint64 (0)
spcm_dwGetContBuf_i64 (hCard, SPCM_BUF_DATA, byref(pvBuffer), byref(qwContBufLen))
sys.stdout.write ("ContBuf length: {0:d}\n".format(qwContBufLen.value))
if qwContBufLen.value >= qwBufferSize.value:
    sys.stdout.write("Using continuous buffer\n")
else:
    pvBuffer = pvAllocMemPageAligned (qwBufferSize.value)
    sys.stdout.write("Using buffer allocated by user program\n")

sys.stdout.write("llMemSamples: {0:d}\n".format(llMemSamples.value))
# calculate the data
pnBuffer = cast  (pvBuffer, ptr16)
lMaxADCValue = int32 (0)
spcm_dwGetParam_i32 (hCard, SPC_MIINST_MAXADCVALUE, byref (lMaxADCValue))
dwFS = uint32 (lMaxADCValue.value)
dwFShalf = uint32 (dwFS.value // 2)
sys.stdout.write("lMaxADCValue: {0:d}\n".format(lMaxADCValue.value))

end_sample_length = llMemSamples.value
L_sum = 0
for f1, f2, time, amp, phase in zip(freq_list_1, freq_list_1_2, time_list, amp_list_1, phase_list_1): 
    num_freq = len(f1)
    if max(f1) >= R/2 or max(f2) >= R/2:
        print('ERROR: The input frequency has to be less than 1/2 * sampling rate.')
        break
    L = R * time
    if (L_sum + L) >= end_sample_length:
        print('Data Memory too small. Please allocate more memory.')
        break
    interp_freq_list = []
    for i in range(num_freq):
        interp_freq_list.append(cubic_interp_freq_list(R, time, f1[i], f2[i]))
    for i in range(L_sum, L_sum + L, 1):
        signal = 0
        for j in range(num_freq): # compute the sum of the different frequency components
            signal = signal + amp[j] * math.sin(2 * math.pi * (i-L_sum) * interp_freq_list[j][i-L_sum] / R
                                                + phase[j])
        pnBuffer[2*i] = int16 (int(dwFShalf.value * signal))   
    L_sum = L_sum + L
# after the loop is complete, L_sum contains the number of data points for channel 0's output
print(L_sum)

L_sum_2 = 0
for f1, f2, time, amp, phase in zip(freq_list_2, freq_list_2_2, time_list_2, amp_list_2, phase_list_2):
    num_freq = len(f1)
    if max(f1) >= R2/2 or max(f2) >= R2/2:
        print('ERROR: The input frequency has to be less than 1/2 * sampling rate.')
        break
    L = R2 * time
    if (L_sum_2 + L) >= end_sample_length:
        print('Data Memory too small. Please allocate more memory.')
        break
    interp_freq_list = []
    for i in range(num_freq):
        interp_freq_list.append(cubic_interp_freq_list(R2, time, f1[i], f2[i]))
    for i in range(L_sum_2, L_sum_2 + L, 1): 
        signal = 0
        for j in range(num_freq): # compute the sum of the different frequency components
            signal = signal + amp[j] * math.sin(2 * math.pi * (i-L_sum_2) * interp_freq_list[j][i-L_sum_2] / R2
                                                + phase[j])
        pnBuffer[2*i+1] = int16 (int(dwFShalf.value * signal))
    L_sum_2 = L_sum_2 + L   
# after the loop is complete, L_sum_2 contains the number of data points for channel 1's output    
print(L_sum_2)

# pad 0 to those unused memories in the buffer (since the buffer length has to be a multiple of 32)
for i in range(L_sum + L_sum_2, end_sample_length, 1):
    pnBuffer[i] = int16 (0)

# we define the buffer for transfer and start the DMA transfer
sys.stdout.write("Starting the DMA transfer and waiting until data is in board memory\n")
spcm_dwDefTransfer_i64 (hCard, SPCM_BUF_DATA, SPCM_DIR_PCTOCARD, int32 (0), pvBuffer, uint64 (0), qwBufferSize)
spcm_dwSetParam_i32 (hCard, SPC_M2CMD, M2CMD_DATA_STARTDMA | M2CMD_DATA_WAITDMA)
sys.stdout.write("... data has been transferred to board memory\n")

dwError = spcm_dwSetParam_i32 (hCard, SPC_M2CMD, M2CMD_CARD_START | M2CMD_CARD_ENABLETRIGGER) 
if dwError != ERR_OK:
    spcm_dwSetParam_i32 (hCard, SPC_M2CMD, M2CMD_CARD_STOP)
    sys.stdout.write ("... Error: {0:d}\n".format(dwError))
    exit (1) 

# press esc to end this program    
sys.stdout.write ("\n key: ESC ... stop replay and end program\n\n")
while True:
    lKey = lKbhit ()
    if lKey == 27: # ESC
        spcm_dwSetParam_i32 (hCard, SPC_M2CMD, M2CMD_CARD_STOP)
        break
spcm_vClose (hCard);

