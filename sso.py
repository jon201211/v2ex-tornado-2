#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
import datetime
import hashlib
import string
import random

import config

import tornado.web

from v2ex.babel.handlers import BaseHandler
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

from v2ex.babel import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies

#template.register_template_library('v2ex.templatetags.filters')

class SSOV0Handler(BaseHandler):
    def get(self):
        site = GetSite()
        self.set_header('Content-type', 'application/json')
        u = self.request.arguments['u'][0].strip().lower()
        p = self.request.arguments['p'][0].strip()
        failed = '{"ok" : 0}'
        if (len(u) > 0) and (len(p) > 0):
            #q = db.GqlQuery("SELECT * FROM Member WHERE username_lower = :1 AND password = :2", u, p)
            q = Member.selectBy(username_lower=u, password=p)
            if q.count() > 0:
                member = q[0]
                if member.avatar_mini_url:
                    if (member.avatar_mini_url[0:1] == '/'):
                        member.avatar_mini_url = 'http://' + site.domain + member.avatar_mini_url
                        member.avatar_normal_url = 'http://' +  site.domain + member.avatar_normal_url
                        member.avatar_large_url = 'http://' + site.domain + member.avatar_large_url
                else:
                    member.avatar_mini_url = 'http://' + site.domain + '/static/img/avatar_mini.png'
                    member.avatar_normal_url = 'http://' + site.domain + '/static/img/avatar_normal.png'
                    member.avatar_large_url = 'http://' + site.domain + '/static/img/avatar_large.png'
                self.write('{"ok" : 1, "num" : ' + str(member.num) + ', "username" : "' + member.username + '", "username_lower" : "' + member.username_lower + '", "email" : "' + member.email + '", "avatar_mini_url" : "' + member.avatar_mini_url + '", "avatar_normal_url" : "' + member.avatar_normal_url + '", "avatar_large_url" : "' + member.avatar_large_url + '", "created" : ' + str(time.mktime(member.created.timetuple())) + ', "last_modified" : ' + str(time.mktime(member.last_modified.timetuple())) + '}')
            else:
                self.write(failed)
        else:
            self.write(failed)

class SSOX0Handler(BaseHandler):
    def get(self):
        site = GetSite()
        self.set_header('Content-type', 'application/json')
        x = self.request.arguments['x'][0].strip()
        n = self.request.arguments['n'][0].strip().lower()
        failed = '{"ok" : 0}'
        if x == config.ssox:
            #q = db.GqlQuery("SELECT * FROM Member WHERE username_lower = :1", n)
            q = Member.selectBy(username_lower=n)
            if q.count() > 0:
                member = q[0]
                if member.avatar_mini_url:
                    if (member.avatar_mini_url[0:1] == '/'):
                        member.avatar_mini_url = 'http://' + site.domain + member.avatar_mini_url
                        member.avatar_normal_url = 'http://' +  site.domain + member.avatar_normal_url
                        member.avatar_large_url = 'http://' + site.domain + member.avatar_large_url
                else:
                    member.avatar_mini_url = 'http://' + site.domain + '/static/img/avatar_mini.png'
                    member.avatar_normal_url = 'http://' + site.domain + '/static/img/avatar_normal.png'
                    member.avatar_large_url = 'http://' + site.domain + '/static/img/avatar_large.png'
                self.write('{"ok" : 1, "num" : ' + str(member.num) + ', "username" : "' + member.username + '", "username_lower" : "' + member.username_lower + '", "email" : "' + member.email + '", "password" : "' + member.password + '", "avatar_mini_url" : "' + member.avatar_mini_url + '", "avatar_normal_url" : "' + member.avatar_normal_url + '", "avatar_large_url" : "' + member.avatar_large_url + '", "created" : ' + str(time.mktime(member.created.timetuple())) + ', "last_modified" : ' + str(time.mktime(member.last_modified.timetuple())) + '}')
            else:
                self.write(failed)
        else:
            self.write(failed)
            
