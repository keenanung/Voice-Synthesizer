import scipy as sp
import wave
import scipy.io.wavfile as wav
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# ------------------------------------------ PART B.2 ------------------------------------------

# load the recording data
sampling_rate, audio_data = wav.read('brbaline.wav')
newAudioData = []

# Make the file proper format from incorrectly formatted mono file (stereo with both indices same)
for indice in audio_data:
    newIndice = indice[0]
    newAudioData.append(newIndice)

audio_data = newAudioData

# down-sample to a 16 KHz file
new_length = int(len(audio_data) * 16000 / sampling_rate)
downsampled_audio_data = sp.signal.resample(audio_data, new_length)
output_recording = 'down-sampled.wav'
wav.write(output_recording, 16000, downsampled_audio_data.astype(np.int16))

# re-load the new down-sampled file into the audio_data
sampling_rate, audio_data = wav.read(output_recording)
print("sampling_rate", sampling_rate)

# Calculate the duration of the audio
duration = (len(audio_data)-1) / sampling_rate
print("duration", duration)

time_axis = (1 / sampling_rate) * np.arange(0, len(audio_data))

# Plot the audio recording data
plt.figure(figsize=(10, 4))
plt.plot(time_axis, audio_data)
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.title('Audio Waveform')
plt.grid()
plt.show()

# Set the sampling rate
sampleRate = 16000

# ------------------------------------------ PART B.3 ------------------------------------------
def generateChunkedData (size, gap):
    # Resolve desired chunk size and gap size as a number of values rather than their inputs which are in (s)
    elementsPerchunk = int(sampleRate * size)
    elementGap = int(sampleRate * gap)
    chunkArray = []

    # Start at 0, iterate to the start of the next chunk each time. Ensure there is room to iterate before doing so
    for i in range(0,len(audio_data) - elementsPerchunk - elementGap,elementsPerchunk + elementGap):
        # generate the individual chunk
        chunk = []

        # i will be the start point of the chunk. Iterate by 1 until you have collected the correct # of elements
        for j in range(i, elementsPerchunk + i, 1):
            chunk = chunk + [audio_data[j]]
        
        # Add the chunk of data to the chunk array
        chunkArray = chunkArray + [chunk]
    
    return chunkArray

def computeRMS(arrayOfValues):
    a = 0
    for value in arrayOfValues:
        a = a + (value**2)
    RMS = 1/(len(arrayOfValues)-1) * np.sqrt(a)
    return RMS

def filterChunks(chunkArray, minimumFrequency, maximumFrequency, bandwidth):
    # Keep track of the chunk number
    n = 0

    # Initialize the output array
    outputData = []

    # Go through all chunks, apply the series of bandpass filters, and synthesize the sine waves
    for chunk in chunkArray:
        length = len(chunk)

        #initialize the array of synthesized sinusoids
        synthesizedSinusoids = []

        # Create the bands. Fourth order filters will be used
        for i in range(minimumFrequency, maximumFrequency - bandwidth, bandwidth):
            lowFrequency = i - (bandwidth / 2)
            highFrequency = i + (bandwidth / 2)

            # Construct the bandpass filter. Note that 'i' is the center frequency
            sos = signal.butter(2, [lowFrequency,highFrequency], 'bandpass', output='sos', fs=sampleRate)

            # Filter the chunk
            filteredChunk =  sp.signal.sosfilt(sos, chunk)

            # Take the RMS and store it
            A = computeRMS(filteredChunk)

            # SYNTHESIZE THE SINUSOID
                # Note the start and  end sample of the chunk      
            start = n + length
            end = start + (length - 1)

                # Create an array with all sample indices of the chunk
            arrayOfSamples = np.linspace(start, end, length)

                # Create an array of all the time indices
            arrayOfTime = arrayOfSamples/sampleRate

                # Scale the times by 2pi * center frequency as instructed
            timeInput = arrayOfTime * 2 * np.pi * i      
            
                # Synthesize the sinusoid and add it to the array. Experimentally determined we need to scale
                # the amplitude so it isnt so quiet. This is likely due to the higher order filters
            sinusoid = 8 * A * np.sin(timeInput)
            synthesizedSinusoids.append(sinusoid)
        
        # Combine all the sinusoids (sum up the amplitude at each point)
        combinedWaveform = np.sum(synthesizedSinusoids, axis=0)

        # Add the sin equivalent of the chunk to the output data array
        outputData.append(combinedWaveform)
        n = n + 1

    # Concatenate list of lists of amplitudes into one list of amplitude at time
    return np.concatenate(outputData, axis = 0)

# ------------------------------------------ PART B.4 ------------------------------------------

# It was deemed that 10ms chunk with no gaps was ideal
chunkArray = generateChunkedData(0.01,0)

# NOTE: Due to nyquist limitations, the maximum frequency we can take care of is 8kHz
outputData = filterChunks(chunkArray, 150, 8000, 100)
finalOutput = 'robot.wav'
wav.write(finalOutput, 16000, outputData.astype(np.int16))
