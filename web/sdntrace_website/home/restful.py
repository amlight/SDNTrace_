import requests
from flask import Blueprint, render_template,  redirect, url_for
from flask import Response
import configparser
import logging
logger = logging.getLogger('web.sdntrace_website.home.restful')

# Read config parameters
_configParser = configparser.RawConfigParser()
_configParser.read_file(open(r'sdntrace_website/conf/web.conf'))
REST_HOST = _configParser.get('web-rest', 'REST_HOST')
logger.debug('REST_HOST: %s' % REST_HOST)

REST_PORT = _configParser.get('web-rest', 'REST_PORT')
logger.debug('REST_PORT: %s' % REST_PORT)

# Flask blueprint
restful_blueprint = Blueprint(name='restful', import_name=__name__)

#
# Proxy class to call SDN-LG core restful
#

@restful_blueprint.route('/switches')
def switches():
    url = 'http://%s:%s/switches' % (REST_HOST, REST_PORT)
    response = requests.get(url)
    return Response(response=response.text, status=response.status_code, mimetype="application/json")

@restful_blueprint.route('/links')
def links():
    url = 'http://%s:%s/links' % (REST_HOST, REST_PORT)
    response = requests.get(url)
    return Response(response=response.text, status=response.status_code, mimetype="application/json")

@restful_blueprint.route('/switches/<dpid>/ports')
def ports(dpid):
    url = 'http://%s:%s/switches/%s/ports' % (REST_HOST, REST_PORT, dpid)
    response = requests.get(url)
    return Response(response=response.text, status=response.status_code, mimetype="application/json")

