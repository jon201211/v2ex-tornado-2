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

import  taskqueue

import tornado.ioloop
from jinja2 import Template, Environment, FileSystemLoader

from v2ex.babel import Member
from v2ex.babel import Counter
from v2ex.babel import Section
from v2ex.babel import Node
from v2ex.babel import Topic
from v2ex.babel import Reply
from v2ex.babel import Note
from v2ex.babel import NodeBookmark
from v2ex.babel import TopicBookmark
from v2ex.babel import MemberBookmark

from v2ex.babel import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *

from v2ex.babel.ext.cookies import Cookies
from v2ex.babel.ext.sessions import Session
from v2ex.babel.handlers import BaseHandler
from v2ex.babel import *


class FavoriteNodeHandler(BaseHandler):
    def get(self, node_name):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.argument['t'][0]
        if member:
            if str(member.created_ts) == str(t):
                node = GetKindByName('Node', node_name)
                if node is not False:
                    #q = db.GqlQuery("SELECT * FROM NodeBookmark WHERE node = :1 AND member = :2", node, member)
                    q = NodeBookmark.selectBy(node=node, member=member)
                    if q.count() == 0:
                        bookmark = NodeBookmark(member=member)
                        bookmark.node = node
                        bookmark.member = member
                        bookmark.sync()
                        member = Member.get(member.id)
                        member.favorited_nodes = member.favorited_nodes + 1
                        member.sync()
                        store.commit()  #jon add
                        memcache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/n' + str(node.num) + '/m' + str(member.num)
                        memcache.set(n, True, 86400 * 14)
        self.redirect(go)
    
class UnfavoriteNodeHandler(BaseHandler):
    def get(self, node_name):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.argument['t'][0]
        if member:
            if str(member.created_ts) == str(t):
                node = GetKindByName('Node', node_name)
                if node is not False:
                    #q = db.GqlQuery("SELECT * FROM NodeBookmark WHERE node = :1 AND member = :2", node, member)
                    q = NodeBookmark.selectBy(node=node,member=member)
                    if q.count() > 0:
                        bookmark = q[0]
                        bookmark.delete()
                        member = Member.get(member.id)
                        member.favorited_nodes = member.favorited_nodes - 1
                        member.sync()
                        store.commit()  #jon add
                        memcache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/n' + str(node.num) + '/m' + str(member.num)
                        memcache.delete(n)
        self.redirect(go)

class FavoriteTopicHandler(BaseHandler):
    def get(self, topic_num):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.argument['t'][0].strip()
        if member:
            if member.username_lower_md5 == t:
                topic = GetKindByNum('Topic', int(topic_num))
                if topic is not False:
                    #q = db.GqlQuery("SELECT * FROM TopicBookmark WHERE topic = :1 AND member = :2", topic, member)
                    q = TopicBookmark.selectBy(topic=topic,member=member)
                    if q.count() == 0:
                        bookmark = TopicBookmark(member=member)
                        bookmark.topic = topic
                        bookmark.member = member
                        bookmark.sync()
                        member = Member.get(member.id)
                        member.favorited_topics = member.favorited_topics + 1
                        member.sync()
                        store.commit()  #jon add
                        memcache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/t' + str(topic.num) + '/m' + str(member.num)
                        memcache.set(n, True, 86400 * 14)
                        #taskqueue.add(url='/add/star/topic/' + str(topic.id))
                        topic.stars = topic.stars + 1
                        topic.sync()
                        store.commit()  #jon add
                        memcache.set('Topic_' + str(topic.num), topic, 86400)
        self.redirect(go)

class UnfavoriteTopicHandler(BaseHandler):
    def get(self, topic_num):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.argument['t'][0].strip()
        if member:
            if member.username_lower_md5 == t:
                topic = GetKindByNum('Topic', int(topic_num))
                if topic is not False:
                    #q = db.GqlQuery("SELECT * FROM TopicBookmark WHERE topic = :1 AND member = :2", topic, member)
                    q = TopicBookmark.selectBy(topic=topic,member=member)
                    if q.count() > 0:
                        bookmark = q[0]
                        bookmark.delete()
                        member = Member.get(member.id)
                        member.favorited_topics = member.favorited_topics - 1
                        member.sync()
                        store.commit()  #jon add
                        memcache.set('Member_' + str(member.num), member, 86400)
                        n = 'r/t' + str(topic.num) + '/m' + str(member.num)
                        memcache.delete(n)
                        #taskqueue.add(url='/minus/star/topic/' + str(topic.id))
                        topic.stars = topic.stars - 1
                        topic.sync()
                        store.commit()  #jon add
                        memcache.set('Topic_' + str(topic.num), topic, 86400)
        self.redirect(go)
        
class FollowMemberHandler(BaseHandler):
    def get(self, one_num):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.argument['t'][0]
        if member:
            if str(member.created_ts) == str(t):
                one = GetKindByNum('Member', int(one_num))
                if one is not False:
                    if one.num != member.num:
                        #q = db.GqlQuery("SELECT * FROM MemberBookmark WHERE one = :1 AND member_num = :2", one, member.num)
                        q = MemberBookmark.selectBy(one=one, member_num=member.num)
                        if q.count() == 0:
                            member = Member.get(member.id)
                            member.favorited_members = member.favorited_members + 1
                            if member.favorited_members > 30:
                                self.session = Session()
                                self.session['message'] = '最多只能添加 30 位特别关注'
                            else:
                                bookmark = MemberBookmark(member=member)
                                bookmark.one = one
                                bookmark.member_num = member.num
                                bookmark.sync()
                                member.sync()
                                memcache.set('Member_' + str(member.num), member, 86400)
                                n = 'r/m' + str(one.num) + '/m' + str(member.num)
                                memcache.set(n, True, 86400 * 14)
                                one = Member.get(one.id)
                                one.followers_count = one.followers_count + 1
                                one.sync()
                                store.commit()  #jon add
                                memcache.set('Member_' + str(one.num), one, 86400)
                                memcache.set('Member::' + str(one.username_lower), one, 86400)
                                self.session = Session()
                                self.session['message'] = '特别关注添加成功，还可以添加 ' + str(30 - member.favorited_members) + ' 位'
        self.redirect(go)

class UnfollowMemberHandler(BaseHandler):
    def get(self, one_num):
        if 'Referer' in self.request.headers:
            go = self.request.headers['Referer']
        else:
            go = '/'
        member = CheckAuth(self)
        t = self.request.argument['t'][0]
        if member:
            if str(member.created_ts) == str(t):
                one = GetKindByNum('Member', int(one_num))
                if one is not False:
                    if one.num != member.num:
                        #q = db.GqlQuery("SELECT * FROM MemberBookmark WHERE one = :1 AND member_num = :2", one, member.num)
                        q = MemberBookmark.selectBy(one=one, member_num=member.num)
                        if q.count() > 0:
                            bookmark = q[0]
                            bookmark.delete()
                            member = Member.get(member.id)
                            member.favorited_members = member.favorited_members - 1
                            member.sync()
                            memcache.set('Member_' + str(member.num), member, 86400)
                            n = 'r/m' + str(one.num) + '/m' + str(member.num)
                            memcache.delete(n)
                            one = Member.get(one.id)
                            one.followers_count = one.followers_count - 1
                            one.sync()
                            store.commit()  #jon add
                            memcache.set('Member_' + str(one.num), one, 86400)
                            memcache.set('Member::' + str(one.username_lower), one, 86400)
        self.redirect(go)

