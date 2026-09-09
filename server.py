import html, json, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from .payments import PaymentManager
from .seed import seed_world
from .dashboard import snapshot
from .education import EducationEngine

PAYMENTS = PaymentManager()
WORLD = seed_world()
PAYMENTS.marketplace.sync_world(WORLD)
EDUCATION = EducationEngine()
for _citizen in WORLD.citizens.values():
    EDUCATION.ensure_citizen(_citizen)

PAGE = r'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Earth v1.1</title>
<style>
:root{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#17202a;background:#f4f6f8}
*{box-sizing:border-box}body{margin:0}.top{background:#101828;color:white;padding:22px 28px;position:sticky;top:0;z-index:3}.top h1{margin:0 0 5px;font-size:28px}.top p{margin:0;color:#b8c2d0}.wrap{max-width:1400px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{background:white;border:1px solid #dfe4ea;border-radius:14px;padding:18px;box-shadow:0 2px 8px #00000008}.metric{font-size:25px;font-weight:750;margin-top:6px}.label{font-size:12px;color:#667085;text-transform:uppercase;letter-spacing:.07em}.section{margin-top:22px}.section h2{font-size:19px}.tablewrap{overflow:auto;background:white;border:1px solid #dfe4ea;border-radius:14px}.table{width:100%;border-collapse:collapse;min-width:850px}.table th,.table td{text-align:left;padding:11px 13px;border-bottom:1px solid #edf0f3;font-size:13px}.table th{color:#667085;background:#fafbfc}.pill{display:inline-block;padding:4px 8px;border-radius:999px;background:#eef2f6;font-size:12px}.danger{background:#fff0f0;color:#a11}.ok{background:#edf9f1;color:#17663a}.actions{display:flex;gap:9px;flex-wrap:wrap;margin:14px 0}button,input{font:inherit;padding:10px 12px;border:1px solid #cfd6df;border-radius:9px}button{cursor:pointer;background:#101828;color:white;border-color:#101828}button.secondary{background:white;color:#101828}.notice{padding:12px;border-radius:10px;background:#fff8e7;border:1px solid #f1d38a}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;white-space:pre-wrap}.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:950px){.grid{grid-template-columns:repeat(2,1fr)}.cols{grid-template-columns:1fr}}@media(max-width:600px){.wrap{padding:14px}.grid{grid-template-columns:1fr}.top{padding:18px}}
</style></head><body>
<header class="top"><h1>🌍 AI Earth v1.1</h1><p>AI civilization command center — economy, businesses, marketplace, finance and oversight</p></header>
<main class="wrap">
<div id="notice" class="notice">Loading AI Earth…</div>
<section class="grid section" id="metrics"></section>
<section class="section"><h2>Owner Finance</h2><div class="card"><div id="finance"></div><div class="actions"><form method="post" action="/deposit"><input name="amount" type="number" min="10" step="0.01" placeholder="Deposit ZAR" required><input name="email" type="email" placeholder="Email" required><button>Deposit via PayFast</button></form><form method="post" action="/withdraw-profit"><input id="withdrawAmount" name="amount" type="number" min="1" step="0.01" placeholder="Profit to withdraw" required><button>Request profit withdrawal</button></form></div><p class="label">Deposited principal is never automatically classified as profit.</p></div></section>
<section class="section"><h2>Education, Training & Mastery</h2><div class="grid" id="educationMetrics"></div><div class="tablewrap"><table class="table"><thead><tr><th>Citizen</th><th>Role</th><th>Capability</th><th>Knowledge</th><th>Training</th><th>Qualifications</th><th>Next</th></tr></thead><tbody id="citizens"></tbody></table></div></section>
<section class="section"><h2>Advanced Institutions & Public Systems</h2><div class="cols"><div class="card"><h3>Institutes</h3><div id="institutions"></div><h3>Research Findings</h3><div id="research" class="mono"></div></div><div class="card"><h3>Culinary & Media</h3><div id="restaurants"></div><h3>Games</h3><div id="games"></div><h3>Virtual Sports</h3><div id="sports"></div><h3>Public Safety</h3><div id="forces"></div></div></div></section><section class="section"><h2>Mineral Wealth & Value-Chain Ecosystem</h2><div class="grid" id="mineralMetrics"></div><div class="cols"><div class="card"><b>Mineral portfolio</b><div id="minerals"></div></div><div class="card"><b>Value-chain projects</b><div id="mineralProjects"></div></div></div></section><section class="section"><h2>Industrial Manufacturing</h2><div class="grid" id="industryMetrics"></div><div class="cols"><div class="card"><b>Plants</b><div id="plants"></div></div><div class="card"><b>Manufactured Products</b><div id="manufactured"></div></div></div></section><section class="section"><h2>Businesses</h2><div class="tablewrap"><table class="table"><thead><tr><th>Business</th><th>Sector</th><th>Cash</th><th>Revenue</th><th>Expenses</th><th>Profit</th><th>Staff</th><th>Quality</th><th>Safety</th><th>Security</th><th>Status</th></tr></thead><tbody id="businesses"></tbody></table></div></section>
<section class="section"><h2>Marketplace</h2><div class="tablewrap"><table class="table"><thead><tr><th>Product</th><th>Kind</th><th>Price</th><th>Business</th><th>Active</th></tr></thead><tbody id="listings"></tbody></table></div></section>
<section class="section cols"><div><h2>Recent AI Earth Events</h2><div class="card mono" id="events"></div></div><div><h2>Finance Ledger</h2><div class="card mono" id="ledger"></div></div></section>
<section class="section"><div class="card"><b>Operations</b><div class="actions"><form method="post" action="/advance"><input name="days" type="number" min="1" max="30" value="1"><button>Advance simulation</button></form><button class="secondary" onclick="refresh()">Refresh dashboard</button></div><p class="label">Payment mode: <span id="mode"></span> · API: <span>/api/dashboard</span> · Health: <span>/health</span></p></div></section>
</main>
<script>
const money=n=>'R'+Number(n||0).toLocaleString('en-ZA',{minimumFractionDigits:2,maximumFractionDigits:2});
async function refresh(){const r=await fetch('/api/dashboard');const d=await r.json();
 document.getElementById('notice').textContent=d.flags.length?('Oversight flags: '+d.flags.join(' · ')):'All oversight systems clear.'; document.getElementById('notice').className=d.flags.length?'notice':'notice ok';
 document.getElementById('metrics').innerHTML=[['World Day',d.day],['Economy Value',money(d.economy_value)],['Treasury',money(d.treasury)],['External Revenue',money(d.external_revenue)],['Citizens',d.citizens],['Businesses',d.business_count],['Realized Profit',money(d.finance.realized_profit)],['Available Profit',money(d.finance.available_profit)]].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="metric">${x[1]}</div></div>`).join('');
 document.getElementById('finance').innerHTML=`<div class="grid"><div><div class="label">Deposited Principal</div><div class="metric">${money(d.finance.deposited_principal)}</div></div><div><div class="label">Realized Profit</div><div class="metric">${money(d.finance.realized_profit)}</div></div><div><div class="label">Withdrawn Profit</div><div class="metric">${money(d.finance.withdrawn_profit)}</div></div><div><div class="label">Available Profit</div><div class="metric">${money(d.finance.available_profit)}</div></div></div>`;
 document.getElementById('withdrawAmount').max=d.finance.available_profit;
 document.getElementById('educationMetrics').innerHTML=[['Average Knowledge',d.education.average_knowledge],['Qualified Citizens',d.education.citizens_with_qualifications+'/'+d.citizens],['Competencies',d.education.competencies.length],['Qualification Paths',d.education.qualifications.length]].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="metric">${x[1]}</div></div>`).join('');
 document.getElementById('citizens').innerHTML=d.citizen_profiles.map(c=>`<tr><td><b>${c.name}</b></td><td>${c.role}</td><td>${c.intelligence_capability}</td><td>${c.knowledge}</td><td>${c.training_level}</td><td>${c.qualifications.length}</td><td>${c.next_recommendation}</td></tr>`).join('');
const m=d.minerals||{}; const ind=d.industry||{}; document.getElementById('industryMetrics').innerHTML=[['Industrial Revenue',money(ind.industrial_revenue)],['Industrial Jobs',ind.industrial_jobs||0],['Domestic Sales',money(ind.domestic_sales)],['Industrial Exports',money(ind.exports)]].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="metric">${x[1]}</div></div>`).join(''); document.getElementById('plants').innerHTML=(ind.plants||[]).map(x=>`<p><b>${x.name}</b> · utilization ${Number(x.utilization||0).toFixed(1)}% · output ${Number(x.output||0).toFixed(2)}</p>`).join(''); document.getElementById('manufactured').innerHTML=(ind.products||[]).map(x=>`<p><b>${x.name}</b> · ${x.category} · produced ${Number(x.units_produced||0).toFixed(2)} · sold ${Number(x.units_sold||0).toFixed(2)}</p>`).join(''); document.getElementById('mineralMetrics').innerHTML=[['Portfolio Value',money(m.portfolio_value)],['Local Value Added',money(m.local_value_added)],['Exports Value',money(m.exports_value)],['Environmental Fund',money(m.environmental_fund)],['Beneficiation Index',Number(m.beneficiation_index||0).toFixed(1)],['Recycling Index',Number(m.recycling_index||0).toFixed(1)]].map(x=>`<div class="card"><div class="label">${x[0]}</div><div class="metric">${x[1]}</div></div>`).join(''); document.getElementById('minerals').innerHTML=(m.resources||[]).map(x=>`<p><b>${x.name}</b> · remaining ${Number(x.remaining||0).toLocaleString()} ${x.unit} · refined ${Number(x.refined||0).toLocaleString()} · recycled ${Number(x.recycled||0).toLocaleString()}</p>`).join(''); document.getElementById('mineralProjects').innerHTML=(m.projects||[]).map(x=>`<p><b>${x.name}</b> · ${x.stage} · jobs ${x.jobs} · value added ${money(x.value_added)}</p>`).join('');
 const a=d.institutions||{};
 document.getElementById('institutions').innerHTML=(a.institutions||[]).map(x=>`<p><b>${x.name}</b> — ${x.kind}<br><span class="label">${x.mission}</span></p>`).join('');
 document.getElementById('research').textContent=(a.research_projects||[]).map(x=>`${x.title}: ${x.findings} [${x.status}]`).join('\n\n')||'No findings yet.';
 document.getElementById('restaurants').innerHTML=(a.restaurants||[]).map(x=>`<p><b>${x.name}</b> · recipes ${x.recipes_shared} · content ${x.content_published} · ${money(x.revenue)}</p>`).join('');
 document.getElementById('games').innerHTML=(a.game_studios||[]).map(x=>`<p><b>${x.name}</b> · ${x.games.join(', ')} · ${x.platforms.join(', ')}</p>`).join('');
 const sp=a.virtual_sports||{}; document.getElementById('sports').innerHTML=`${sp.name||'Virtual Sports'} · ${sp.events||0} events · ${sp.teams||0} teams · ${money(sp.revenue)}`;
 document.getElementById('forces').innerHTML=(a.forces||[]).map(x=>`<p><b>${x.name}</b> · readiness ${Number(x.readiness).toFixed(1)}% · training ${x.training_hours}h · ${x.defensive_only?'defensive only':''}</p>`).join('');
 document.getElementById('businesses').innerHTML=d.businesses.map(b=>`<tr><td><b>${b.name}</b></td><td>${b.sector}</td><td>${money(b.cash)}</td><td>${money(b.revenue)}</td><td>${money(b.expenses)}</td><td><b>${money(b.profit)}</b></td><td>${b.employees}</td><td>${b.quality}</td><td>${b.safety}</td><td>${b.security}</td><td><span class="pill ${b.status==='active'?'ok':'danger'}">${b.status}</span></td></tr>`).join('');
 document.getElementById('listings').innerHTML=d.listings.map(l=>`<tr><td>${l.name}</td><td>${l.kind}</td><td>${money(l.price)}</td><td>${l.business_id}</td><td>${l.active?'Yes':'No'}</td></tr>`).join('');
 document.getElementById('events').textContent=d.events.slice(-15).map(e=>`Day ${e.day} · ${e.kind}\n${e.message}${e.amount?' · '+money(e.amount):''}`).join('\n\n')||'No events yet.';
 document.getElementById('ledger').textContent=d.finance.entries.slice(-15).map(e=>`${e.kind} · ${money(e.amount)} · ${e.status}\n${e.note}`).join('\n\n')||'No finance entries yet.';
 document.getElementById('mode').textContent='Payment provider configured';
}
refresh();setInterval(refresh,5000);
</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def _send(self, body, status=200, content_type='text/html; charset=utf-8'):
        raw=body.encode(); self.send_response(status); self.send_header('Content-Type',content_type); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def _form(self):
        length=int(self.headers.get('Content-Length','0')); return parse_qs(self.rfile.read(length).decode())
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ('/','/dashboard','/marketplace'):
            self._send(PAGE); return
        if path=='/api/dashboard': self._send(json.dumps(snapshot(WORLD,PAYMENTS.owner_finance,PAYMENTS.marketplace,EDUCATION)),content_type='application/json'); return
        if path=='/health': self._send('{"ok":true}',content_type='application/json'); return
        self._send('Not found',404)
    def do_POST(self):
        path=urlparse(self.path).path; q=self._form()
        if path=='/advance':
            try:
                from .engine import EconomyEngine
                n=max(1,min(30,int(q.get('days',['1'])[0])))
                EconomyEngine(WORLD).run(n)
                PAYMENTS.marketplace.sync_world(WORLD)
                self.send_response(303); self.send_header('Location','/dashboard'); self.end_headers()
            except Exception as e: self._send(f'<h2>Advance error</h2><pre>{html.escape(str(e))}</pre>',500)
            return
        if path=='/deposit':
            try:
                d,form=PAYMENTS.create_checkout(float(q.get('amount',['0'])[0]),q.get('email',[''])[0],'/dashboard?deposit=success','/dashboard?deposit=cancel','/itn')
                self._send(f'<html><body><h2>Deposit {html.escape(d.id)}</h2>{form}<p><a href="/dashboard">Back to dashboard</a></p></body></html>')
            except Exception as e:self._send(f'<h2>Deposit setup error</h2><pre>{html.escape(str(e))}</pre>',500)
            return
        if path=='/withdraw-profit':
            try:
                req=PAYMENTS.owner_finance.request_profit_withdrawal(float(q.get('amount',['0'])[0]),'Owner requested realized-profit payout')
                self._send(json.dumps({'ok':True,'request_id':req.id,'status':req.status}),content_type='application/json')
            except Exception as e:self._send(json.dumps({'ok':False,'error':str(e)}),400,'application/json')
            return
        if path=='/buy':
            try:
                sale,form=PAYMENTS.create_product_checkout(q.get('listing_id',[''])[0],q.get('email',[''])[0],'/dashboard?purchase=success','/dashboard?purchase=cancel','/itn')
                self._send(f'<html><body><h2>Order {html.escape(sale.id)}</h2>{form}</body></html>')
            except Exception as e:self._send(f'<h2>Checkout error</h2><pre>{html.escape(str(e))}</pre>',400)
            return
        if path=='/itn':
            payload={k:v[0] for k,v in q.items()}
            try:
                result=PAYMENTS.verify_and_apply_itn(payload); self._send('{"received":true}' if result else '{"received":false}',200 if result else 404,'application/json')
            except Exception as e:self._send(json.dumps({'received':False,'error':str(e)}),400,'application/json')
            return
        self._send('Not found',404)

def main():
    port=int(os.getenv('AI_EARTH_PORT','8787')); print(f'AI Earth v1.1 dashboard: http://localhost:{port}/'); HTTPServer(('0.0.0.0',port),Handler).serve_forever()
if __name__=='__main__': main()
