# Voice-Synthesizer
Processes an audio file into a "robo-voice" clip. Essentially, the output is a reconstructed sound wave (resembling a sine wave) built based on the frequency data of chunks of the original audio file. The amplitude at each piece of the sine wave coincides with the root mean square measurements at different frequencies of the particular audio chunk corresponding to that time.

Each of these pieces are then arranged one after another to generate the output audio wave.
