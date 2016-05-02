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

from v2ex.babel import Member, NodeBookmark, TopicBookmark, MemberBookmark
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
from v2ex.babel.ext.sessions import Session

#template.register_template_library('v2ex.templatetags.filters')

class MyNodesHandler(BaseHandler):
    def get(self):
        member = CheckAuth(self)
        if member:
            site = GetSite()
            l10n = GetMessages(self, member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我收藏的节点'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_nodes > 0:
                template_values['has_nodes'] = True
                #q = db.GqlQuery("SELECT * FROM NodeBookmark WHERE member = :1 ORDER BY created DESC LIMIT 0,15", member)
                #q = NodeBookmark.selectBy(member=member).orderBy('-created')[0:15]
                q = NodeBookmark.select(NodeBookmark.q.member==member,orderBy='-created').offset(0).limit(15)
                template_values['column_1'] = q
                if member.favorited_nodes > 15:
                    #q2 = db.GqlQuery("SELECT * FROM NodeBookmark WHERE member = :1 ORDER BY created DESC LIMIT 15,15", member)
                    #q2 = NodeBookmark.selectBy(member=member).orderBy('-created')[15,15]
                    q2 = NodeBookmark.select(NodeBookmark.q.member==member,orderBy='-created').offset(15).limit(15)
                    template_values['column_2'] = q2
            else:
                template_values['has_nodes'] = False
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
            t=self.get_template(path,'my_nodes.html')
            self.finish(t.render(template_values))
        else:
            self.redirect('/')

class MyTopicsHandler(BaseHandler):
    def get(self):
        member = CheckAuth(self)
        if member:
            site = GetSite()
            l10n = GetMessages(self, member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我收藏的主题'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_topics > 0:
                template_values['has_topics'] = True
                #q = db.GqlQuery("SELECT * FROM TopicBookmark WHERE member = :1 ORDER BY created DESC", member)
                q = TopicBookmark.selectBy(member=member).orderBy('-created')
                bookmarks = []
                for bookmark in q:
                    try:
                        topic = bookmark.topic
                        bookmarks.append(bookmark)
                    except:
                        bookmark.delete()
                template_values['bookmarks'] = bookmarks
            else:
                template_values['has_topics'] = False
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
            t=self.get_template(path,'my_topics.html')
            self.finish(t.render(template_values))
        else:
            self.redirect('/')
            
class MyFollowingHandler(BaseHandler):
    def get(self):
        member = CheckAuth(self)
        if member:
            site = GetSite()
            l10n = GetMessages(self, member, site)
            template_values = {}
            template_values['site'] = site
            template_values['member'] = member
            template_values['l10n'] = l10n
            template_values['page_title'] = site.title + u' › 我的特别关注'
            template_values['rnd'] = random.randrange(1, 100)
            if member.favorited_members > 0:
                template_values['has_following'] = True
                #q = db.GqlQuery("SELECT * FROM MemberBookmark WHERE member_num = :1 ORDER BY created DESC", member.num)
                q = MemberBookmark.selectBy(member_num=member.num).orderBy('-created')
                template_values['following'] = q
                following = []
                for bookmark in q:
                    following.append(bookmark.one.num)
                #q2 = db.GqlQuery("SELECT * FROM Topic WHERE member_num IN :1 ORDER BY created DESC LIMIT 20", following)
                q2 = Topic.selectBy(member_num=following).orderBy('-created').limit(20)
                template_values['latest'] = q2
            else:
                template_values['has_following'] = False
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
            t=self.get_template(path,'my_following.html')
            self.finish(t.render(template_values))
        else:
            self.redirect('/')
