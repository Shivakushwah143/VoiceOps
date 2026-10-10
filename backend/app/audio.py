import audioop
from collections import deque
import webrtcvad

class Codec:
    def __init__(self):self.in_state=None;self.out_state=None
    def decode(self,data):
        pcm=audioop.ulaw2lin(data,2)
        pcm,self.in_state=audioop.ratecv(pcm,2,1,8000,16000,self.in_state)
        return pcm
    def encode(self,pcm):
        data,self.out_state=audioop.ratecv(pcm,2,1,16000,8000,self.out_state)
        return audioop.lin2ulaw(data,2)

class Endpoint:
    def __init__(self):
        self.vad=webrtcvad.Vad(2);self.buffer=b'';self.pre=deque(maxlen=15)
        self.speaking=False;self.silence=0;self.frames=0;self.voiced=0
    def feed(self,data):
        self.buffer+=data;events=[]
        while len(self.buffer)>=640:
            frame,self.buffer=self.buffer[:640],self.buffer[640:]
            voiced=self.vad.is_speech(frame,16000)
            if not self.speaking:
                self.pre.append(frame)
                self.voiced=self.voiced+1 if voiced else 0
                if self.voiced>=3:
                    self.speaking=True;self.silence=0;self.frames=0
                    events.append(('start',b''.join(self.pre)));self.pre.clear()
            else:
                events.append(('audio',frame));self.frames+=1
                self.silence=0 if voiced else self.silence+1
                if self.silence>=35 or self.frames>=1480:
                    events.append(('end',None));self.speaking=False;self.voiced=0
        return events
