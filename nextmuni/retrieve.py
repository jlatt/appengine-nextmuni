#!/usr/bin/env python
from __future__ import with_statement
import sys
import time
import urllib
from xml.dom import minidom


route_list_url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=sf-muni'


def route_config_url(route_tag):
    return 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=sf-muni&r=' + urllib.quote_plus(route_tag)


if __name__ == '__main__':
    with file('route_list.xml', 'w') as outfile:
        infile = urllib.urlopen(route_list_url)
        print route_list_url
        infile_data = infile.read()
        outfile.write(infile_data)

    doc = minidom.parseString(infile_data)
    for route_element in doc.getElementsByTagName('route'):
        route_tag = route_element.getAttribute('tag')
        time.sleep(1) # throttle
        with file('route_config_%s.xml' % route_tag, 'w') as outfile:
            url = route_config_url(route_tag)
            print url
            infile = urllib.urlopen(url)
            outfile.write(infile.read())
