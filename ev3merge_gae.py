
#vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import os
import webapp2
import StringIO
from ev3 import Ev3

HTML_DIR = os.path.join(os.path.dirname(__file__), 'static', 'html')

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(open(os.path.join(HTML_DIR, 'index.html')).read())

    def post(self):
	upload_files = self.request.POST.multi.getall('file')
	base_file = upload_files.pop()
        name, _ = os.path.splitext(base_file.filename)
	merged = Ev3(base_file.file, name=name)
	
	for upload_file in upload_files:
            name, _ = os.path.splitext(upload_file.filename)
	    merged.merge(Ev3(upload_file.file, name=name))

	outfile = StringIO.StringIO()
	merged.write(outfile)
	outfile.seek(0)
        
        self.response.headers['Content-type'] = 'application/octet-stream'
        self.response.headers['Content-Disposition'] = 'attachment; filename=merged.ev3'
        self.response.write(outfile.read())

app = webapp2.WSGIApplication([('/', MainPage),], debug=True)
