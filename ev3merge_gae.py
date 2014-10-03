
#vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import os
from StringIO import StringIO
from base64 import b64encode, b64decode

#Webapp stuff:
import webapp2
from webapp2_extras import sessions

#Application stuff:
from ev3 import Ev3

HTML_DIR = os.path.join(os.path.dirname(__file__), 'static', 'html')

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session(backend='memcache')

class IndexHandler(BaseHandler):
    def get(self):        
        self.session['merged'] = None
        self.session['log'] = ''
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(open(os.path.join(HTML_DIR, 'index.html')).read())

class UploadHandler(BaseHandler):

    def post(self):
        if 'file' in self.request.POST.multi:
            upload_files = self.request.POST.multi.getall('file')
        else:
            upload_files = [value for key, value in self.request.POST.multi.items() if key.startswith('file')]

        merged = self.session['merged']
        
        if merged:
            merged_data = StringIO(b64decode(merged))
            merged = Ev3(merged_data)
        else:
            fstorage = upload_files.pop()
            name, _ = os.path.splitext(fstorage.filename)
            self.session['log'] = 'Reading %s\n' % name
            merged = Ev3(fstorage.file)
        
        for fstorage in upload_files:
            name, _ = os.path.splitext(fstorage.filename)
            self.session['log'] += 'Merging %s\n' % name
	    log = merged.merge(Ev3(fstorage.file, name=name))
            self.session['log'] += log

	outfile = StringIO()
	merged.write(outfile)
	outfile.seek(0)
        
        self.session['merged'] = b64encode(outfile.read())

class MergeHandler(BaseHandler):

    def get(self):
        self.response.headers['Content-type'] = 'application/octet-stream'
        self.response.headers['Content-Disposition'] = 'attachment; filename=merged.ev3'
        self.response.write(b64decode(self.session['merged']))

class LogHandler(BaseHandler):

    def get(self):
        log =  self.session['log']
        self.response.headers['Content-type'] = 'text/plain'
        self.response.write(log)

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key-asdf-asdf-asdf'}

handlers = [('/', IndexHandler),
            ('/upload', UploadHandler),
            ('/merge', MergeHandler),
            ('/log', LogHandler)]
app = webapp2.WSGIApplication(handlers, debug=True, config=config)
