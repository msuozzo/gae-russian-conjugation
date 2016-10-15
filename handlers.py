import os
import logging
import urlparse

import webapp2
import jinja2

import scrape


_JINJA_ENV = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)


class AckHandler(webapp2.RequestHandler):

    def get(self):
        self.response.write('ACK')


class MainHandler(webapp2.RequestHandler):

    def get(self, word):
        logging.info('Got word: %s', word)
        parsed_word = word.decode('utf8')
        logging.info('Decoded word: %s', parsed_word)

        table = scrape.GetConjugationTable(parsed_word)
        logging.info('Received table: %s', table)

        template = _JINJA_ENV.get_template('main.html')
        rendered_template = template.render({
            'word': parsed_word,
            'table': table})
        self.response.write(rendered_template)


app = webapp2.WSGIApplication([
        webapp2.Route(r'/', AckHandler),
        webapp2.Route(r'/<word:[^/]+>', MainHandler),
    ], debug=True)
