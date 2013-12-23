# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)word_select?check=1
## - call exposes all registered services (none by default)
#########################################################################
import os,subprocess
def index():
    redirect(URL('home'))
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = "Welcome to web2py!"
    return dict(message=T('Hello World'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())




@auth.requires_login()
def home():
    t = auth.user.id
    h = db(db.rules.userid==t).select()
    g = []
    for i in h:
        g.append(db(db.words.id==i.wid).select(db.words.word))
    h=[]
    for i in g:
        for j in i:
            h.append(j.word) 
    h=list(set(h))
    return dict(t=t,h=h)

@auth.requires_login()
def word_select():
    if not request.vars.check:
        redirect('home')
    else:
        check=0
    if request.vars.submit:
        session.level = request.vars.level
        w = request.vars.word
        t = db(db.words).select()
        for i in t:
            if i.word==w:
                session.word = w
                session.ide = i.id
                break
        redirect('sentence_select')
    return dict()

@auth.requires_login()
@auth.requires_membership('admin')
def changelevel():
    if request.vars.submit:
        if request.vars.new_email:
            db(db.user_level).insert(email=request.vars.new_email,level=request.vars.level)
        else:
            db(db.user_level.email==request.vars.emailq).update(level=request.vars.level)
        redirect('home')
    return dict()


@auth.requires_login()
def word_selectc():
    if not request.vars.check:
        redirect('home')
    else:
        check=0
    if request.vars.submit:
        session.level = request.vars.level
        w = request.vars.word
        t = db(db.words).select()
        for i in t:
            if i.word==w:
                session.word = w
                session.ide = i.id
                break
        redirect(URL('sentence_selectc',vars=dict(second=request.vars.second)))
    return dict()
    
#@auth.requires_login()
#def reason():
#    t=session.senid
#    pre=db((db.rules.wid==session.ide)&(db.rules.sid==session.sid)).select()
#    c=0
#    for i in pre:
#        c+=1
#    if request.vars.hindit:
#        db.rules.insert(name=session.word+str(c),userid=auth.user.id,wid=session.ide,sid=session.sid,translation=hindit)
#        redirect(URL('rel'))
#    return dict()
    
    
@auth.requires_login()
def sentence_select():
    print '*'
    f = ''
    x = 0
    if request.vars.submit and (request.vars.hindit):
        t = request.vars.sentence
        r = db(db.sentences.esentence==t).select(db.sentences.id)
        for i in r:
          session.sid=i.id
          break
        pre=db((db.rules.wid==session.ide)&(db.rules.userid==auth.user.id)).select()
        c=0
        f=0
        for i in pre:
            c+=1
            if str(session.sid)==i.sid:
                f=1
                break
        if f==0:
            db.rules.insert(name=session.word+str(c),userid=auth.user.id,wid=session.ide,sid=session.sid,translation=request.vars.hindit)
            session.f=0
        redirect(URL('typ'))
    return dict(w=session.word,d=session.ide,f=f,level_set=session.level)


@auth.requires_login()
def sentence_selectc():
    print '*'
    f = ''
    x = 0
    if request.vars.submit:
        t = request.vars.sentence
        r = db(db.sentences.esentence==t).select(db.sentences.id)
        for i in r:
          hindit=i.id
          session.sid=i.id
          break
        redirect(URL('reasonc',vars=dict(hindit=hindit)))
    return dict(w=session.word,d=session.ide,f=f,level_set=session.level)


@auth.requires_login()
def reasonc():
    t=session.sid
    r = db(db.sentences.id==t).select(db.sentences.hsentence)
    if request.vars.advanced or request.vars.novice:
        pre=db((db.rules.wid==session.ide)&(db.rules.userid==auth.user.id)).select()
        c=0
        f=0
        for i in pre:
            c+=1
            if i.sid==str(session.sid):
                f=1
                break
        if f==0:
            db.rules.insert(name=session.word+str(c),userid=auth.user.id,wid=session.ide,sid=session.sid)
        session.f=0
	if request.vars.advanced:
	  redirect(URL('typ'))
	else:
	  redirect(URL('novi'))
    return dict(r=r)

@auth.requires_login()
def novi():
  t=session.sid
  r=db(db.sentences.id==t).select(db.sentences.esentence)
  r=r[0].esentence
  l=r.split()
  w=session.word
  return dict(l=l,w=w)
@auth.requires_login()
def novi_insert():
    print request.vars.property,request.vars.word
    a=db((db.novice.userid==auth.user.id)&(db.novice.wid==session.ide)&(db.novice.sid==session.sid)&(db.novice.word==request.vars.word)).select()
    if a:
        if request.vars.property=='1':
            print 'haha'
            db((db.novice.userid==auth.user.id)&(db.novice.wid==session.ide)&(db.novice.sid==session.sid)&(db.novice.word==request.vars.word)).update(relation=1,property=0,both=0)
        elif request.vars.property=='2':
            db((db.novice.userid==auth.user.id)&(db.novice.wid==session.ide)&(db.novice.sid==session.sid)&(db.novice.word==request.vars.word)).update(relation=0,property=1,both=0)
        elif request.vars.property=='3':   
            db((db.novice.userid==auth.user.id)&(db.novice.wid==session.ide)&(db.novice.sid==session.sid)&(db.novice.word==request.vars.word)).update(relation=0,property=0,both=1)                     
    else:
        if request.vars.property=='1':
            db.novice.insert(userid=auth.user.id,sid=session.sid,wid=session.ide,word=request.vars.word,relation=1,property=0,both=0)
        elif request.vars.property=='2':
            db.novice.insert(userid=auth.user.id,sid=session.sid,wid=session.ide,word=request.vars.word,relation=0,property=1,both=0)
        elif request.vars.property=='3':
            db.novice.insert(userid=auth.user.id,sid=session.sid,wid=session.ide,word=request.vars.word,relation=0,property=0,both=1)
    return None
@auth.requires_login()
@auth.requires_membership('admin')
def delaccount():
    if request.vars.submit:
        db(db.auth_user.email==request.vars.email).delete()
        redirect("home")
    return dict()

@auth.requires_login()
@auth.requires_membership('admin')
def addword():
    if request.vars.submit:
       db.words.insert(word=request.vars.word)
       word=request.vars.word
       db.sentences.insert(level=request.vars.level,esentence=request.vars.esentence,hsentence=request.vars.hsentence)
       w = db(db.words.word==request.vars.word).select(db.words.id)
       s = db(db.sentences.esentence==request.vars.esentence).select(db.sentences.id)
       #s=db(db.sentences.id==session.sid).select(db.sentences.esentence)
       #s=s[0].esentence
       sen=request.vars.esentence
       print sen,word
       f=open('sample','w')
       st="\n<TITLE> test. </TITLE>\n<p>\n" + sen + "\n</p>\n"
       f.write(st)
       f.close()
       os.system("/bin/bash Anusaaraka_stanford.sh sample 0 True")
       f=open(os.environ['HOME_anu_tmp']+'/tmp/sample_tmp/2.1/word.dat','r')
       for line in f:
           ind=line.rfind(' '+word)
           print word+'*'+line
           print "index"+str(ind)
           if ind != -1 :
               print '*'
               anu_id=line[ind-2]
               break
       f.close() 
       print "anu_id= " + anu_id
       f=open(os.environ['HOME_anu_tmp']+'/tmp/sample_tmp/2.1/cat_consistency_check.dat','r')
       for line in f:
           ind=line.find('id-cat_coarse '+anu_id)
           if ind != -1 :
               line=line[::-1]
               end=line.find(' ')
               psp=line[2:end][::-1]
               break
       f.close()
       for i in w:
           for j in s:
               db.links.insert(wid=i.id,sid=j.id,typ=psp)
               break
           break
       f=open(os.environ['HOME_anu_tmp']+'/tmp/sample_tmp/2.1/word.dat','r')
       d={}
       for i in f:
           i=i.strip()
           if i.find('id-word')!=-1:
               d[i[9]]=i[12:-1]
       f.close()
       f=open(os.environ['HOME_anu_tmp']+'/tmp/sample_tmp/2.1/relations.dat','r')
       l,l1,l2=[],[],[]
       for i in f:
           i=i.strip()
           if i[-4]==str(anu_id):
               l1.append(i[:-4].strip()+')'+' '+' '+str(anu_id)+','+'\"'+str(word)+'\"'+' '+i[-2]+','+'\"'+d[i[-2]]+'\"')
           elif i[-2]==str(anu_id):
               l2.append(i[:-4].strip()+')'+' '+' '+i[-2]+','+'\"'+d[i[-4]]+'\"'+' '+str(anu_id)+','+'\"'+str(word)+'\"')
       l=l1+l2
       f.close()
       for r in l:
           db.rel_all.insert(wid=w[0].id,sid=s[0].id,relation=r)
       session.flash="Word Added"
       redirect('home')
    return dict()

@auth.requires_login()
@auth.requires_membership('admin')
def delword():
    if request.vars.submit:
        g = db(db.words.word==request.vars.word).select(db.words.id)
        for i in g:
            db(db.words.id==i.id).delete()
            db(db.rules.wid==i.id).delete()
            y = db(db.links.wid==i.id).select(db.links.sid)
            db(db.links.wid==i.id).delete()
            for j in y:
                db(db.sentences.id==j.sid).delete()
                break
            break
            session.flash="Word Deleted "
        redirect('home')
    return dict()

def typ():
  psp=db((db.links.sid==session.sid)&(db.links.wid==session.ide)).select(db.links.typ)
  psp=psp[0].typ
  session.psp=psp
  if request.vars.submit and request.vars.typ:
    db((db.rules.userid==auth.user.id)&(db.rules.wid==session.ide)&(db.rules.sid==session.sid)).update(typ=psp)
    if request.vars.typ=='yes':
      redirect(URL('index'))
    else:
      redirect(URL('rel'))
  return dict(psp=psp) 

def rel():
    s=db((db.rel_all.wid==session.ide)&(db.rel_all.sid==session.sid)).select(db.rel_all.relation)
    l=[]
    for i in s:
        l+=[i.relation]
    fields=[]   
    fields.append(Field('Relations',widget=SQLFORM.widgets.multiple.widget,requires=IS_IN_SET(l,multiple=True)))
    if session.psp!='adverb':
        fields.append(Field('ans',label='Is the relation sufficient for forming the rule ?',widget=SQLFORM.widgets.radio.widget,requires=IS_IN_SET(['yes','no'])))
    form=SQLFORM.factory(*fields)
    if form.accepts(request.vars,session):
        for i in form.vars.Relations:
            print "i="+str(i)
            db.rel_rule.insert(wid=session.ide,sid=session.sid,relation=i)
        if session.psp=='adverb':
            redirect('index')
        elif form.vars.ans=='yes':
            redirect('index')
        else :
            redirect(URL('nature_'+str(session.psp)))
    return dict(form=form)

def nature_noun():
    form=SQLFORM.factory(
        Field('Nature',requires=IS_IN_SET(['Animate','Inanimate','Human','Place','Time']),label='Semantic Property'))
    if form.accepts(request.vars,session):
        db((db.rules.userid==auth.user.id)&(db.rules.wid==session.ide)&(db.rules.sid==session.sid)).update(property=form.vars.Nature)
        redirect(URL('index'))
    return dict(form=form)

def nature_verb():
    form=SQLFORM.factory(
        Field('Nature',requires=IS_IN_SET(['transitive','intransitive'])))
    if form.accepts(request.vars,session):
        db((db.rules.userid==auth.user.id)&(db.rules.wid==session.ide)&(db.rules.sid==session.sid)).update(property=form.vars.Nature)
        redirect(URL('index'))
    return dict(form=form)

def nature_adjective():
    form=SQLFORM.factory(
        Field('Nature',requires=IS_IN_SET(['Animate','Inanimate','Human','Place','Time']),label='Semantic Property of noun whom it modifies'))
    if form.accepts(request.vars,session):
        db((db.rules.userid==auth.user.id)&(db.rules.wid==session.ide)&(db.rules.sid==session.sid)).update(property=form.vars.Nature)
        redirect(URL('index'))
    return dict(form=form)
def testt():
    v=db(db.auth_user).select()
    return dict(v=v)
def sel_novice():
    a=db(db.novice.userid==db.auth_user.id).select(db.auth_user.email,db.auth_user.id)
    l,d=[],{}
    for i in a:
        l+=[i.email]
        d[i.email]=i.id
    l=list(set(l))
    form=SQLFORM.factory(Field('user',requires=IS_IN_SET(l)))
    if form.accepts(request.vars,session):
            redirect(URL('disp_novice',vars=dict(uid=d[form.vars.user])))
    return dict(form=form)
def disp_novice():
    u=request.vars.uid
    email=db(db.auth_user.id==u).select(db.auth_user.email)
    email=email[0].email
    l=db(db.novice.userid==u).select()
    return dict(l=l,email=email)
def sel_adv():
    a=db(db.rules.userid==db.auth_user.id).select(db.auth_user.email,db.auth_user.id)
    l,d=[],{}
    for i in a:
        l+=[i.email]
        d[i.email]=i.id
    l=list(set(l))
    form=SQLFORM.factory(Field('user',requires=IS_IN_SET(l)))
    if form.accepts(request.vars,session):
            redirect(URL('disp_adv',vars=dict(uid=d[form.vars.user])))
    return dict(form=form)
def disp_adv():
    u=request.vars.uid
    email=db(db.auth_user.id==u).select(db.auth_user.email)
    email=email[0].email
    l=db(db.rules.userid==u).select()
    return dict(l=l,email=email)
