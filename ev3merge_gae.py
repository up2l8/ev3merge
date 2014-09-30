
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

app = webapp2.WSGIApplication([('/', MainPage),], debug=True)
