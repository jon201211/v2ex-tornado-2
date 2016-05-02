#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
import datetime
import hashlib
import string
import random

import tornado.web

from v2ex.babel.memcached import mc as memcache
import urlfetch


import tornado.ioloop
from jinja2 import Template, Environment, FileSystemLoader

from v2ex.babel import Member
from v2ex.babel import Counter
from v2ex.babel import Section
from v2ex.babel import Node
from v2ex.babel import Topic
from v2ex.babel import Reply
from v2ex.babel import Note
from v2ex.babel import Place
from v2ex.babel import PlaceMessage
from v2ex.babel import Site

from v2ex.babel import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies


from v2ex.babel.handlers import BaseHandler
from v2ex.babel import *

#template.register_template_library('v2ex.templatetags.filters')

class PlaceHandler(BaseHandler):
    def get(self, ip):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        member = CheckAuth(self)
        if member:
            template_values['member'] = member
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        template_values['ip'] = ip
        template_values['xsrf'] = self.xsrf_form_html()
        substance = GetPlaceByIP(ip)
        if substance:
            template_values['substance'] = substance
            #template_values['messages'] = db.GqlQuery("SELECT * FROM PlaceMessage WHERE place = :1 ORDER BY created DESC LIMIT 30", substance)
            template_values['messages'] = PlaceMessage.select(PlaceMessage.q.place == substance).orderBy('-created').limit(30)
        else:
            if member:
                if member.ip == ip:
                    substance = CreatePlaceByIP(ip)
                    template_values['substance'] = substance
        can_post = False
        can_see = True
        if member:
            if member.ip == ip:
                can_post = True
                can_see = True
            else:
                can_see = False
        else:
            if 'X-Real-IP' in self.request.headers:
                ip_guest = self.request.headers['X-Real-IP']
            else:
                ip_guest = self.request.remote_addr
            if ip_guest == ip:
                can_see = True
            else:
                can_see = False
        template_values['can_post'] = can_post
        template_values['can_see'] = can_see
        if member:
            template_values['ip_guest'] = member.ip
        else:
            template_values['ip_guest'] = ip_guest
        template_values['page_title'] = site.title + u' › ' + ip
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
        t=self.get_template(path,'place.html')
        self.finish(t.render(template_values))
    
    def post(self, ip):
        site = GetSite()
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/place'
        member = CheckAuth(self)
        place = GetPlaceByIP(ip)
        say = self.request.arguments['say'][0].strip()
        if len(say) > 0 and len(say) < 280 and member and place:
            if member.ip == ip:
                message = PlaceMessage()
                #q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place_message.max')
                q = Counter.selectBy(name='place_message.max')
                if (q.count() == 1):
                    counter = q[0]
                    counter.value = counter.value + 1
                else:
                    counter = Counter()
                    counter.name = 'place_message.max'
                    counter.value = 1
                #q2 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place_message.total')
                q2 = Counter.selectBy(name='place_message.total')
                if (q2.count() == 1):
                    counter2 = q2[0]
                    counter2.value = counter2.value + 1
                else:
                    counter2 = Counter()
                    counter2.name = 'place_message.total'
                    counter2.value = 1
                message.num = counter.value
                message.place = place
                message.place_num = place.num
                message.member = member
                message.content = say
                message.sync()
                counter.sync()
                counter2.sync()
                store.commit()  #jon add
        self.redirect(go)

class PlaceMessageRemoveHandler(BaseHandler):
    def get(self, key):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/place'
        member = CheckAuth(self)
        if member:
            message = PlaceMessage.get(key)
            if message:
                if message.member.num == member.num:
                    message.delete()
                    #q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'place_message.total')
                    q = Counter.selectBy(name='place_message.total')
                    if (q.count() == 1):
                        counter = q[0]
                        counter.value = counter.value - 1
                        counter.sync()
                        store.commit()  #jon add
        self.redirect(go)


