import wave,os, sys, struct, math

cover_path = "cover_audio.wav"
stego_path = "stego_audio_LSB.wav"
msg_path = "data.txt"
continuous_duration = 0.2


def convertMsgToBin(m):
	res = ''
	for i in m:
		x = str(format(ord(i), 'b'))
		x = ('0'*(8-len(x)))+x
		res = res+x
	return res

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
	print("\nrate", rate)

	duration = frames/rate 
	samples = frames * channels
	print("parameters", para)
	#print("channels", channels)
	#print("sample_width", sample_width)
	#print("frames", frames)
	#print("samples", samples)

	if(channels == 1):
		fmt = str(samples) + "B"
		mask = (1 << 8) - (1 << nlsb)
		minByte = -(1 << 8)
	elif(channels == 2):
		fmt = str(samples) + "h"
		mask = (1 << 15) - (1 << nlsb)
		minByte = -(1 << 15)
	else:
		raise ValueError("Number of channels is too large")

def count_availaible_slots(rawdata):
	global  minByte

	cnt = 0
	for i  in range(len(rawdata)):
		if(rawdata[i] != minByte):
			cnt = cnt+1
	#print("cnt", cnt, len(rawdata))
	return cnt

def stego(cover, msg, nlsb):
	global para, channels, sample_width, frames, samples, fmt, mask, minByte
	pre(cover)

	rawdata = list(struct.unpack(fmt, cover.readframes(frames)))
	#print("rawdata\n", rawdata[20000:30000])
	#print("rawdata\n", rawdata[64469:73301])
	#print("rawdata\n", rawdata[:50])
	#print(len(rawdata))

	#cnt availaible space
	availaible = count_availaible_slots(rawdata)
	slot_len = frames_continuous(continuous_duration)
	nslots = math.ceil(len(msg)/(slot_len*nlsb))
	print("\nnslots", nslots, "\nslot_len", slot_len, "\navailaible", availaible)
	skip = (availaible-(nslots*slot_len))//(nslots-1)

	print("skip", skip)


	cover_ind = 0
	msg_ind = 0
	res = []

	slot_ind = 0

	while(msg_ind < len(msg) and cover_ind<len(rawdata)):
		if(rawdata[cover_ind] == minByte):
			res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
			cover_ind += 1
			continue

		curr = ""
		while(len(curr)<nlsb):
			if(msg_ind < len(msg)):
				curr += msg[msg_ind]
			else:
				curr += "0"
			msg_ind += 1
		curr = int(curr)


		sign = 1
		if(rawdata[cover_ind] < 0):
			rawdata[cover_ind] *= -1
			sign = -1
		#print("Mask: ", mask)
		to_append = ((rawdata[cover_ind]&mask) | curr) * sign
		#print(rawdata[cover_ind], to_append)
		res.append(struct.pack(fmt[-1], to_append))
		cover_ind += 1
		slot_ind += 1
		if(slot_ind<slot_len):
			continue

		i = 0
		while(i<skip and cover_ind<len(rawdata)):
			if(rawdata[cover_ind] != minByte):
				i += 1
			res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
			cover_ind += 1
		slot_ind = 0
		

	if(msg_ind<len(msg)):
		print("\n\nMessage length too long. Terminating process")
		return 0
	while(cover_ind < len(rawdata)):
		res.append(struct.pack(fmt[-1], rawdata[cover_ind]))
		cover_ind += 1
	steg = wave.open(stego_path, "w")
	steg.setparams(para)
	steg.writeframes(b"".join(res))
	steg.close()

	print("\n\nStegonography complete. Data hidden in file", stego_path)  
	return 1


if __name__ == "__main__":

	cover = wave.open(cover_path, "r")

	with open(msg_path,'r') as file:
		msg = file.read()
	

	print("Size of message in bytes: ", len(msg))
	msg = convertMsgToBin(msg)
	print("Length of message in bits: ", len(msg))
	#print(msg)

	print("\nEnter number of LSBs to be used:")
	nlsb = int(input())

	stego(cover, msg, nlsb)
	cover.close()