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

from v2ex.babel.handlers import BaseHandler
from v2ex.babel.memcached import mc as memcache
import urlfetch
#from collective.taskqueue import taskqueue
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

class AddStarTopicHandler(BaseHandler):
    def get(self, topic_key):
        topic = Topic.get(topic_key)
        if topic:
            topic.stars = topic.stars + 1
            topic.sync()
            store.commit()  #jon add
            memcache.set('Topic_' + str(topic.num), topic, 86400)

class MinusStarTopicHandler(BaseHandler):
    def get(self, topic_key):
        topic = Topic.get(topic_key)
        if topic:
            topic.stars = topic.stars - 1
            topic.sync()
            store.commit()  #jon add
            memcache.set('Topic_' + str(topic.num), topic, 86400)


