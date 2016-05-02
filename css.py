#!/usr/bin/env python
# coding=utf-8

import os
import datetime

from v2ex.babel.memcached import mc as memcache
from jinja2 import Template, Environment, FileSystemLoader

from v2ex.babel.handlers import BaseHandler
from v2ex.babel import *
from v2ex.babel import SYSTEM_VERSION

import tornado.web
import pytz
#template.register_template_library('v2ex.templatetags.filters')



class CSSHandler(tornado.web.RequestHandler):
    def get(self,theme):
        template_values = {}
        themes = os.listdir(os.path.join(os.path.dirname(__file__),'tpl', 'themes'))
        if theme in themes:
            path = os.path.join(theme, 'style.css')
        else:
            path = os.path.join('default', 'style.css')
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),"tpl/themes")))
        template = env.get_template(path)
        output = template.render(template_values)
        expires_date = datetime.datetime.now(pytz.timezone('Asia/Shanghai')) + datetime.timedelta(days=7)
        expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
        self.add_header("Expires", expires_str)
        self.set_header('Cache-Control', 'max-age=120, must-revalidate')
        self.set_header('Content-type','text/css;charset=UTF-8')
        self.write(output)
