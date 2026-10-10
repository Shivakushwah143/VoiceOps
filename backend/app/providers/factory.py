from .base import ProviderManager,Route,ProviderError
from .cloud import SarvamSTT,SarvamTTS,Groq
from .local import FasterWhisper,Ollama,Kokoro
from ..config import settings as s

def manager(mode,audit):
    providers={'sarvam_stt':SarvamSTT(),'faster_whisper':FasterWhisper(),'groq':Groq(),'ollama':Ollama(),'sarvam_tts':SarvamTTS(),'kokoro':Kokoro()}
    names={'stt':s.stt or ('faster_whisper' if mode=='local' else 'sarvam'),'llm':s.llm or ('ollama' if mode=='local' else 'groq'),'tts':s.tts or ('kokoro' if mode=='local' else 'sarvam')}
    routes={}
    for family,name in names.items():
        if name not in {'stt':{'sarvam','faster_whisper'},'llm':{'groq','ollama'},'tts':{'sarvam','kokoro'}}[family]:raise ProviderError('configuration')
        primary=providers[name+'_'+family if name=='sarvam' else name]
        fallback=providers[{'stt':'faster_whisper','llm':'ollama','tts':'kokoro'}[family]]
        routes[family]=Route(primary,None if primary is fallback else fallback)
    return ProviderManager(routes,audit,hybrid=mode=='hybrid',rate_fallback=s.rate_fallback)
