from google.appengine.api import memcache
from google.appengine.ext import db

from geo import geomodel


__author__ = 'Jeremy Latt <jeremy.latt@gmail.com>'


class Tagged(db.Model):
    short_title = db.StringProperty()
    tag = db.StringProperty()
    title = db.StringProperty()


class Route(Tagged):
    # directions = [RouteDirection]
    # stops = [Stop]
    pass


class Stop(geomodel.GeoModel, Tagged):
    route = db.ReferenceProperty(Route, collection_name='stops')
    stop_id = db.StringProperty()


class RoutePath(db.Model):
    # directions = [RouteDirection]
    points = db.ListProperty(db.GeoPt)


class RouteDirection(Tagged):
    path = db.ReferenceProperty(RoutePath, collection_name='directions')
    route = db.ReferenceProperty(Route, collection_name='directions')
    stops = db.ListProperty(db.Key)
    use_for_ui = db.BooleanProperty(default=False)
