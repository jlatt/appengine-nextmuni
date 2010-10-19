import logging
import urllib
from xml.dom import minidom

from google.appengine.ext import db

import model


__author__ = 'Jeremy Latt <jeremy.latt@gmail.com>'
route_list_url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=sf-muni'
log = logging.getLogger('nextmuni.nextbus')


def route_config_url(route_tag):
    return 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=sf-muni&r=' + route_tag


def element_to_point(element):
    return db.GeoPt(float(element.getAttribute('lat')), float(element.getAttribute('lon')))


def route_list():
    """Create routes."""
    resource = urllib.urlopen(route_list_url)
    doc = minidom.parse(resource)

    def to_route(element):
        route = model.Route()
        route.tag = element.getAttribute('tag')
        route.title = element.getAttribute('title')
        route.short_title = element.getAttribute('shortTitle') # optional
        return route
    route_list_elements = doc.getElementsByTagName('route')
    routes = map(to_route, route_list_elements)
    db.put(routes)

    return routes


def route_config(route_tag):
    """Create stops, directions, and paths for a route."""
    resource = urllib.urlopen(route_config_url(route_tag))
    doc = minidom.parse(resource)

    # create stops
    def to_stop(element):
        stop = model.Stop()
        stop.location = element_to_point(element)
        stop.tag = element.getAttribute('tag')
        stop.title = element.getAttribute('title')
        stop.short_title = element.getAttribute('shortTitle') # optional
        stop.stop_id = element.getAttribute('stopId')
        stop.update_location()
        return stop
    route_stop_elements = doc.getElementsByTagName('stop')
    stops = map(to_stop, (element for element in route_stop_elements if element.getAttribute('lat')))
    db.put(stops)

    # create route directions
    stops_by_tag = dict((stop.tag, stop) for stop in stops)
    def to_direction(element):
        direction = model.RouteDirection()
        direction.tag = element.getAttribute('tag')
        direction.title = element.getAttribute('title')
        direction.use_for_ui = element.getAttribute('useForUI') == 'true'
        stop_elements = element.getElementsByTagName('stop')
        direction.stops = [stops_by_tag[stop_element.getAttribute('tag')].key() for stop_element in stop_elements]
        return direction
    direction_elements = doc.getElementsByTagName('direction')
    directions = map(to_direction, direction_elements)
    db.put(directions)

    # create paths
    def to_path(element):
        path = model.RoutePath()
        point_elements = element.getElementsByTagName('point')
        path.points = [element_to_point(point_element) for point_element in point_elements]
        return path
    path_elements = doc.getElementsByTagName('path')
    paths = map(to_path, path_elements)
    db.put(paths)

    # connect directions and paths
    directions_by_tag = dict((direction.tag, direction) for direction in directions)
    for path, element in zip(paths, path_elements):
        tag_elements = element.getElementsByTagName('tag')
        for tag_element in tag_elements:
            tag = tag_element.getAttribute('id')
            if tag in directions_by_tag:
                directions_by_tag[tag].path = path
            else:
                log.warning('tag %(tag)s not found', locals())
    db.put(directions)

    return stops, directions, paths


def load_all():
    routes = route_list()
    for route in routes:
        route_config(route.tag)


def load_some():
    routes = route_list()
    for route_tag in ('33', '1', '2'):
        route_config(route_tag)


def delete_all():
    db.delete(model.Route.all())
    db.delete(model.Stop.all())
    db.delete(model.RouteDirection.all())
    db.delete(model.RoutePath.all())
