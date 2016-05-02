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


import requests
from redis import Redis
from rq import Queue


q = Queue(connection=Redis())

def post_url(url):
    """Just an example function that's called async."""

    resp = requests.get('http://localhost:8888' + url)
    return len(resp.text.split())


def add(*args, **kwargs):
    q.enqueue(post_url, kwargs['url'])
