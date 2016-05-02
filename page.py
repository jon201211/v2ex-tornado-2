#!/usr/bin/env python
# coding=utf-8

import os
import datetime
import random

import tornado.web


from v2ex.babel.handlers import BaseHandler
from v2ex.babel.memcached import mc as memcache
import urlfetch


import tornado.ioloop
from jinja2 import Template, Environment, FileSystemLoader

from v2ex.babel import *
from v2ex.babel import Counter
from v2ex.babel import Section
from v2ex.babel import Node
from v2ex.babel import Topic
from v2ex.babel import Reply
from v2ex.babel import Site
from v2ex.babel import Note

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies

#template.register_template_library('v2ex.templatetags.filters')

class AboutHandler(BaseHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        note = GetKindByNum('Note', 127)
        if note is False:
            note = GetKindByNum('Note', 2)
        template_values['note'] = note
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › About'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
        t=self.get_template(path, 'about.html')
        self.finish(t.render(template_values))

class FAQHandler(BaseHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        note = GetKindByNum('Note', 195)
        if note is False:
            note = GetKindByNum('Note', 4)
        template_values['note'] = note
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › FAQ'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
        t=self.get_template(path,'faq.html')
        self.finish(t.render(template_values))

class MissionHandler(BaseHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        note = GetKindByNum('Note', 240)
        if note is False:
            note = GetKindByNum('Note', 5)
        template_values['note'] = note
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › Mission'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
        t=self.get_template(path,'mission.html')
        self.finish(t.render(template_values))

class AdvertiseHandler(BaseHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › Advertise'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
        t=self.get_template(path,'advertise.html')
        self.finish(t.render(template_values))

class AdvertisersHandler(BaseHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        template_values['page_title'] = site.title + u' › Advertisers'
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
        t=self.get_template(path,'advertisers.html')
        self.finish(t.render(template_values))

