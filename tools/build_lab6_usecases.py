from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from html import escape
import json

root=Path(__file__).resolve().parents[1]
paths=[root/'docs/costs_database.mdj',root/'frontend/docs/costs_database.mdj']
projects=[json.loads(p.read_text(encoding='utf-8-sig')) for p in paths]
model_name='ЛР6 Прецеденты интерфейса издержек'
old=next(m for m in projects[0]['ownedElements'] if m.get('name')==model_name)
uid=lambda key:sha256(('costs-lab6-usecases-v2:'+key).encode()).hexdigest()[:24]
ref=lambda o:{'$ref':o['_id']}
model={'_type':'UMLModel','_id':old['_id'],'_parent':ref(projects[0]),'name':model_name,'ownedElements':[]}
diagram={'_type':'UMLUseCaseDiagram','_id':old['ownedElements'][0]['_id'],'_parent':ref(model),'name':'ЛР6 Гость и создатель издержек','showGrid':False,'ownedViews':[]}
model['ownedElements'].append(diagram)
views=diagram['ownedViews']

def classifier(key,kind,name,x,y,w,h):
 obj={'_type':kind,'_id':uid(key),'_parent':ref(model),'name':name.replace('\n',' ')}
 model['ownedElements'].append(obj)
 view={'_type':kind+'View','_id':uid(key+'view'),'_parent':ref(diagram),'model':ref(obj),'left':x,'top':y,'width':w,'height':h,'font':'Arial;20;0','fillColor':'#ffffff','lineColor':'#000000','wordWrap':True,'suppressAttributes':True,'suppressOperations':True,'showShadow':False,'subViews':[]}
 comp={'_type':'UMLNameCompartmentView','_id':uid(key+'comp'),'_parent':ref(view),'model':ref(obj),'left':x,'top':y,'width':int(w*.70),'height':45,'wordWrap':True,'subViews':[]}
 label={'_type':'LabelView','_id':uid(key+'label'),'_parent':ref(comp),'left':x+5,'top':y+5,'width':int(w*.70)-10,'height':45,'text':name,'wordWrap':True,'font':'Arial;20;1','horizontalAlignment':2}
 comp['subViews'].append(label);comp['nameLabel']=ref(label)
 view['subViews'].append(comp);view['nameCompartment']=ref(comp)
 for prop,cls in [('attributeCompartment','UMLAttributeCompartmentView'),('operationCompartment','UMLOperationCompartmentView')]+([('extensionPointCompartment','UMLExtensionPointCompartmentView')] if kind=='UMLUseCase' else []):
  child={'_type':cls,'_id':uid(key+prop),'_parent':ref(view),'model':ref(obj),'visible':False}
  view['subViews'].append(child);view[prop]=ref(child)
 views.append(view)
 return obj,view

subject=classifier('subject','UMLUseCaseSubject','Масштаб — React-приложение',290,30,710,1400)
subject[1]['subViews'][0]['width']=710
subject[1]['subViews'][0]['subViews'][0]['width']=690
# A native system boundary replaces the unsupported UMLRectView annotation.
guest=classifier('guest','UMLActor','Гость',55,310,150,145)
creator=classifier('creator','UMLActor','Создатель',55,1020,150,145)

cases=[
 ('catalog','Просмотреть каталог\nиздержек',140,guest),
 ('filter','Отфильтровать каталог\nпо коду издержки',250,guest),
 ('feed','Просмотреть ленту,\nописание и параметры',360,guest),
 ('next','Перейти к следующей\nиздержке в ленте',470,guest),
 ('register','Зарегистрироваться',580,guest),
 ('login','Войти в систему',690,guest),
 ('create','Создать черновик:\nназвание, изображение, видео',820,creator),
 ('resume','Открыть собственный\nсохранённый черновик',930,creator),
 ('publish','Заполнить описание, тип, код\nи опубликовать издержку',1040,creator),
 ('delete','Удалить собственную\nиздержку',1150,creator),
 ('like','Поставить или отменить\nлайк издержке',1260,creator),
 ('logout','Выйти из системы',1370,creator),
]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="1470" viewBox="0 0 1040 1470">','<rect width="1040" height="1470" fill="white"/>','<g font-family="Arial" font-size="21" fill="white" stroke="black" stroke-width="1.5">','<rect x="290" y="30" width="710" height="1400"/>','<text x="645" y="68" fill="black" stroke="none" text-anchor="middle" font-weight="bold">Масштаб — React-приложение</text>']
for label,y in [('Гость',330),('Создатель',1040)]:
 svg += [f'<circle cx="130" cy="{y}" r="17"/>',f'<path d="M130 {y+17} v43 m-35 -25 h70 m-35 25 l-28 34 m28 -34 l28 34" fill="none"/>',f'<text x="130" y="{y+127}" fill="black" stroke="none" text-anchor="middle">{label}</text>']
for key,name,y,actor in cases:
 obj,view=classifier(key,'UMLUseCase',name,390,y-44,520,88)
 assoc={'_type':'UMLAssociation','_id':uid(key+'assoc'),'_parent':ref(model),'end1':{'_type':'UMLAssociationEnd','_id':uid(key+'end1'),'reference':ref(actor[0])},'end2':{'_type':'UMLAssociationEnd','_id':uid(key+'end2'),'reference':ref(obj)}}
 for end in ('end1','end2'):assoc[end]['_parent']=ref(assoc)
 model['ownedElements'].append(assoc)
 sy=365 if actor is guest else 1075
 views.append({'_type':'UMLAssociationView','_id':uid(key+'edge'),'_parent':ref(diagram),'model':ref(assoc),'tail':ref(actor[1]),'head':ref(view),'lineStyle':1,'points':f'205:{sy};310:{y};390:{y}'})
 svg += [f'<polyline points="165,{sy} 310,{y} 390,{y}" fill="none"/>',f'<ellipse cx="650" cy="{y}" rx="260" ry="44"/>']
 lines=name.split('\n')
 for j,line in enumerate(lines):
  text_y=y+6 if len(lines)==1 else y-5+j*23
  svg.append(f'<text x="650" y="{text_y}" text-anchor="middle" fill="black" stroke="none" font-weight="bold">{escape(line)}</text>')
inheritance={'_type':'UMLGeneralization','_id':uid('inherit'),'_parent':ref(creator[0]),'source':ref(creator[0]),'target':ref(guest[0])}
creator[0]['ownedElements']=[inheritance]
views.append({'_type':'UMLGeneralizationView','_id':uid('inheritview'),'_parent':ref(diagram),'model':ref(inheritance),'tail':ref(creator[1]),'head':ref(guest[1]),'lineStyle':1,'points':'130:1020;130:465'})
svg += ['<path d="M130 1020 V490" fill="none"/><path d="M130 465 L118 490 L142 490 Z"/>','</g></svg>']

def audit(project):
 ids=[];refs=[]
 def walk(n):
  if isinstance(n,dict):
   if '_id' in n:ids.append(n['_id'])
   if '$ref' in n:refs.append(n['$ref'])
   for v in n.values():walk(v)
  elif isinstance(n,list):
   for v in n:walk(v)
 walk(project)
 assert len(ids)==len(set(ids))
 assert set(refs)<=set(ids)
for path,project in zip(paths,projects):
 before=[m for m in project['ownedElements'] if m.get('name')!=model_name]
 project['ownedElements']=[deepcopy(model) if m.get('name')==model_name else m for m in project['ownedElements']]
 assert before==[m for m in project['ownedElements'] if m.get('name')!=model_name]
 audit(project)
 path.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'frontend/docs/costs_usecases.svg').write_text('\n'.join(svg),encoding='utf-8')

# Every association stays to the left of the complete oval column until it
# reaches the centre of its own oval. This remains safe if StarUML changes
# an oval's width to accommodate its label.
for key, name, y, actor in cases:
 sy=365 if actor is guest else 1075
 segments=[((165,sy),(310,y)),((310,y),(390,y))]
 for other_key, other_name, other_y, other_actor in cases:
  if other_key==key: continue
  for (ax,ay),(bx,by) in segments:
   # Analytic minimum distance from a segment to the normalized ellipse.
   px,py=(ax-650)/260,(ay-other_y)/44
   dx,dy=(bx-ax)/260,(by-ay)/44
   t=max(0,min(1,-(px*dx+py*dy)/(dx*dx+dy*dy)))
   assert (px+t*dx)**2+(py+t*dy)**2>1, (key,other_key)
print('12 use cases; 24 association segments checked against all unrelated ovals; all IDs and references valid; other diagrams preserved.')

