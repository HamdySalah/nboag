from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib
P=Path.cwd();O=P/'output/nobogh-v2';S=O/'screens';S.mkdir(exist_ok=True)
files={'landing':'صفحة-الهبوط.html','auth':'نبوغ-تسجيل-انشاء-حساب-.html','parent':'ولي الامر.html','admin':'مدير النظام.html'}
res={}
with sync_playwright() as p:
 b=p.chromium.launch(channel='msedge',headless=True)
 for key,name in files.items():
  page=b.new_page(viewport={'width':1440,'height':1000},color_scheme='light')
  errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
  page.goto((P/name).as_uri(),wait_until='load');page.evaluate('document.fonts.ready');page.wait_for_timeout(200)
  page.screenshot(path=str(S/f'{key}-desktop.png'))
  res[key]={'errors':errs,'sha256_equal':hashlib.sha256((P/name).read_bytes()).hexdigest()==hashlib.sha256((O/'source-backup'/name).read_bytes()).hexdigest(),'sizes':{}}
  for w,h in [(1440,1000),(768,1024),(390,844),(320,740)]:
   page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(100)
   res[key]['sizes'][str(w)]=page.evaluate('''()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,body:document.body.scrollWidth,overflows:[...document.querySelectorAll('h1,h2,h3,button,a,input,select')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.left < -2 || r.right > innerWidth+2)&&getComputedStyle(e).position!=='fixed'&&!(e.closest('aside')||e.closest('#sidebar')||e.closest('.testi-track')||e.closest('#preview-stage'))}).slice(0,8).map(e=>({tag:e.tagName,cls:e.className,text:e.innerText?.slice(0,50)}))})''')
   if w==390:page.screenshot(path=str(S/f'{key}-mobile.png'));page.screenshot(path=str(S/f'{key}-mobile-full.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1000})
  if key=='parent':
   page.evaluate("go('activities')");page.screenshot(path=str(S/'parent-activities.png'));res[key]['activities']=page.locator('#page-activities').is_visible()
   page.evaluate("go('dashboard')")
  if key=='auth':
   page.evaluate("switchView('signup')");page.screenshot(path=str(S/'auth-signup.png'));res[key]['signup']=page.locator('#signupView').is_visible()
   page.evaluate("switchView('login'); showChildCode()");page.screenshot(path=str(S/'auth-child-code.png'));res[key]['child_code']=True
  if key=='landing':
   page.locator('#sec-trial').scroll_into_view_if_needed();page.screenshot(path=str(S/'landing-activities.png'))
  page.close()
 b.close()
(O/'qa-results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False,indent=2))
