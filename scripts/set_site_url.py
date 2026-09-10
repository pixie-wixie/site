"""One-time deployment setup: python3 scripts/set_site_url.py https://your-domain.ua
No script execution or Python is needed by the deployed static site.
"""
from pathlib import Path
from urllib.parse import urlsplit
import sys,re,json,html
from xml.etree.ElementTree import Element,SubElement,ElementTree,register_namespace
root=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 scripts/set_site_url.py https://your-domain.ua')
base=sys.argv[1].rstrip('/')
url=urlsplit(base)
if url.scheme!='https' or not url.hostname or url.query or url.fragment or url.username or url.password:
 raise SystemExit('Provide the public HTTPS site address, optionally including its subdirectory.')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';register_namespace('',ns)
sitemap=Element('{'+ns+'}urlset')
pages = list(root.glob('*.html')) + list((root/'articles').rglob('*.html'))
for p in sorted(pages):
 relative=p.relative_to(root).as_posix()
 canonical=base+'/' if relative=='index.html' else base+'/'+relative
 s=p.read_text()
 s=re.sub(r'\n?<link rel="canonical"[^>]*>','',s)
 s=re.sub(r'\n?<meta property="og:url"[^>]*>','',s)
 s=s.replace('</head>',f'<link rel="canonical" href="{html.escape(canonical,quote=True)}">\n<meta property="og:url" content="{html.escape(canonical,quote=True)}">\n</head>')
 match=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)
 data=json.loads(match.group(1));data['url']=canonical
 data['publisher'].update(url=base+'/',logo={'@type':'ImageObject','url':base+'/img/logo.png'})
 if data['@type']=='BlogPosting':data['mainEntityOfPage']={'@type':'WebPage','@id':canonical}
 if relative=='index.html':
  data['isPartOf']={'@type':'WebSite','name':'Pixie Wixie','url':base+'/','inLanguage':'uk'}
 replacement='<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
 s=s[:match.start()]+replacement+s[match.end():]
 if data['@type'] != 'BlogPosting':
  s=re.sub(r'\n?<meta (?:property="og:image"|name="twitter:image")[^>]*>', '', s)
  s=s.replace('</head>',f'<meta property="og:image" content="{base}/img/logo.png">\n<meta name="twitter:image" content="{base}/img/logo.png">\n</head>')
 p.write_text(s)
 item=SubElement(sitemap,'{'+ns+'}url');SubElement(item,'{'+ns+'}loc').text=canonical
ElementTree(sitemap).write(root/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(root/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n')
print('Configured canonical URLs, social URLs, structured data and sitemap for',base)
