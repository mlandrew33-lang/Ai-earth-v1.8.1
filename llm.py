import json, os, urllib.request, urllib.error
from dataclasses import dataclass
from typing import Any

@dataclass
class LLMResponse:
    text: str
    provider: str

class LLMClient:
    """Provider-neutral text generation. No API key is required for the deterministic fallback."""
    def __init__(self):
        self.provider = os.getenv('AI_EARTH_LLM_PROVIDER', 'fallback').lower()
        self.model = os.getenv('AI_EARTH_LLM_MODEL', '')

    def enabled(self):
        return self.provider in {'gemini', 'openai', 'ollama'}

    def generate(self, system: str, prompt: str, json_mode: bool = False) -> LLMResponse:
        if self.provider == 'gemini':
            return self._gemini(system, prompt, json_mode)
        if self.provider == 'openai':
            return self._openai_compatible(system, prompt, json_mode)
        if self.provider == 'ollama':
            return self._ollama(system, prompt, json_mode)
        return LLMResponse('', 'fallback')

    def _post(self, url, payload, headers=None, timeout=60):
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json', **(headers or {})}, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))

    def _gemini(self, system, prompt, json_mode):
        key = os.getenv('GEMINI_API_KEY')
        if not key:
            return LLMResponse('', 'gemini-not-configured')
        model = self.model or 'gemini-2.5-flash'
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}'
        cfg = {'temperature': 0.4}
        if json_mode:
            cfg['responseMimeType'] = 'application/json'
        payload = {'systemInstruction': {'parts':[{'text':system}]}, 'contents':[{'role':'user','parts':[{'text':prompt}]}], 'generationConfig':cfg}
        try:
            data = self._post(url, payload)
            text = data['candidates'][0]['content']['parts'][0]['text']
            return LLMResponse(text, 'gemini')
        except Exception as e:
            return LLMResponse('', f'gemini-error:{e}')

    def _openai_compatible(self, system, prompt, json_mode):
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            return LLMResponse('', 'openai-not-configured')
        model = self.model or 'gpt-5-mini'
        base = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
        payload = {'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}], 'temperature':0.4}
        if json_mode:
            payload['response_format'] = {'type':'json_object'}
        try:
            data = self._post(base + '/chat/completions', payload, {'Authorization':f'Bearer {key}'})
            return LLMResponse(data['choices'][0]['message']['content'], 'openai')
        except Exception as e:
            return LLMResponse('', f'openai-error:{e}')

    def _ollama(self, system, prompt, json_mode):
        model = self.model or 'llama3.2'
        url = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/chat')
        payload = {'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}], 'stream':False, 'options':{'temperature':0.4}}
        if json_mode:
            payload['format'] = 'json'
        try:
            data = self._post(url, payload)
            return LLMResponse(data['message']['content'], 'ollama')
        except Exception as e:
            return LLMResponse('', f'ollama-error:{e}')

    @staticmethod
    def parse_json(text: str) -> Any:
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find('{'), text.rfind('}')
            if start >= 0 and end > start:
                try: return json.loads(text[start:end+1])
                except json.JSONDecodeError: pass
            start, end = text.find('['), text.rfind(']')
            if start >= 0 and end > start:
                try: return json.loads(text[start:end+1])
                except json.JSONDecodeError: pass
        return None
