# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate, Mail
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

from gluon.contrib.login_methods.cas_auth import CasAuth
auth.settings.login_form=CasAuth(urlbase = "https://login.iiit.ac.in/cas",actions = ['login','validate','logout'],casversion = 2,casusername="cas:user")

	
## create all tables needed by auth if not custom tables

auth.settings.extra_fields['auth_user']=[
		Field('age','integer',label='Please Enter your Age ',requires=IS_NOT_EMPTY()),
		Field('sex','string',label='Please Select your Gender ',requires=IS_IN_SET(['Male','Female']),default='Male',widget=SQLFORM.widgets.radio.widget),
		Field('phone','integer',label='Please Enter your Contact Number ',requires=IS_NOT_EMPTY()),
		Field('photo','upload',label='Please select your Profile Picture '),
		Field('usertype','string',label='You are a ',requires=IS_IN_SET(['Faculty','Student','Librarian']),default='Student',widget=SQLFORM.widgets.radio.widget),
]


auth.define_tables(username=False, signature=False)

## configure email
mail = Mail()
auth.settings.actions_disabled.append('register')
mail.settings.server = 'students.iiit.ac.in:25'
mail.settings.sender = 'mohit.jain@students.iiit.ac.in'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

auth.settings.login_next=URL('default','profile')

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('authtalk',
		Field('subject','string',label='Please provide the subject of your mail ',requires=IS_NOT_EMPTY()),
		Field('conte','text',label='Your message goes here ',requires=IS_NOT_EMPTY()))

db.define_table('usertalk',
		Field('reciever','string',label="Enter Email-Id of the reciever ",requires=[IS_NOT_EMPTY(),IS_EMAIL()]),
		Field('subject','string',label='Enter Subject of the mail here ',requires=IS_NOT_EMPTY()),
		Field('conte','text',label='Your message goes here ',requires=IS_NOT_EMPTY()))

db.define_table('questions',
		Field('question','string',label='Please post your question here ',requires=IS_NOT_EMPTY()))

db.define_table('answers',
		Field('question',db.questions,requires=IS_IN_DB(db,'questions.id','questions.question')),
		Field('answer','text',label='Know the answer? Be helpful! ',requires=IS_NOT_EMPTY()))

db.define_table('newbookreq',
		Field('book','string',label='Enter Name of the Book ',requires=IS_NOT_EMPTY()),
		Field('author','string',label='Enter Name of the Author ',requires=IS_NOT_EMPTY()),
		Field('edition','integer',label='Edition of the Requested Book ',requires=IS_NOT_EMPTY()),
		Field('publisher','string',label='Publisher of the Book ',requires=IS_NOT_EMPTY()))

db.define_table('bookresponse',
		Field('book',db.newbookreq,requires=IS_IN_DB(db,'newbookreq.id','newbookreq.book')),
		Field('status','string',requires=IS_IN_SET(['Accepted','Rejected','Pending']),default='Pending'))


#db.define_table(auth.settings.table_user_name,
#		Field('name','string',label='Please Enter your Name ',requires=IS_NOT_EMPTY()),
#		Field('userid','string',label='Enter your unique Username ',requires=IS_NOT_EMPTY(),unique=True),
#		Field('passwd','password',label='Please Enter a Password ',requires=IS_NOT_EMPTY()),
#		Field('confpasswd','password',label='Please Confirm your Password ',requires=IS_NOT_EMPTY()),
#		Field('branch','string',label='Please Enter your Branch ',requires=IS_IN_SET(['CSE','CSD','ECE','ECD','CLD','CND','EHD','M.Tech','PhD']),widget=SQLFORM.widgets.radio.widget),
#		Field('photo','upload',label='Please upload a profile picture '))


#db.define_table('stud_reg',
#		Field('name','string',label='Please Enter your Name ',requires=IS_NOT_EMPTY()),
#		Field('roll','integer',label='Please Enter your RollNo. ',unique=True,requires=IS_NOT_EMPTY()),
#		Field('userid','string',label='Please Enter a Unique Id ',unique=True,requires=IS_NOT_EMPTY()),
#		Field('passwd','password',label='Please Enter your Password ',requires=IS_NOT_EMPTY()),
#		Field('confpasswd','password',label='Please Re-Enter your Password ',requires=IS_NOT_EMPTY()),
#		Field('category','string',label='You are a ',requires=IS_IN_SET(['Faculty','Student','Librarian']),widget=SQLFORM.widgets.radio.widget),
#		Field('branch','string',label='Please Enter your Branch ',requires=IS_IN_SET(['CSE','CSD','ECE','ECD','CLD','CND','EHD','M.Tech','PhD']),widget=SQLFORM.widgets.radio.widget),
#		Field('email','string',label='Please Enter your \'IIIT-H Mail\' Email-Id ',requires=[IS_EMAIL(),IS_NOT_EMPTY()]),
#		Field('phone','integer',label='Please Enter your Contact Number ',requires=IS_NOT_EMPTY()))

#db.define_table('fac_reg',
#		Field('name','string',label='Please Enter your Name ',requires=IS_NOT_EMPTY()),
#		Field('userid','string',label='Please Enter a Unique Id ',unique=True,requires=IS_NOT_EMPTY()),
#		Field('area','text',label='Please Enter your Area of Expertise '),
#		Field('passwd','password',label='Please Enter your Password ',requires=IS_NOT_EMPTY()),
#		Field('confpasswd','password',label='Please Re-Enter your Password ',requires=IS_NOT_EMPTY()),
#		Field('email','string',label='Please Enter your \'IIIT\' Email-Id ',requires=[IS_EMAIL(),IS_NOT_EMPTY()]),
#		Field('phone','integer',label='Please Enter your Contact Number ',requires=IS_NOT_EMPTY()))


db.define_table('issue',
		Field('userid','integer'),
		Field('bookid','integer'),
		Field('idate','datetime'))

db.define_table('books',
		Field('isbn','integer',label='ISBN',requires=IS_NOT_EMPTY()),
		Field('name','string',label='Name',requires=IS_NOT_EMPTY()),
		Field('subject','string',label='Subject',requires=IS_NOT_EMPTY()),
		Field('author','string',label='Author',requires=IS_NOT_EMPTY()),
		Field('publisher','string',label='Publisher',requires=IS_NOT_EMPTY()),
		Field('edition','integer',label='Edition',requires=IS_NOT_EMPTY()),
		Field('issued','integer',label='# Issued',requires=IS_NOT_EMPTY()),
		Field('copies','integer',label='# on Shelf',requires=IS_NOT_EMPTY()),
		Field('canbe','string',label='Enter type of Document',requires=IS_IN_SET(['Book','Journal','Magazine']),default='Book',widget=SQLFORM.widgets.radio.widget),
		Field('photo','upload'))

db.define_table('rate',
		Field('bookid',db.books,requires=IS_IN_DB(db,'books.id','books.name')),
		Field('rating','float',requires=IS_IN_SET(['1','2','3','4','5']),default='3'))

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
