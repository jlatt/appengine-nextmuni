import logging

from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

from geo import geotypes

from nextmuni import model


log = logging.getLogger('main')


class JSONRequestHandler(webapp.RequestHandler):
    def write_json(self, **kwargs):
        self.response.headers['Content-Type'] = 'application/json'
        json.dump(kwargs, self.response.out)

class Stops(JSONRequestHandler):
    def get(self):
        n = float(self.request.get('n'))
        e = float(self.request.get('e'))
        s = float(self.request.get('s'))
        w = float(self.request.get('w'))
        box = geotypes.Box(n, e, s, w)
        stops = model.Stop.bounding_box_fetch(model.Stop.all(), box, max_results=25)
        def to_dict(stop):
            stop_dict = dict(
                location=dict(lat=stop.location.lat, lng=stop.location.lon),
                short_title=stop.short_title,
                title=stop.title,
                stop_id=stop.stop_id,
                tag=stop.tag,
                key=str(stop.key()),
                )
            return stop_dict
        stop_dicts = map(to_dict, stops)
        log.debug('stop_dicts=%r', stop_dicts)
        self.write_json(stops=stop_dicts)


class Stop(JSONRequestHandler):
    def get(self, stop_key):
        stop = model.Stop.get(stop_key)
        rd_stops = list(stop.route_direction_stops)
        directions = [rd_stop.direction for rd_stop in rd_stops]
        routes = [direction.route for direction in directions]

        def direction_to_dict(direction):
            return dict(
                title=direction.title,
                tag=direction.tag,
                key=str(direction.key()),
                route_key=str(direction.route.key()),
                )

        def route_to_dict(route):
            return dict(
                title=route.title,
                tag=route.tag,
                key=str(route.key()),
                )

        self.write_json(
            directions=map(direction_to_dict, directions),
            routes=map(route_to_dict, routes),
            )


application = webapp.WSGIApplication([
        ('/api/stop/(.+)', Stop),
        ('/api/stops.*', Stops),
        ], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
