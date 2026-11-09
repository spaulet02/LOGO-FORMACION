import sys, docx
from docx.oxml.ns import qn
d = docx.Document(sys.argv[1]); start=int(sys.argv[2]); end=int(sys.argv[3])
body = d.element.body
def sty(p):
    ps = p.find(qn('w:pPr'))
    s = ps.find(qn('w:pStyle')) if ps is not None else None
    return s.get(qn('w:val')) if s is not None else '-'
def txt(e): return ''.join(t.text or '' for t in e.iter(qn('w:t')))
for i, el in enumerate(body):
    if i < start or i >= end: continue
    tag = el.tag.split('}')[1]
    if tag == 'p':
        img = len(list(el.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')))
        num = el.find('.//'+qn('w:numPr'))
        nid = num.find(qn('w:numId')).get(qn('w:val')) if num is not None and num.find(qn('w:numId')) is not None else ''
        print(f"{i} P[{sty(el)}{' num'+nid if nid else ''}{' IMG' if img else ''}] {txt(el)[:150]}")
    elif tag == 'tbl':
        rows = el.findall(qn('w:tr')); cols = len(rows[0].findall(qn('w:tc'))) if rows else 0
        shd = el.find('.//'+qn('w:shd')); fill = shd.get(qn('w:fill')) if shd is not None else ''
        print(f"{i} TBL {len(rows)}x{cols} fill={fill} :: {txt(el)[:200]}")
    else: print(i, tag)
