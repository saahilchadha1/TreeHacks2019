#!/usr/bin/env python3
import houndify
import sys
import time
import wave
import recorder
import csv


recorder.RecordingFile.record_process()

CLIENT_ID = "G-0XtruAEyMbzqN5FTfH0Q=="
CLIENT_KEY = "YYIyq4j1BUgoNQ0Ped9TK4hWsuoxfPdKfLbsjGVmUdFvoDVA3IH3761OZ5dIik1tpOeReMNIVXWtqsVRPIbDiA=="
AUDIO_FILE = "nonblocking.wav"

BUFFER_SIZE = 256


audio = wave.open(AUDIO_FILE)
if audio.getsampwidth() != 2:
  print("%s: wrong sample width (must be 16-bit)" % fname)
  sys.exit()
# if audio.getframerate() != 8000 and audio.getframerate() != 16000:
#   print("%s: unsupported sampling frequency (must be either 8 or 16 khz)" % fname)
#   sys.exit()
if audio.getnchannels() != 1:
  print("%s: must be single channel (mono)" % fname)
  sys.exit()


audio_size = audio.getnframes() * audio.getsampwidth()
audio_duration = audio.getnframes() / audio.getframerate()
chunk_duration = BUFFER_SIZE * audio_duration / audio_size
# checkups =	{"pulse": -1,
#             "heart_rate" : -1,
#             "blood_pressure" : -1,
#             "blood_pressure_2" : -1,
#             "hands" : -1,
#             "headneck" : -1,
#             "glands" : -1
#             }
with open('data.csv', mode = 'r') as infile:
    reader = csv.reader(infile)
    checkups = {rows[0]:rows[1] for rows in reader}
# write a function printing out what you have left.

#
# Simplest HoundListener; just print out what we receive.
# You can use these callbacks to interact with your UI.
#
class MyListener(houndify.HoundListener):
  #def onPartialTranscript(self, transcript):
    #print("Partial transcript: " + transcript)
  def onFinalResponse(self, response):
    #print("Final response: " + str(response))
    #takes in a dictionary
    holder = response["AllResults"][0]["Result"]
    def word_inside(dictionary):
        for key in dictionary.keys():
            if key in holder.keys():
                if key == 'blood_pressure' or key == 'blood_pressure_2':
                    checkups["blood_pressure"] = holder["blood_pressure"]['value']
                    checkups["blood_pressure_2"] = holder["blood_pressure_2"]["value"]
                    return None
                checkups[key]=holder[key]['value']
                return None
    word_inside(checkups)
    for key in checkups.keys():
        if checkups.get(key) == -1:
            print("You should check "+ key)
    with open('data.csv', 'w') as f:
        for key in checkups.keys():
            f.write("%s, %s\n"%(key, checkups[key]))


  def onError(self, err):
    print("Error: " + str(err))



client = houndify.StreamingHoundClient(CLIENT_ID, CLIENT_KEY, "test_user", enableVAD=False)
client.setLocation(37.388309, -121.973968)
client.setSampleRate(audio.getframerate())




# # Uncomment the lines below to see an example of using a custom
# # grammar for matching.  Use the file 'turnthelightson.wav' to try it.
# clientMatches = [ {
#   "Expression" : '([1/100 ("can"|"could"|"will"|"would")."you"].[1/10 "please"].("turn"|"switch"|(1/100 "flip"))."on".["the"].("light"|"lights").[1/20 "for"."me"].[1/20 "please"])|([1/100 ("can"|"could"|"will"|"would")."you"].[1/10 "please"].[100 ("turn"|"switch"|(1/100 "flip"))].["the"].("light"|"lights")."on".[1/20 "for"."me"].[1/20 "please"])|((("i".("want"|"like"))|((("i".["would"])|("i\'d")).("like"|"want"))).["the"].("light"|"lights").["turned"|"switched"|("to"."go")|(1/100"flipped")]."on".[1/20"please"])"',
#   "Result" : { "Intent" : "TURN_LIGHT_ON" },
#   "SpokenResponse" : "Ok, I\'m turning the lights on.",
#   "SpokenResponseLong" : "Ok, I\'m turning the lights on.",
#   "WrittenResponse" : "Ok, I\'m turning the lights on.",
#   "WrittenResponseLong" : "Ok, I\'m turning the lights on."
# } ]
#
# client.setHoundRequestInfo('ClientMatches', clientMatches)


client.start(MyListener())

while True:
  chunk_start = time.time()

  samples = audio.readframes(BUFFER_SIZE)
  if len(samples) == 0: break
  if client.fill(samples): break

  # # Uncomment the line below to simulate real-time request
  # time.sleep(chunk_duration - time.time() + chunk_start)

result = client.finish() # returns either final response or error
