"""External observational harness; never replaces graph nodes or model responses."""
import os, sys, json, uuid, time, subprocess
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path('/workspace/llm-run/wt-c63c26f')
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'services/api')]
os.chdir(ROOT)
from app.agent.graph import compile_agent
from langgraph.checkpoint.memory import InMemorySaver
from data.rag_settings import load_settings
from openai.resources.chat.completions import Completions
settings=load_settings()
secrets=[v for k,v in os.environ.items() if any(t in k.upper() for t in ('KEY','TOKEN','PASSWORD','SECRET')) and len(v)>5]
def clean(x):
    s=json.dumps(x,ensure_ascii=False,default=str)
    for v in secrets: s=s.replace(v,'***')
    return json.loads(s)
def write(name,x): (OUT/name).write_text(json.dumps(clean(x),ensure_ascii=False,indent=2)+'\n')
def now(): return datetime.now(ZoneInfo('America/Mexico_City')).isoformat()
metadata=[]
original=Completions.create
def observe(self,*args,**kwargs):
    response=original(self,*args,**kwargs)
    usage=getattr(response,'usage',None)
    metadata.append({'model':getattr(response,'model',None),'usage':usage.model_dump() if usage else None})
    return response
Completions.create=observe
questions=json.loads((ROOT/'docs/langgraph/evidence/llm-live/02-run-agent-live.json').read_text())['resultados']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
runs=[]
for index,item in enumerate(questions):
    run_id=str(uuid.uuid4()); thread_id=str(uuid.uuid4())
    config={'run_id':uuid.UUID(run_id),'configurable':{'thread_id':thread_id}}
    graph=compile_agent(checkpointer=InMemorySaver())
    run={'run_id':run_id,'thread_id':thread_id,'question':item['pregunta'],'started_at':now(),'nodes':[],'debug_events':[],'updates':[]}
    started=time.perf_counter(); tasks={}; state={'question':item['pregunta']}; metadata.clear()
    try:
        for mode,event in graph.stream(state,config,stream_mode=['updates','debug']):
            received=time.perf_counter()
            if mode=='debug':
                run['debug_events'].append(event)
                p=event.get('payload',{}); typ=event.get('type')
                if typ=='task':
                    tasks[p['id']]={'node':p['name'],'start_timestamp':event['timestamp'],'clock':received}
                elif typ=='task_result':
                    task=tasks.get(p['id'],{})
                    run['nodes'].append({'order':len(run['nodes'])+1,'node':p.get('name'), 'start_timestamp':task.get('start_timestamp'),'end_timestamp':event['timestamp'], 'latency_s':received-task['clock'] if 'clock' in task else None,'latency_basis':'debug event observation monotonic clock','error':p.get('error')})
            else:
                run['updates'].append(event)
                for name,update in event.items():
                    if name.startswith('__'): continue
                    matching=next((n for n in reversed(run['nodes']) if n['node']==name),None)
                    # Updates can precede the task_result debug event; attach after streaming.
                    changed=[k for k,v in update.items() if k not in state or state[k]!=v]
                    run.setdefault('node_outputs',[]).append({'node':name,'output':update,'state_keys_written':list(update),'state_keys_changed':changed,'sources_retrieved':update.get('context',[])})
                    state.update(update)
        run['error']=''
    except Exception as exc:
        run['error']=f'{type(exc).__name__}: {exc}'
    run['latencia_s']=time.perf_counter()-started;run['ended_at']=now()
    for n in run['nodes']:
        out=next((x for x in run.get('node_outputs',[]) if x['node']==n['node']),{})
        n.update({k:v for k,v in out.items() if k!='node'})
    final=graph.get_state(config).values
    run.update(status=final.get('status'),answer=final.get('answer'),sources=final.get('context',[]))
    run['checkpoints']=[{'checkpoint_id':s.config['configurable'].get('checkpoint_id'),'created_at':s.created_at,'step':s.metadata.get('step'),'source':s.metadata.get('source'),'next':list(s.next),'status':s.values.get('status')} for s in reversed(list(graph.get_state_history(config)))]
    run['checkpoint_count']=len(run['checkpoints']);run['response_metadata']=list(metadata)
    run['tokens']=metadata[0]['usage'] if metadata else None
    run['tokens_reason']=None if run['tokens'] else ('No generation call on insufficient_context route.' if not metadata else 'Provider response omitted usage.')
    run['model']=metadata[0]['model'] if metadata else None
    run['configured_generation_model']=settings.generation_model_id
    run['embedding_model']=settings.embedding_model_id
    run['generation_base_url']=settings.generation_base_url
    run['generation_mode']='live' if metadata else 'not_called'
    run['label']=['live_fee_grounding','live_outside_corpus'][index]
    run['correctness']={'fee_22_percent':'22%' in (run['answer'] or ''),'discount_escalates_to_Marcos_Ibanez':'Marcos Ibáñez' in (run['answer'] or '')} if index==0 else {'honest_refusal':run['status']=='insufficient_context'}
    runs.append(run)
    write('trace-instrumented.json',{'head':head,'date_CST':now(),'runs':runs})
export=json.loads((ROOT/'docs/langgraph/trace-full-run.json').read_text())
export.update(note='Real instrumented live stream; debug task/task_result timing, update payloads and MemorySaver history. No status-inferred nodes.',evidence=str(OUT/'trace-instrumented.json'),hora=now(),tokens=[r['tokens'] for r in runs],tokens_reason=None)
for dest,src in zip(export['runs'],runs):
    dest.update({k:v for k,v in src.items() if k not in ('debug_events','updates','node_outputs')})
    dest.update(nodes_basis='Observed LangGraph debug task/task_result and updates events',run_id_reason=None,checkpoints_reason=None,model_reason=None if src['model'] else 'Generation not called.')
write('trace-full-run.instrumented.json',export)
log={'date_CST':now(),'head':head,'runs':[{k:r[k] for k in ('run_id','status','error','latencia_s','checkpoint_count','tokens','correctness')} for r in runs]}
write('run.log',log)
print(json.dumps(clean(log),ensure_ascii=False,indent=2))
