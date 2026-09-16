from pathlib import Path
import json
from playwright.sync_api import sync_playwright
P=Path.cwd();out=P/'output/nobogh-v2/references'
files={'landing':'صفحة-الهبوط.html','auth':'نبوغ-تسجيل-انشاء-حساب-.html','parent':'ولي الامر.html','admin':'مدير النظام.html'}
results={}
with sync_playwright() as p:
 b=p.chromium.launch(channel='msedge',headless=True)
 for key,name in files.items():
  page=b.new_page(viewport={'width':1440,'height':1000},color_scheme='light')
  page.goto((P/name).as_uri(),wait_until='load');page.evaluate('document.fonts.ready');page.wait_for_timeout(400)
  page.screenshot(path=str(out/f'before-{key}.png'))
  results[key]={'body_class':page.locator('body').get_attribute('class'),'text':page.locator('body').inner_text()[:5500],'layout':page.evaluate('''()=>[...document.querySelectorAll('h1,h2,.welcome-hero,.visual-panel,.video-card,.hero')].map(e=>({tag:e.tagName,cls:e.className,text:e.innerText?.slice(0,150),box:[e.offsetWidth,e.offsetHeight],children:[...e.children].map(x=>({tag:x.tagName,cls:x.className})).slice(0,12)}))''')}
  page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/f'before-{key}-mobile.png'))
  results[key]['mobile']=page.evaluate('({scroll:document.documentElement.scrollWidth,width:innerWidth})')
  page.close()
 for name,url in [('khan','https://www.khanacademy.org/kids'),('lingokids','https://lingokids.com/'),('classdojo','https://www.classdojo.com/')]:
  page=b.new_page(viewport={'width':1440,'height':1000},color_scheme='light')
  try:
   page.goto(url,wait_until='domcontentloaded',timeout=40000);page.wait_for_timeout(1800);page.screenshot(path=str(out/f'{name}.png'));results[name]={'url':page.url,'text':page.locator('body').inner_text()[:900]}
  except Exception as e:results[name]={'error':str(e)[:300]}
  page.close()
 b.close()
(P/'tmp/source-inspection.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
