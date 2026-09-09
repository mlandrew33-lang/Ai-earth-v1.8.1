import json
from .llm import LLMClient
from .agents import Decision

class AgentBrain:
    """LLM reasoning layer. The economy remains deterministic and validates every proposed action."""
    def __init__(self, client=None):
        self.llm = client or LLMClient()

    def citizen_decision(self, citizen, world):
        system = ('You are an AI citizen in a simulated civilization. Make one bounded economic proposal. '
                  'You may propose save, invest, train, research, improve_product, or found_business. '
                  'Do not move money yourself. Return JSON with action,target,reason,confidence.')
        prompt = json.dumps({'citizen': citizen.__dict__, 'day': world.day, 'treasury': world.treasury,
                             'businesses': [{k:getattr(b,k) for k in ['id','name','sector','cash','profit','reputation','quality_score']} for b in world.businesses.values()]})
        r = self.llm.generate(system, prompt, True)
        data = self.llm.parse_json(r.text)
        if isinstance(data, dict) and data.get('action'):
            return Decision(citizen.name, data['action'], str(data.get('target', citizen.id)), str(data.get('reason','LLM proposal')), True)
        return None

    def controller_plan(self, world, specialist_summary):
        system = ('You are the World Controller of AI Earth. Coordinate, but never bypass Finance, Quality, Safety, Security, '
                  'or the Constitution. Return JSON array of proposals. Allowed actions: expand, train, experiment, freeze_spending, review_debt.')
        prompt = json.dumps({'day':world.day,'treasury':world.treasury,'specialists':specialist_summary,
                             'businesses':[{'id':b.id,'name':b.name,'profit':b.profit,'cash':b.cash,'quality':b.quality_score,'safety':b.safety_score,'security':b.security_score} for b in world.businesses.values()]})
        r = self.llm.generate(system, prompt, True)
        data = self.llm.parse_json(r.text)
        out=[]
        if isinstance(data,list):
            for x in data[:5]:
                if isinstance(x,dict) and x.get('action'):
                    out.append(Decision('WORLD_CONTROLLER',x['action'],str(x.get('target','')),str(x.get('reason','LLM plan')),True))
        return out
