"""Killable per-utterance local model worker. No implicit model downloads."""
import contextlib,sys
from pathlib import Path
import numpy as np

def main():
    kind,path=sys.argv[1:];path=Path(path);data=sys.stdin.buffer.read()
    with contextlib.redirect_stdout(sys.stderr):
        if kind=='stt':
            from faster_whisper import WhisperModel
            model=WhisperModel(str(path),device='cpu',compute_type='int8',local_files_only=True)
            segments,_=model.transcribe(np.frombuffer(data,dtype='<i2').astype(np.float32)/32768,language='en',vad_filter=False)
            output=' '.join(segment.text for segment in segments).strip().encode()
        elif kind=='tts':
            import torch
            from kokoro import KModel,KPipeline
            from scipy.signal import resample_poly
            model=KModel(config=str(path/'config.json'),model=str(path/'kokoro-v1_0.pth'))
            pipeline=KPipeline(lang_code='a',model=model)
            voice=torch.load(path/'af_heart.pt',map_location='cpu',weights_only=True)
            chunks=[np.asarray(audio) for _,_,audio in pipeline(data.decode(),voice=voice)]
            audio=resample_poly(np.concatenate(chunks),2,3)
            output=(np.clip(audio,-1,1)*32767).astype('<i2').tobytes()
        else:raise ValueError('Unknown worker operation')
    sys.stdout.buffer.write(output)
if __name__=='__main__':main()
