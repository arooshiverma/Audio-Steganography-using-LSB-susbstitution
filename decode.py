import wave,os, sys, struct, math

stego_path = "stego_audio_LSB.wav"
output_path = "output.txt"
continuous_duration = 0.2

def decimalToBinary(n): 
    return bin(n).replace("0b", "") 

def frames_continuous(time):
	global rate
	return int(rate*time)

def pre(cover):

	global para, channels, sample_width, frames, samples, fmt, mask, minByte, rate, frame_per_min

	#Getting the metadata
	para = cover.getparams()
	channels = cover.getnchannels()
	sample_width = cover.getsampwidth()
	frames = cover.getnframes()
	rate = cover.getframerate()
	

	duration = frames/rate 
	samples = frames * channels
	#print("parameters", para)
	#print("channels", channels)
	#print("sample_width", sample_width)
	#print("frames", frames)
	#print("samples", samples)

	if(channels == 1):
		fmt = str(samples) + "B"
		minByte = -(1 << 7)
	elif(channels == 2):
		fmt = str(samples) + "h"
		minByte = -(1 << 15)
	else:
		raise ValueError("Number of channels is too large")

def count_availaible_slots(rawdata):
	global  minByte

	cnt = 0
	for i  in range(len(rawdata)):
		if(rawdata[i] != minByte):
			cnt = cnt+1
	#print("cnt", cnt)
	return cnt

def extract(stego, nlsb, size_in_bytes):
	global frames, samples, fmt, minByte

	pre(stego)

	msg = ""
	stego_index = 0
	rawdata = list(struct.unpack(fmt, stego.readframes(frames)))

	size = size_in_bytes*8
	msg_index = 0

	#cnt availaible space
	availaible = count_availaible_slots(rawdata)
	slot_len = frames_continuous(continuous_duration)
	nslots = math.ceil(size/(slot_len*nlsb))
	print("\nnslots", nslots, "\nslot_len", slot_len, "\navailaible frames", availaible)
	skip = (availaible-(nslots*slot_len))//(nslots-1)
	print("skip", skip)

	mask = (1 << nlsb) - 1

	slot_ind = 0
	while(msg_index < size):
		if(rawdata[stego_index]!=minByte):
			curr = decimalToBinary(abs(rawdata[stego_index]) & mask)
			msg += ('0'*(nlsb-len(curr))) + curr
			#print(rawdata[stego_index])
			msg_index += nlsb
		stego_index += 1
		slot_ind += 1
		if(slot_ind<slot_len):
			continue
		i = 0
		while(i<skip):
			if(rawdata[stego_index] != minByte):
				i += 1
			stego_index += 1
		slot_ind = 0

	msg = msg[:size]
	#print("msg length: ", len(msg))
	#print(msg)

	val = len(msg)//8
	chunks, chunk_size = len(msg), len(msg)//val
	new_string = [ msg[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
	dec_msg = ''
	for i in new_string:
		#print(i)
		dec_msg += chr(int(i, 2))

	with open(output_path,'w') as file:
		file.write(dec_msg)
	print("\nThe extracted message is written in", output_path)
	#print(dec_msg)


	
if __name__ == "__main__":
	stego = wave.open(stego_path, "r")

	print("Enter number of LSBs used: ")
	nlsb = int(input())

	print("Enter size of data in bytes: ")
	size = int(input())

	extract(stego, nlsb, size)

