import sqlite3
from urllib.parse import  parse_qs
from html import  escape
import re
import sys

from wtools import Session

DBPATH='movie.sqlite3'

def mapurl(path,formdata):
    '''A url-function map to select functions'''
    # (re, function, auth required)
    urlmap = [ ('^movie/insert$', insert, True),
           ('^movie/update/(?P<id>[a-z_0-9]+)$', update, True),
           ('^movie/update$', update, True),
           ('^movie/like/(?P<id>[a-z_0-9]+)/(?P<like>yes|no)$', like, True),
           ('^movie/delete/(?P<id>[a-z_0-9]+)/(?P<name>.+)$', delete, True),
           ('^movie/delete$', delete, True),
           ('^movie/login$', login, False),
           ('^movie/logout$', logout, False),
         ]

    for (k,v,a) in urlmap:
        m = re.search(k, path)
        if m:
            # update regexp dict data on formdata
            formdata.update(m.groupdict())
            return v,a
    return None

def processform(env):
    '''parse get and post methods and return a simple dictionary'''
    try:
        if env['REQUEST_METHOD'] == 'POST':
            try:
               request_body_size = int(env.get('CONTENT_LENGTH', 0))
            except (ValueError):
                      request_body_size = 0
            p = env['wsgi.input'].read(request_body_size)
        else:
            p = env['HTTP_QUERY']
        f = parse_qs(p.decode())
        formdata = {}
        #replace with singular values in parse result i.e. {'name':['abc']} -> {'name':'abc'}
        for k in f:
            if len(f[k]) == 1 :
                formdata[k] = f[k][0]
            else:
                formdata[k] = f[k]
        print(formdata)
        return formdata
    except Exception as e:
        print('Exception:',e)
        return {}

    

def _torow(thelist):
    '''return html table row from the database row as a list'''
    r = '''<tr><td><a href="/movie/update/%s">Update</a><br/>
           <a href="/movie/delete/%s/%s">Delete</a>''' % (thelist[1], thelist[1], escape(thelist[0]))
    r = r + '''
<td>%s</td><td>%s</td><td>%s</td>''' % \
         (thelist[0],thelist[2],thelist[3])
    r = r + '''<td><a href="http://www.imdb.com/title/%s">
<img src="%s" height="100px"/>
<td>%s <a href="/movie/like/%s/yes">like</a>,<br/> %s <a href="/movie/like/%s/no">dislike</a></td>\n''' %\
        (thelist[4],thelist[5],thelist[6], thelist[1], thelist[7], thelist[1])
    r = r + '</tr>\n'''
    return r

def _showcurrent(db,offset=0):
    '''return current content of the movie table'''
    r = '<table border="1" cellspacing="0">'
    c = db.cursor()
    # gives 5 rows from specified offset
    c.execute('''select * from movies
             order by name''' )
    cnt = 0
    for i in c:
        r = r + _torow(i)
        cnt += 1

    r = r + '</table>' 
    return r

# this one is used to generate the page. %s replaced by the content
_template = '''
<html>
<title> Database for Movie Night</title>
<body>
<h1>Movies List</h1>
<p>
<a href="/movie/insert">Add new</a>
<a href="/movie/logout">Logout</a>
</p>
%s
</form>
'''
import hashlib
        
def application(env,start_resp):
    '''main page handler'''
    resp=[('content-type','text/html; charset=UTF-8')]

    # process form data on user input
    formdata = processform(env)
    view = mapurl(env['PATH_INFO'][1:],formdata)
    if view:
        if view[1]:    # authentication required
            session = Session('movies',env,resp)
            if not session.is_valid():
                # redirect to login page
                start_resp('302 Redirect',resp + [('Location','/movie/login')])
                return []
        return view[0](env,start_resp, resp,formdata)

    # login required on home page too
    session = Session('movies',env,resp)
    if not session.is_valid():
        # redirect to login page
        start_resp('302 Redirect',resp + [('Location','/movie/login')])
        return []
    try:
      db = sqlite3.connect(DBPATH)
      db.text_factory = str
      # show current list of movies
      t = _showcurrent(db)
    except sqlite3.Error as e:
      t =  '<br/><strong>Database error:</strong><br/>'+e.args[0]
    start_resp('200 OK', resp)
    return [(_template % t).encode()]

def insert(env,start_resp,resp, kw):
    try:
        insert = kw['insert']
    except:
        insert = None


    if insert:    # if insert form is submitted
        try:
          db = sqlite3.connect(DBPATH)
          db.text_factory = str
          # id is given as None for autoinrement id
          db.execute('''insert into movies values
                 (?,?,?,?,?,?,0,0)''',
                (kw['title'],None,kw['director'],
                 kw['cast'], kw['imdb'],kw['poster']))
          db.commit()
          # redirect to main page
          start_resp('307 Redirect',resp + [('Location','/movie/')])
          return []
        except sqlite3.Error as e:
            t =  DBPATH + '<br/><strong>Database error:</strong><br/>'+e.args[0]
            start_resp('200 OK',resp)
            return [(_template % t).encode()]
        except KeyError as key:
            t =  'form is invalid fill in field %s' % (key)
            start_resp('200 OK',resp)
            return [(_template % t).encode()]
    # else, if coming first time from main page
    insertform='''
<form action="/movie/insert" method="post">
    <table border="0">'''
    for i in ('title','director','cast','imdb','poster'):
        insertform = insertform + '''
<tr><td><b>%s</b></td>
    <td><input type="text" name="%s" size="50"></td></tr>''' % (i,i)
    insertform = insertform + '''
<tr><td colspan="2" align="right">
    <input type="submit" name="insert" value="Add">
    </td></tr>'''

    start_resp('200 OK',resp)
    return [(_template % insertform).encode()]

def update(env,start_resp,resp, kw):
    print(kw)
    try:
        update = kw['update']
    except:
        update = None

    try:
        id = kw['id']
    except:
        id = None

    if update:    # if update form is submitted
        try:
          db = sqlite3.connect(DBPATH)
          db.text_factory = str
          # update the record based on id
          db.execute('''update movies set
                  name = ? , director = ?,
                  cast = ?, imdb = ?,
                  poster = ? where id = ? ''',
                (kw['title'],kw['director'],
                 kw['cast'], kw['imdb'],kw['poster'],id))
          db.commit()
          # redirect to main page
          start_resp('307 Redirect',resp + [('Location','/movie/')])
          return []
        except sqlite3.Error as e:
            t =  DBPATH + '<br/><strong>Database error:</strong><br/>'+e.args[0]
            start_resp('200 OK',resp)
            return [(_template % t).encode()]
        except KeyError as key:
            t =  'form is invalid fill in field %s' % (key)
            start_resp('200 OK',resp)
            return [(_template % t).encode()]
    # else, if comming from main page
    try:
      db = sqlite3.connect(DBPATH)
      db.text_factory = str
      c = db.cursor()
      # get current record values, we need to fill in the current values
      c.execute('''select * from movies where id=?''', (id,))
      row = c.fetchone()
    except sqlite3.Error as e:
        t =  '<br/><strong>Database error:</strong><br/>'+e.args[0]
        start_resp('200 OK',resp)
        return [(_template % t).encode()]
    insertform='''
<form action="/movie/update" method="post">
<input type="hidden" name="id" value="%s">
    <table border="0">''' % id

    colnames = ['title','id','director','cast','imdb','poster']
    for i in [0,2,3,4,5]:
        insertform = insertform + '''
<tr><td><b>%s</b></td>
    <td><input type="text" name="%s" value="%s" size="50">
    </td></tr>''' %  (colnames[i],colnames[i],row[i])

    insertform = insertform + '''
<tr><td colspan="2" align="right">
    <input type="submit" name="update" value="Update">
    </td></tr>'''
    start_resp('200 OK',resp)
    return [(_template % insertform).encode()]

def like(env,start_resp,resp, kw):
    try:
        like = kw['like']
    except:
        like = None

    try:
        id = kw['id']
    except:
        id = None

    if not id or not like:
        t =  'Invalid parameters <a href="/movie/">Go back</a>'
        start_resp('200 OK',resp)
        return [(_template % t).encode()]
    else:  # depending on like parameters value 
        try:
          db = sqlite3.connect(DBPATH)
          db.text_factory = str
          if like == 'yes':
            # increment likes
            db.execute('''update movies set likes=likes+1
                    where id=?''',(id,))
            db.commit()
          elif like == 'no':
            # increment dislikes
            db.execute('''update movies set dislikes=dislikes+1
                    where id=?''',(id,))
            db.commit()
          # redirect to main page
          start_resp('307 Redirect',resp + [('Location','/movie/')])
          return []
        except sqlite3.Error as e:
            t =  '<br/><strong>Database error:</strong><br/> <a href="/movie/">Go back</a>'+e.args[0]
            start_resp('200 OK',resp)
            return [(_template % t).encode()]

        
def delete(env,start_resp,resp, kw):
    try:
        name = kw['name']
    except:
        name = None

    try:
        id = kw['id']
    except:
        id = None

    if not id :    # if no parameter suppllied goto main page
        t =  'Invalid parameters <a href="/movie/">Go back</a>'
        start_resp('200 OK',resp)
        return [(_template % t).encode()]

    # if coming from main page, show confirmation form
    if not ('submit' in kw):
        t = '''        
        Do yo really want to delete the movie "%s"?
        <form action="/movie/delete" method="post">
        <input type="hidden" name="id" value="%s">
        <input type="submit" name="submit" value="Yes">
        <input type="submit" name="submit" value="Cancel">
        </form>''' % (name,id)
        start_resp('200 OK',resp)
        return [(_template % t).encode()]
    if kw['submit'] != "Yes":    # if no  confirmation
        start_resp('302 Redirect',resp + [('Location','/movie/')])
        return []

    # now we can delete
    try:
      db = sqlite3.connect(DBPATH)
      db.text_factory = str
      db.execute('''delete from movies where id=?''',(id,))
      db.commit()
      start_resp('307 Redirect',resp + [('Location','/movie/')])
      return []
    except sqlite3.Error as e:
      t =  '<br/><strong>Database error:</strong><br/>'+e.args[0]
      start_resp('200 OK',resp)
      return [(_template % t).encode()]
        
    
def login(env,start_resp,resp, kw):
    '''check username,password if supplied,
       else return the form for login'''
    try:
        username = kw['username']
    except:
        username = None

    try:
        password = kw['password']
    except:
        password = None

    form = '''
guest password guest
visitor password visitor
<form action="/movie/login" method="post">
<input type="input" name="username" size=20/><br/>
<input type="password" name="password" size=20/><br/>
<input type="submit" name="action" value="Login"/>
</form>
    '''
    if username and password:    # login form submitted
        # get plain password and get one way digest of it.
        encpass = hashlib.md5(('movies:'+password).encode()).hexdigest()
        db = sqlite3.connect(DBPATH)
        db.text_factory = str
        c = db.cursor()
        # authenticate by checking username,encrypted passwd pair
        c.execute('select username from passwords where username=? and password=?',(username, encpass))
        if c.fetchone():
          # login successfull
          session = Session('movies',env,resp)
          session.create(username)

          # redirect to main page, ignore handlers
          start_resp('302 Redirect',resp + [('Location','/movie')])
          return []
          t = '<br/><strong>Database error:</strong><br/>'+e.args[0]
          start_resp('200 OK',resp )
          return [(_template % t).encode()]
    start_resp('200 OK',resp )
    return [(_template % form).encode()]
        

def logout(env,start_resp,resp, kw):
    session = Session('movies',env,resp)
    # invalidate (delete) session info, from storage and browser
    session.destroy()
    
    start_resp('200 OK',resp) 
    return [(_template % 'you are succesfully logged-out <a href="/movie/">Go back</a>').encode()]

if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    httpd = make_server('', 9000, application)
    print("Serving on port 9000...")
    httpd.serve_forever()
