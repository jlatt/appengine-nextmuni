import logging
import os
import urllib
from xml.dom import minidom

from google.appengine.ext import db

import model


__author__ = 'Jeremy Latt <jeremy.latt@gmail.com>'
log = logging.getLogger('nextmuni.nextbus')


def element_to_point(element):
    return db.GeoPt(float(element.getAttribute('lat')), float(element.getAttribute('lon')))


def route_list(resource):
    """Create routes."""
    doc = minidom.parse(resource)

    def to_route(element):
        tag = element.getAttribute('tag')
        route = model.Route(key_name=tag)
        route.tag = tag
        route.title = element.getAttribute('title')
        route.short_title = element.getAttribute('shortTitle') # optional
        return route
    route_list_elements = doc.getElementsByTagName('route')
    routes = map(to_route, route_list_elements)
    db.put(routes)

    return routes


def route_config(resource):
    """Create stops, directions, and paths for a route."""

    doc = minidom.parse(resource)

    route_tag = doc.getElementsByTagName('route')[0].getAttribute('tag')
    route_key = db.Key.from_path('Route', route_tag)

    # create stops
    stops = []
    def to_route_stop(element):
        tag = element.getAttribute('tag')
        stop = model.Stop.get_by_key_name(tag)
        if not stop:
            stop = model.Stop(key_name=tag)
            stop.location = element_to_point(element)
            stop.title = element.getAttribute('title')
            stop.short_title = element.getAttribute('shortTitle') # optional
            stop.stop_id = element.getAttribute('stopId')
            stop.update_location()
            stops.append(stop)

        route_stop = model.RouteDirectionStop()
        route_stop.stop = db.Key.from_path('Stop', tag)
        route_stop.direction = db.Key.from_path('RouteDirection', element.getAttribute('dirTag'))
        return route_stop
    route_stop_elements = doc.getElementsByTagName('stop')
    route_stops = map(to_route_stop, (element for element in route_stop_elements if element.getAttribute('lat')))
    if stops:
        db.put(stops)

    # create route directions
    route_stops_by_tag = dict((route_stop.stop.key().name(), route_stop) for route_stop in route_stops)
    directions = []
    def to_direction(element):
        tag = element.getAttribute('tag')
        direction = model.RouteDirection(key_name=tag)
        direction.route = route_key
        direction.title = element.getAttribute('title')
        direction.use_for_ui = element.getAttribute('useForUI') == 'true'

        stop_elements = element.getElementsByTagName('stop')
        for index, stop_element in enumerate(stop_elements):
            tag = stop_element.getAttribute('tag')
            route_stops_by_tag[tag].index = index

        return direction
    direction_elements = doc.getElementsByTagName('direction')
    directions = map(to_direction, direction_elements)
    db.put(directions)
    db.put(route_stops)

    return stops, directions, route_stops


def delete_all():
    db.delete(model.Route.all())
    db.delete(model.Stop.all())
    db.delete(model.RouteDirection.all())
    db.delete(model.RoutePath.all())


def load():
    routes = route_list(file(os.path.join('xml', 'route_list.xml')))
    for route in routes:
        path = os.path.join('xml', 'route_config_%s.xml' % route.tag)
        log.info('loading %s', path)
        route_config(file(path))
