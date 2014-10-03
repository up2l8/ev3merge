
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
        self.session['uploads'] = []
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(open(os.path.join(HTML_DIR, 'index.html')).read())

class UploadHandler(BaseHandler):

    def post(self):        
        if 'file' in self.request.POST.multi:
            upload_files = self.request.POST.multi.getall('file')
        else:
            upload_files = [value for key, value in self.request.POST.multi.items() if key.startswith('file')]

        session_uploads = self.session.setdefault('uploads', [])
        
        for fstorage in upload_files:
            fname = fstorage.filename
            fdata = fstorage.file.read()
            session_uploads.append((fname, b64encode(fdata)))

        self.session['uploads'] = session_uploads
        print [f[0] for f in self.session['uploads']]

class MergeHandler(BaseHandler):

    def get(self):
        upload_files = self.session['uploads']
	filename, fdata = upload_files.pop()
        fdata = b64decode(fdata)
        name, _ = os.path.splitext(filename)
	merged = Ev3(StringIO(fdata), name=name)
	
	for filename, fdata in upload_files:
            fdata = b64decode(fdata)
            name, _ = os.path.splitext(filename)
	    merged.merge(Ev3(StringIO(fdata), name=name))

	outfile = StringIO()
	merged.write(outfile)
	outfile.seek(0)
        
        self.response.headers['Content-type'] = 'application/octet-stream'
        self.response.headers['Content-Disposition'] = 'attachment; filename=merged.ev3'
        self.response.write(outfile.read())

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key-asdf-asdf-asdf'}

handlers = [('/', IndexHandler),
            ('/upload', UploadHandler),
            ('/merge', MergeHandler)]
app = webapp2.WSGIApplication(handlers, debug=True, config=config)
