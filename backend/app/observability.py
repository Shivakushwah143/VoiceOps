import json,logging
from prometheus_client import Counter,Histogram
EVENTS=Counter('voiceops_events','Observed runtime events',['kind'])
LATENCY=Histogram('voiceops_latency_seconds','Measured stage durations',['stage'],buckets=(.05,.1,.25,.5,1,2,5,10,30,60))
def observe(kind,data,call_id=None,turn_id=None):
    EVENTS.labels(kind).inc()
    if kind.startswith('latency.') and isinstance(data.get('ms'),(int,float)):
        LATENCY.labels(kind[8:]).observe(data['ms']/1000)
    if kind=='llm.usage' and data.get('ttft_ms') is not None:LATENCY.labels('llm_ttft').observe(data['ttft_ms']/1000)
    logging.info(json.dumps({'event':kind,'call_id':call_id,'turn_id':turn_id}))
