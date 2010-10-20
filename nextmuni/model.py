from google.appengine.api import memcache
from google.appengine.ext import db

from geo import geomodel


__author__ = 'Jeremy Latt <jeremy.latt@gmail.com>'


class Tagged(db.Model):
    short_title = db.StringProperty()
    title = db.StringProperty()

    @property
    def tag(self):
        return self.key().name()


class Route(Tagged):
    # directions = [RouteDirection]
    pass


class Stop(geomodel.GeoModel, Tagged):
    stop_id = db.StringProperty()
    # route_direction_stops = [RouteDirectionStop]


class RouteDirection(Tagged):
    route = db.ReferenceProperty(Route, collection_name='directions')
    use_for_ui = db.BooleanProperty(default=False)
    # route_direction_stops = [RouteDirectionStop]


class RouteDirectionStop(db.Model):
    index = db.IntegerProperty()
    stop = db.ReferenceProperty(Stop, collection_name='route_direction_stops')
    direction = db.ReferenceProperty(RouteDirection, collection_name='route_direction_stops')
