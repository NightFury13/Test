#-*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################



@auth.requires_login()
def profile():
	name=db(auth.user_id==db.auth_user.id).select(db.auth_user.first_name,db.auth_user.last_name)
	name=name[0]['first_name']+' '+name[0]['last_name']
	age=db(auth.user_id==db.auth_user.id).select(db.auth_user.age)
	age=age[0]['age']
	sex=db(auth.user_id==db.auth_user.id).select(db.auth_user.sex)
	sex=sex[0]['sex']	
	email=db(auth.user_id==db.auth_user.id).select(db.auth_user.email)
	email=email[0]['email']
	contact=db(auth.user_id==db.auth_user.id).select(db.auth_user.phone)
	contact=contact[0]['phone']
	usertype=db(auth.user_id==db.auth_user.id).select(db.auth_user.usertype)
	usertype=usertype[0]['usertype']
	issues=[]
	if (usertype=='Librarian'):
		a=request.now
		issues=db((db.issue.idate<=a) & (db.issue.userid==db.auth_user.id) & (db.issue.bookid==db.books.id)).select(db.auth_user.first_name,db.auth_user.id,db.books.id,db.auth_user.email,db.issue.idate,db.books.name)		
	bookid=db(db.issue.userid==auth.user_id).select(db.issue.bookid,db.issue.idate)
	books=db(db.books.id>0).select()
	issuedbooks=[]
	for i in bookid:
		issuedbooks.append((books[i['bookid']-1],i['idate']))
	bc='Thankyou'
	addbook=SQLFORM(db.books)
	if usertype=='Librarian':
		bc=''
	return locals()

def notify():
	userid=int(request.args(0))
	username=db(db.auth_user.id==userid).select(db.auth_user.first_name)
	username=username[0]['first_name']
	bookid=int(request.args(1))
	bookname=db(db.books.id==bookid).select(db.books.name)
	bookname=bookname[0]['name']
	email=db(db.auth_user.id==userid).select(db.auth_user.email)
	email=email[0]['email']
	mail.send(email,subject='[IIIT-H: Library] Reminder!',message='Dear '+username+', Your book, '+bookname+' is due for submission.')
	return dict(message="Email sent succesfully!")

def authtalk():
	form=SQLFORM(db.authtalk)
	if form.accepts(request.vars):
		mess=db(db.authtalk.id>0).select()
		mess=mess[-1]
		mail.send('mohit.jain@students.iiit.ac.in',subject=mess['subject'],message=mess['conte'])
		return dict(form=form,message="Email sent succesfully!")
	else:
	 	return dict(form=form,message="Please provide your name and email address in the content of the mail.")

def usertalk():
	form=SQLFORM(db.usertalk)
	if form.accepts(request.vars):
		mess=db(db.usertalk.id>0).select()
		mess=mess[-1]
		mail.send(mess['reciever'],subject=mess['subject'],message=mess['conte'])
		return dict(form=form,message="Email sent succesfully!")
	else:
		return dict(form=form,message="Please enter only one user at a time.")

@auth.requires_login()	
def newbookreq():
	req=db(db.newbookreq.id==db.bookresponse.book).select(db.newbookreq.book,db.newbookreq.author,db.newbookreq.edition,db.newbookreq.publisher,db.bookresponse.status)
	forma=SQLFORM(db.newbookreq)
	if forma.accepts(request.vars):
		response.flash = T('Request Noted')
	formb=SQLFORM(db.bookresponse)
	if formb.accepts(request.vars):
		response.flash = T('Status Updated')
	return locals()
	 
def numboo():
	records=db().select(db.books.copies)
	sume=0
	for i in range(len(records)):
		sume+=records[i]['copies']
	rec=db().select(db.books.issued)
	sumq=0
	for j in range(len(rec)):
		sumq+=rec[i]['issued']
	return dict(sume=sume,sumq=sumq,sump=sume-sumq)

def newbooks():
	forma=SQLFORM(db.books)
	if forma.accepts(request.vars,session):
		response.flash = T('Record Inserted')
	return dict(forma=forma)

@auth.requires_login()	
def faq():
	records=db(db.questions.id==db.answers.question).select(db.questions.question,db.answers.answer)
	forma=SQLFORM(db.questions)
	if forma.accepts(request.vars):
		response.flash = T('Question Posted')
	formb=SQLFORM(db.answers)
	if formb.accepts(request.vars):
		response.flash = T('Answer Posted')
	return dict(forma=forma,formb=formb,records=records)

def signup():
	form=SQLFORM(auth_user)
	if form.accepts(request.vars):
		response.flash = T('Record Inserted')
	return dict(form=form)

def rate():
	form=SQLFORM(db.rate)
	if form.accepts(request.vars):
		response.flash = T('Book Rated!')
	return dict(form=form)

def issue():
	bookid=request.args(0)
	state=db((db.issue.userid==auth.user_id) & (db.issue.bookid==bookid)).select()
	if ((state)):
		return dict(message='You have already made a request for this book!')
	else:
		db.issue.insert(userid=auth.user_id,bookid=bookid,idate=request.now)
		return dict(message='Your request for this book has been taken.')

def cancel():
	bookid=request.args(0)
	db((db.issue.userid==auth.user_id) & (db.issue.bookid==bookid)).delete()
	return dict(message='Your request has been succesfully taken back.')

def readbook():
	a=request.args(0)
	bo=db(db.books.id==a).select()
	bo=bo[0]
	rates=db(db.rate.bookid==bo['id']).select(db.rate.rating)
	j=0
	for i in rates:
		j=j+i['rating']
	if (len(rates)):
		rating=j/len(rates)
	else:
		rating=3
	return dict(bo=bo,rating=rating)

@auth.requires_login()	
def search():
	keywords=str(request.get_vars['keywords'])
	results=[]
	if keywords:
		keywords = [x for x in keywords.split() if len(x)>3]
	if keywords:
		query1 = reduce(lambda a,b:a|b,[db.books.name.like('%'+k+'%')for k in keywords])
		query2 = reduce(lambda a,b:a|b,[db.books.author.like('%'+k+'%')for k in keywords])
		results = db(query1|query2).select()
	else:
		results=''
	return dict(results=results)
	
def complete():
	if not request.vars.vab:return ''
	pattern=request.vars.vab.capitalize()+'%'
	selected=[row.name for row in db(db.books.name.like(pattern)).select()]
	return ''.join([DIV(k,_onclick="$('#vab').attr('value','%s')"%k,_onmouseover="this.style.backgroundColor='yellow'",_onmouseout="this.style.backgroundColor='white'").xml() for k in selected])

def index():
	if not session.counter: 
		session.counter=1
	else: 
		session.counter+=1
	return dict(message=T('Hello World'),counter=session.counter,form=auth())

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
    return response.download(request, db)


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
