# Audio-Steganography-using-LSB-susbstitution
Hiding textual data in audio file. Use encode.py to embed your data and decode.py to extract your data. The cover audio file name is 'cover_audio.wav'. The data to be embedded is stored in 'data.txt' file. 

The embedding result is stored in file 'stego_audio_LSB.wav'. The extraction process writes data extracted to the 'output.txt' file.

Algorithm:
Our audio file looks like this: 

![Audio File](https://github.com/arooshiverma/Audio-Steganography-using-LSB-susbstitution/blob/main/imgs/img1.JPG?raw=true)

Now, we know the number of LSBs to use(nlsb) and the length of our message in binary(mlen).
#### Basic Algorithm
We calculate the value minByte – the smallest value possible in the raw-data of the file which depends on the number of channels in the file. We also input the number of LSBs – nlsb, to be used. Up to 3 LSBs give good results.
We sequentially change n LSB bits of the frames. We skip frames whose value is equal to minByte. We do so because we are changing the value by first taking the absolute of, the frame data. If this data is equal to the minimum possible one (for that length), on taking its absolute, we will encounter overflow.

#### Optimization 1:
I observed that rather than storing all the data sequentially, only in 1 section of the audio file, it is better to uniformly spread the data over the whole file. This way, the person analyzing the audio will not be able to detect the noise that easily. As the noise will be for very less time.

#### Optimization 2:
After optimization 1, it was observed that if the message is too big, the spreading over of data would feel like a constant noise.
A new value called continuous_duration=0.2 secs was created. This means, that the message will be stored for 0.2 secs of data then some of the frames will be skipped, then again, some data would be stored for 0.2 secs of frames and so on. If there is a sound for just 0.2 secs, the human ear would rarely catch it. Thus, slots are created:

![Slotting in audio file](https://github.com/arooshiverma/Audio-Steganography-using-LSB-susbstitution/blob/main/imgs/img2.JPG?raw=true)

The blue areas depict 0.2 secs of data where the message is saved. The white areas depict the unchanged cover data.

After these two optimizations, for a secret message of 619,620 bytes and hiding done using 3 LSBs, no noticeable change was there in the audio.

![Embedding Algorithm](https://github.com/arooshiverma/Audio-Steganography-using-LSB-susbstitution/blob/main/imgs/img3.JPG?raw=true)

#### ALGORITHM FOR EXTRACTING DATA
The extraction of the secret message is done in the same way as above. The combination of values of continuous_duration, nlsb and message length constitute the secret key. Then the appropriate number of slots, length of slots etc are computed and data is extracted.

#### FURTHER OPTIMIZATIONS POSSIBLE
If we need to send multiple files and avoid sending the (continuous_duration, nlsb, message length) triplet, we can fix the value of skip and continuous_duration. Or, we can save the message length in the first 8 frames (changing 2 LSBs each) and calculate the rest accordingly. Also, we can fix nlsb beforehand.
