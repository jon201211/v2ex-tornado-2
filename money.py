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
from v2ex.babel import Notification

from v2ex.babel import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies

from v2ex.babel.handlers import BaseHandler

import config



class MoneyDashboardHandler(BaseHandler):
    def get(self):
        if self.member:
            self.set_title(u'账户查询')
            self.finalize(template_name='money_dashboard')
        else:
            self.redirect('/signin')


