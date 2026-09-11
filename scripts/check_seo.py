"""Local SEO consistency audit. Run after catalogue and URL generation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import re,json,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
 def __init__(self,p):super().__init__();self.p=p;self.h1=0;self.ids=[];self.anchors=[];self.meta={}
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='html':assert a.get('lang')=='uk',self.p
  if t=='h1':self.h1+=1
  if 'id' in a:self.ids.append(a['id'])
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content','')
  if t=='img':assert all(k in a for k in ('alt','width','height')),(self.p,a)
  for key in ('href','src'):
   if key in a:
    u=urlsplit(a[key])
    if not u.scheme:
     if u.path:assert (self.p.parent/u.path).is_file(),(self.p,a[key])
     elif u.fragment:self.anchors.append(u.fragment)
titles=set();descs=set();urls=set()
for p in list(root.glob('*.html'))+list((root/'articles').rglob('*.html')):
 # Google's ownership files must remain unmodified and outside the sitemap.
 if re.fullmatch(r'google[0-9a-f]+\.html',p.name) and p.read_text().strip()=='google-site-verification: '+p.name:continue
 s=p.read_text();page=Page(p);page.feed(s)
 assert page.h1==1,p
 assert len(page.ids)==len(set(page.ids)),p
 assert all(i in page.ids for i in page.anchors),p
 title=re.search(r'<title>(.*?)</title>',s,re.S).group(1);desc=page.meta['description']
 assert title and title not in titles,p; titles.add(title)
 assert desc and desc not in descs,p;descs.add(desc)
 assert page.meta['og:title']==title and page.meta['og:description']==desc,p
 assert page.meta['twitter:title']==title and page.meta['twitter:description']==desc,p
 assert 'noindex' not in page.meta.get('robots',''),p
 canonicals=re.findall(r'<link rel="canonical" href="([^"]+)"',s)
 assert len(canonicals)==1,p
 canonical=canonicals[0];assert canonical.startswith('https://') and canonical not in urls,p;urls.add(canonical)
 data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S).group(1))
 assert data['url']==canonical==page.meta['og:url'],p
 assert data['inLanguage']=='uk',p
 if data['@type']=='BlogPosting':
  assert data['author']['url'] and data['datePublished'] and data['timeRequired'],p
 if p.name!='index.html':
  breadcrumb=data['mainEntityOfPage']['breadcrumb'] if data['@type']=='BlogPosting' else data['breadcrumb']
  assert breadcrumb['itemListElement'][-1]['item']==canonical,p
 if data['@type']=='CollectionPage':
  assert len(data['mainEntity']['itemListElement'])==s.count('class="article-card"'),p
sitemap={n.text for n in ET.parse(root/'sitemap.xml').findall('.//{*}loc')}
assert urls==sitemap
print(f'PASS: {len(urls)} pages. Metadata, canonical URLs, schemas, sitemap, headings, anchors and assets are consistent.')
