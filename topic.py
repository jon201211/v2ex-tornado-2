#!/usr/bin/env python
# coding=utf-8

import base64
import os
import re
import time
import datetime
import hashlib
import string
import random
import pickle
import zlib
import math

import tornado.web
from v2ex.babel.memcached import mc as memcache
import urlfetch

import  taskqueue
import tornado.ioloop
from jinja2 import Template, Environment, FileSystemLoader

from v2ex.babel import Member, TopicBookmark
from v2ex.babel import Counter
from v2ex.babel import Section
from v2ex.babel import Node
from v2ex.babel import Topic
from v2ex.babel import Reply
from v2ex.babel import Notification
from v2ex.babel import Page

from v2ex.babel import SYSTEM_VERSION

from v2ex.babel.security import *
from v2ex.babel.ua import *
from v2ex.babel.da import *
from v2ex.babel.l10n import *
from v2ex.babel.ext.cookies import Cookies
from v2ex.babel.ext.sessions import Session


import json
import pytz

from twitter.oauthtwitter import OAuthApi
from twitter.oauth import OAuthToken

from config import twitter_consumer_key as CONSUMER_KEY
from config import twitter_consumer_secret as CONSUMER_SECRET

from v2ex.babel.handlers import BaseHandler

import config

TOPIC_PAGE_SIZE = 100

class NewTopicHandler(BaseHandler):
    def get(self, node_name):
        site = GetSite()
        browser = detect(self.request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        template_values['xsrf'] = self.xsrf_form_html()
        template_values['page_title'] = site.title + u' › ' + l10n.create_new_topic.decode('utf-8')
        can_create = False
        if site.topic_create_level > 999:
            if member:
                can_create = True
        else:
            if member:
                if member.level <= site.topic_create_level:
                    can_create = True
        if (member):
            template_values['member'] = member
            node = GetKindByName('Node', node_name)
            if node is False:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                t=self.get(path,'node_not_found.html')
                return self.finish(t.render(template_values))
            template_values['node'] = node
            section = GetKindByNum('Section', node.section_num)
            template_values['section'] = section
            if site.use_topic_types:
                types = site.topic_types.split("\n")
                options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                i = 0
                for a_type in types:
                    i = i + 1
                    detail = a_type.split(':')
                    options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                tt = '<div class="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                template_values['tt'] = tt
            else:
                template_values['tt'] = ''
            if can_create:
                if browser['ios']:
                    if node:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                        filename = 'new_topic.html'
                    else:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                        filename = 'node_not_found.html'
                else:
                    if node:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                        filename = 'new_topic.html'
                    else:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                        filename = 'node_not_found.html'
            else:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop' )
                filename = 'access_denied.html'
            t=self.get_template(path,filename)
            self.finish(t.render(template_values))
        else:
            self.redirect('/signin')

    def post(self, node_name):
        site = GetSite()
        ### BEGIN: CAN CONTINUE
        can_continue = True
        if ('Host' in self.request.headers):
            if (self.request.headers['Host'] not in ['www.v2ex.com', 'v2ex.appspot.com', 'fast.v2ex.com', 'beta.v2ex.com', 'us.v2ex.com', 'jp.v2ex.com', 'eu.v2ex.com', 'localhost:10000']):
                can_continue = False
        else:
            can_continue = False
        if ('User-Agent' not in self.request.headers):
            can_continue = False
        if ('Cookie' not in self.request.headers):
            can_continue = False
        if ('Referer' in self.request.headers):
            has_v2ex = False
            if ('http://localhost:10000' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://www.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://v2ex.appspot.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('https://www.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://jp.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://eu.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://us.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('https://v2ex.appspot.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://fast.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://beta.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://' + str(site.domain) in self.request.headers['Referer']):
                has_v2ex = True
            if has_v2ex is False:
                can_continue = False
        else:
            can_continue = False
        if ('Content-Type' in self.request.headers):
            if self.request.headers['Content-Type'].startswith( 'application/x-www-form-urlencoded') is False:
                can_continue = False
        else:
            can_continue = False
        if can_continue is False:
            return self.redirect('http://' + site.domain + '/')
        ### END: CAN CONTINUE
        browser = detect(self.request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        template_values['xsrf'] = self.xsrf_form_html()
        template_values['page_title'] = site.title + u' › ' + l10n.create_new_topic.decode('utf-8')
        can_create = False
        if site.topic_create_level > 999:
            if member:
                can_create = True
        else:
            if member:
                if member.level <= site.topic_create_level:
                    can_create = True
        if (member):
            template_values['member'] = member
            if can_create:
                node = False
                node = GetKindByName('Node', node_name)
                template_values['node'] = node
                section = False
                if node:
                    section = GetKindByNum('Section', node.section_num)
                template_values['section'] = section
                errors = 0
                # Verification: title
                topic_title_error = 0
                topic_title_error_messages = ['',
                    u'请输入主题标题',
                    u'主题标题长度不能超过 120 个字符'
                    ]
                topic_title = self.request.arguments['title'][0].strip().replace("\n", " ")
                if (len(topic_title) == 0):
                    errors = errors + 1
                    topic_title_error = 1
                else:
                    if (len(topic_title) > 120):
                        errors = errors + 1
                        topic_title_error = 2
                template_values['topic_title'] = topic_title
                template_values['topic_title_error'] = topic_title_error
                template_values['topic_title_error_message'] = topic_title_error_messages[topic_title_error]
                # Verification: content
                topic_content_error = 0
                topic_content_error_messages = ['',
                    u'主题内容长度不能超过 200000 个字符'
                ]
                topic_content = self.request.arguments['content'][0].strip()
                topic_content_length = len(topic_content)
                if (topic_content_length > 0):
                    if (topic_content_length > 200000):
                        errors = errors + 1
                        topic_content_error = 1
                template_values['topic_content'] = topic_content
                template_values['topic_content_error'] = topic_content_error
                template_values['topic_content_error_message'] = topic_content_error_messages[topic_content_error]
                # Verification: type
                if site.use_topic_types:
                    types = site.topic_types.split("\n")
                    if len(types) > 0:
                        topic_type = self.request.arguments['type'][0].strip()
                        try:
                            topic_type = int(topic_type)
                            if topic_type < 0:
                                topic_type = 0
                            if topic_type > len(types):
                                topic_type = 0
                            if topic_type > 0:
                                detail = types[topic_type - 1].split(':')
                                topic_type_label = detail[0]
                                topic_type_color = detail[1]
                        except:
                            topic_type = 0
                    else:
                        topic_type = 0
                    options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                    i = 0
                    for a_type in types:
                        i = i + 1
                        detail = a_type.split(':')
                        if topic_type == i:
                            options = options + '<option value="' + str(i) + '" selected="selected">' + detail[0] + '</option>'
                        else:
                            options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                    tt = '<div class="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                    template_values['tt'] = tt
                else:
                    template_values['tt'] = ''
                template_values['errors'] = errors
                if (errors == 0):
                    topic = Topic(node=node)
                    #q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'topic.max')
                    q = Counter.selectBy(name='topic.max')
                    if (q.count() == 1):
                        counter = q[0]
                        counter.value = counter.value + 1
                    else:
                        counter = Counter()
                        counter.name = 'topic.max'
                        counter.value = 1
                    #q2 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'topic.total')
                    q2 = Counter.selectBy(name='topic.total')
                    if (q2.count() == 1):
                        counter2 = q2[0]
                        counter2.value = counter2.value + 1
                    else:
                        counter2 = Counter()
                        counter2.name = 'topic.total'
                        counter2.value = 1
                    topic.num = counter.value
                    topic.title = topic_title
                    topic.content = topic_content
                    if len(topic_content) > 0:
                        topic.has_content = True
                        topic.content_length = topic_content_length
                    else:
                        topic.has_content = False
                    path = os.path.join(os.path.dirname(__file__), 'tpl', 'portion')
                    t=self.get_template(path,'topic_content.html')
                    output = t.render({'topic' : topic})
                    topic.content_rendered = output.decode('utf-8')
                    topic.node = node
                    topic.node_num = node.num
                    topic.node_name = node.name
                    topic.node_title = node.title
                    topic.created_by = member.username
                    topic.member = member
                    topic.member_num = member.num
                    time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                    topic.created = time
                    topic.last_modified = time
                    topic.last_touched = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                    ua = self.request.headers['User-Agent']
                    if (re.findall('Mozilla\/5.0 \(iPhone;', ua)):
                        topic.source = 'iPhone'
                    if (re.findall('Mozilla\/5.0 \(iPod;', ua)):
                        topic.source = 'iPod'
                    if (re.findall('Mozilla\/5.0 \(iPad;', ua)):
                        topic.source = 'iPad'
                    if (re.findall('Android', ua)):
                        topic.source = 'Android'
                    if (re.findall('Mozilla\/5.0 \(PLAYSTATION 3;', ua)):
                        topic.source = 'PS3'
                    if site.use_topic_types:
                        if topic_type > 0:
                            topic.type = topic_type_label
                            topic.type_color = topic_type_color          
                    node.topics = node.topics + 1
                    node.sync()
                    topic.sync()
                    counter.sync()
                    counter2.sync()
                    store.commit()  #jon add
                    memcache.delete('feed_index')
                    memcache.delete('Node_' + str(topic.node_num))
                    memcache.delete('Node::' + str(node.name))
                    memcache.delete('q_latest_16')
                    memcache.delete('home_rendered')
                    memcache.delete('home_rendered_mobile')
                    try:
                        taskqueue.add(url='/index/topic/' + str(topic.num))
                    except:
                        pass
                    
                    # Twitter Sync
                    if member.twitter_oauth == 1 and member.twitter_sync == 1:
                        access_token = OAuthToken.from_string(member.twitter_oauth_string)
                        twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                        status = topic.title + ' #' + topic.node.name + ' http://' + self.request.headers['Host'] + '/t/' + str(topic.num)
                        try:
                            twitter.PostUpdate(status.encode('utf-8'))
                        except:
                            logging.error("Failed to sync to Twitter for Topic #" + str(topic.num))
                    # Change newbie status?
                    if member.newbie == 1:
                        now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                        created = member.created
                        diff = now - created
                        if diff.seconds > (86400 * 60):
                            member.newbie = 0
                            member.sync()
                            store.commit()  #jon add
                    
                    # Notifications: mention_topic
                    taskqueue.add(url='/notifications/topic/' + str(topic.id))
                    
                    self.redirect('/t/' + str(topic.num) + '#reply0')
                else:    
                    if browser['ios']:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                    else:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                    t=self.get_template(path,'new_topic.html')
                    self.finish(t.render(template_values))
            else:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                t=self.get_template(path,'access_denied.html')
                self.finish(t.render(template_values))
        else:
            self.redirect('/signin')

class TopicHandler(BaseHandler):
    def get(self, topic_num):
        site = GetSite()
        browser = detect(self.request)
        template_values = {}
        template_values['site'] = site
        template_values['rnd'] = random.randrange(1, 100)
        try:
            reply_reversed = self.request.arguments['r'][0]
        except:
            reply_reversed = '0'

        if reply_reversed == '1':
            reply_reversed = True
        else:
            reply_reversed = False
        try:
            filter_mode = self.request.arguments['f'][0]
        except:
            filter_mode = '0'

        if filter_mode == '1':
            filter_mode = True
        else:
            filter_mode = False
        template_values['reply_reversed'] = reply_reversed
        template_values['filter_mode'] = filter_mode
        template_values['system_version'] = SYSTEM_VERSION
        errors = 0
        template_values['errors'] = errors
        member = CheckAuth(self)
        template_values['member'] = member
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        template_values['xsrf'] = self.xsrf_form_html()
        if member is not False:
            try:
                blocked = pickle.loads(member.blocked.encode('utf-8'))
            except:
                blocked = []
            if (len(blocked) > 0):
                template_values['blocked'] = ','.join(map(str, blocked))
            if member.level == 0:
                template_values['is_admin'] = 1
            else:
                template_values['is_admin'] = 0
        topic_num_str = str(topic_num)
        if len(topic_num_str) > 8:
            if browser['ios']:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
            else:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
            t=self.get_template(path,'topic_not_found.html')
            self.finish(t.render(template_values))
            return
        topic = False
        topic = memcache.get('Topic_' + str(topic_num))
        if topic is None:
            #q = db.GqlQuery("SELECT * FROM Topic WHERE num = :1", int(topic_num))
            q = Topic.selectBy(num=int(topic_num))
            if (q.count() == 1):
                topic = q[0]
                memcache.set('Topic_' + str(topic_num), topic, 86400)
        can_edit = False
        can_move = False
        if topic:
            if topic.content:
                template_values['page_description'] = topic.content[:60] + ' - ' + topic.member.username
            else:
                template_values['page_description'] = topic.title[:60] + ' - ' + topic.member.username
            template_values['page_description'] = template_values['page_description'].replace("\r\n", " ")
            if member:
                if member.level == 0:
                    can_edit = True
                    can_move = True
                if topic.member_num == member.num:
                    now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                    if (now - topic.created).seconds < 300:
                        can_edit = True
                        can_move = True
            try:
                #taskqueue.add(url='/hit/topic/' + str(topic.id))
                topic.hits = topic.hits + 1
                topic.sync()
                store.commit()  #jon add
            except:
                pass
            template_values['page_title'] = site.title + u' › ' + topic.title
            template_values['canonical'] = 'http://' + site.domain + '/t/' + str(topic.num)
            if topic.content_rendered is None:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'portion')
                t=self.get_template(path,'topic_content.html')
                output = t.render({'topic' : topic})
                topic = Topic.get()
                topic.content_rendered = output.decode('utf-8')
                memcache.delete('Topic_' + str(topic.num))
                topic.sync()
                store.commit()  #jon add
        else:
            template_values['page_title'] = site.title + u' › 主题未找到'
        template_values['topic'] = topic
        template_values['can_edit'] = can_edit
        template_values['can_move'] = can_move
        if (topic):
            node = False
            section = False
            node = GetKindByNum('Node', topic.node_num)
            if (node):
                section = GetKindByNum('Section', node.section_num)
            template_values['node'] = node
            template_values['section'] = section
            
            page_size = TOPIC_PAGE_SIZE
            pages = 1
            if topic.replies > page_size:
                if (topic.replies % page_size) > 0:
                    pages = int(math.floor(topic.replies / page_size)) + 1
                else:
                    pages = int(math.floor(topic.replies / page_size))
            try:
                page_current = int(self.request.arguments['p'][0])
                if page_current < 1:
                    page_current = 1
                if page_current > pages:
                    page_current = pages
            except:
                page_current = pages
            page_start = (page_current - 1) * page_size
            template_values['pages'] = pages
            template_values['page_current'] = page_current
            
            template_values['ps'] = False
            i = 1
            ps = []
            while i <= pages:
                ps.append(i)
                i = i + 1
            if len(ps) > 1:
                template_values['ps'] = ps
            replies = False
            if browser['ios']:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'portion')
                filename = 'topic_replies_mobile.html'
            else:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'portion')
                filename = 'topic_replies.html'
            if filter_mode:
                if browser['ios']:
                    r_tag = 'topic_' + str(topic.num) + '_replies_filtered_rendered_ios_' + str(page_current)
                else:
                    r_tag = 'topic_' + str(topic.num) + '_replies_filtered_rendered_desktop_' + str(page_current)
                r = memcache.get(r_tag)
                if r is None:
                    replies = memcache.get('topic_' + str(topic.num) + '_replies_filtered_compressed_' + str(page_current))
                    if replies is None:
                        #q5 = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1 AND member_num = :2 ORDER BY created ASC LIMIT " + str(page_start) + "," + str(page_size), topic.num, topic.member.num)
                        q5 = Reply.selectBy(topic_num=topic.num, member_num=member.num).orderBy('created')[page_start:page_size]
                        replies = q5
                        memcache.set('topic_' + str(topic.num) + '_replies_filtered_compressed_' + str(page_current), GetPacked(replies), 7200)
                    else:
                        replies = GetUnpacked(replies)
                    template_values['replies'] = replies
                    template_values['replies_count'] = replies.count()
                    t=self.get_template(path,filename)
                    r = t.render(template_values)
                    memcache.set(r_tag, r, 86400)
            else:    
                if reply_reversed:
                    if browser['ios']:
                        r_tag = 'topic_' + str(topic.num) + '_replies_desc_rendered_ios_' + str(page_current)
                    else:
                        r_tag = 'topic_' + str(topic.num) + '_replies_desc_rendered_desktop_' + str(page_current)
                    r = memcache.get(r_tag)
                    if r is None:
                        replies = memcache.get('topic_' + str(topic.num) + '_replies_desc_compressed_' + str(page_current))
                        if replies is None:
                            #q4 = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1 ORDER BY created DESC LIMIT " + str(page_start) + "," + str(page_size), topic.num)
                            #q4 = Reply.selectBy(topic_num=topic.num).orderBy('-created')[page_start:page_size]
                            q4 = Reply.select(Reply.q.topic_num==topic.num,orderBy='-created').offset(page_start).limit(page_size)
                            replies = q4
                            memcache.set('topic_' + str(topic.num) + '_replies_desc_compressed_' + str(page_current), GetPacked(q4), 86400)
                        else:
                            replies = GetUnpacked(replies)
                        template_values['replies'] = replies
                        template_values['replies_count'] = replies.count()
                        t=self.get_template(path,filename)
                        r = t.render(template_values)
                        memcache.set(r_tag, r, 86400)
                else:
                    if browser['ios']:
                        r_tag = 'topic_' + str(topic.num) + '_replies_asc_rendered_ios_' + str(page_current)
                    else:
                        r_tag = 'topic_' + str(topic.num) + '_replies_asc_rendered_desktop_' + str(page_current)
                    r = memcache.get(r_tag)
                    if r is None:
                        replies = memcache.get('topic_' + str(topic.num) + '_replies_asc_compressed_' + str(page_current))
                        if replies is None:
                            #q4 = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1 ORDER BY created ASC LIMIT " + str(page_start) + "," + str(page_size), topic.num)
                            #q4 = Reply.selectBy(topic_num=topic.num).orderBy('created')[page_start:page_size]
                            q4 = Reply.select(Reply.q.topic_num == topic.num,orderBy='created').offset(page_start).limit(page_size)
                            replies = q4
                            memcache.set('topic_' + str(topic.num) + '_replies_asc_compressed_' + str(page_current), GetPacked(q4), 86400)
                        else:
                            replies = GetUnpacked(replies)
                        template_values['replies'] = replies
                        template_values['replies_count'] = replies.count()
                        t=self.get_template(path,filename)
                        r = t.render(template_values)
                        memcache.set(r_tag, r, 86400)
            template_values['r'] = r
            if topic and member:
                if member.hasFavorited(topic):
                    template_values['favorited'] = True
                else:
                    template_values['favorited'] = False
            if browser['ios']:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                filename = 'topic.html'
            else:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                filename = 'topic.html'
        else:
            if browser['ios']:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                filename = 'topic_not_found.html'
            else:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                filename = 'topic_not_found.html'
        t=self.get_template(path, filename)
        self.finish(t.render(template_values))

        
    def post(self, topic_num):
        site = GetSite()
        ### BEGIN: CAN CONTINUE
        can_continue = True
        if ('Host' in self.request.headers):
            if (self.request.headers['Host'] not in ['www.v2ex.com', 'v2ex.appspot.com', 'fast.v2ex.com', 'beta.v2ex.com', 'us.v2ex.com', 'eu.v2ex.com', 'jp.v2ex.com', 'localhost:10000']):
                can_continue = False
        else:
            can_continue = False
        if ('User-Agent' not in self.request.headers):
            can_continue = False
        if ('Cookie' not in self.request.headers):
            can_continue = False
        if ('Referer' in self.request.headers):
            has_v2ex = False
            if ('http://localhost:10000' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://www.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://v2ex.appspot.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('https://www.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://eu.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://us.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://jp.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('https://v2ex.appspot.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://fast.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://beta.v2ex.com' in self.request.headers['Referer']):
                has_v2ex = True
            if ('http://' + site.domain in self.request.headers['Referer']):
                has_v2ex = True
            if has_v2ex is False:
                can_continue = False
        else:
            can_continue = False
        if ('Content-Type' in self.request.headers):
            if self.request.headers['Content-Type'].startswith( 'application/x-www-form-urlencoded') is False:
                can_continue = False
        else:
            can_continue = False
        if can_continue is False:
            return self.redirect('http://' + site.domain + '/')
        ### END: CAN CONTINUE
        browser = detect(self.request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(self)
        template_values['member'] = member
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        topic_num_str = str(topic_num)
        if len(topic_num_str) > 8:
            if browser['ios']:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
            else:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
            t=self.get_template(path, 'topic_not_found.html')
            self.finish(t.render(template_values))
            return
        if (member):
            topic = False
            topic = GetKindByNum('Topic', int(topic_num))
            template_values['topic'] = topic
            errors = 0
            # Verification: content
            reply_content_error = 0
            reply_content_error_messages = ['',
                u'请输入回复内容',
                u'回复内容长度不能超过 200000 个字符'
            ]
            reply_content = self.request.arguments['content'][0].strip()
            if (len(reply_content) == 0):
                errors = errors + 1
                reply_content_error = 1
            else:
                if (len(reply_content) > 200000):
                    errors = errors + 1
                    reply_content_error = 2
            template_values['reply_content'] = reply_content
            template_values['reply_content_error'] = reply_content_error
            template_values['reply_content_error_message'] = reply_content_error_messages[reply_content_error]
            template_values['errors'] = errors
            if (topic and (errors == 0)):
                reply = Reply()
                reply.topic=topic
                #q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'reply.max')
                q = Counter.selectBy(name='reply.max')
                if (q.count() == 1):
                    counter = q[0]
                    counter.value = counter.value + 1
                else:
                    counter = Counter()
                    counter.name = 'reply.max'
                    counter.value = 1
                #q2 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'reply.total')
                q2 = Counter.selectBy(name='reply.total')
                if (q2.count() == 1):
                    counter2 = q2[0]
                    counter2.value = counter2.value + 1
                else:
                    counter2 = Counter()
                    counter2.name = 'reply.total'
                    counter2.value = 1
                node = False
                section = False
                if topic:
                    node = False
                    section = False
                    node = GetKindByNum('Node', topic.node_num)
                    if (node):
                        section = GetKindByNum('Section', node.section_num)
                    template_values['node'] = node
                    template_values['section'] = section
                reply.num = counter.value
                reply.content = reply_content
                reply.topic = topic
                reply.topic_num = topic.num
                reply.member = member
                reply.member_num = member.num
                reply.created_by = member.username
                reply.created = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                reply.last_modified = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                topic.replies = topic.replies + 1
                topic.node_name = node.name
                topic.node_title = node.title
                topic.last_reply_by = member.username
                topic.last_touched = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                ua = self.request.headers['User-Agent']
                if (re.findall('Mozilla\/5.0 \(iPhone', ua)):
                    reply.source = 'iPhone'
                if (re.findall('Mozilla\/5.0 \(iPod', ua)):
                    reply.source = 'iPod'
                if (re.findall('Mozilla\/5.0 \(iPad', ua)):
                    reply.source = 'iPad'
                if (re.findall('Android', ua)):
                    reply.source = 'Android'
                if (re.findall('Mozilla\/5.0 \(PLAYSTATION 3;', ua)):
                    reply.source = 'PS3'
                reply.sync()
                topic.sync()
                counter.sync()
                counter2.sync()
                store.commit()  #jon add
                
                # Notifications
                
                notified_members = []
                keys = []
                
                # type: reply
                
                if reply.member_num != topic.member_num:
                    #q = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'notification.max')
                    q = Counter.selectBy(name='notification.max')
                    if (q.count() == 1):
                        counter = q[0]
                        counter.value = counter.value + 1
                    else:
                        counter = Counter()
                        counter.name = 'notification.max'
                        counter.value = 1
                    #q2 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'notification.total')
                    q2 = Counter.selectBy(name='notification.total')
                    if (q2.count() == 1):
                        counter2 = q2[0]
                        counter2.value = counter2.value + 1
                    else:
                        counter2 = Counter()
                        counter2.name = 'notification.total'
                        counter2.value = 1
                    
                    notification = Notification(member=topic.member)
                    notification.num = counter.value
                    notification.type = 'reply'
                    notification.payload = reply.content
                    notification.label1 = topic.title
                    notification.link1 = '/t/' + str(topic.num) + '#reply' + str(topic.replies)
                    notification.member = member
                    notification.for_member_num = topic.member_num
                    
                    keys.append(str(topic.member.id))
                    
                    counter.sync()
                    counter2.sync()
                    notification.sync()
                    store.commit()  #jon add
                    
                    for key in keys:
                        taskqueue.add(url='/notifications/check/' + key)
                
                taskqueue.add(url='/notifications/reply/' + str(reply.id))
                
                page_size = TOPIC_PAGE_SIZE
                pages = 1
                if topic.replies > page_size:
                    if (topic.replies % page_size) > 0:
                        pages = int(math.floor(topic.replies / page_size)) + 1
                    else:
                        pages = int(math.floor(topic.replies / page_size))
                
                memcache.set('Topic_' + str(topic.num), topic, 86400)
                memcache.delete('topic_' + str(topic.num) + '_replies_desc_compressed_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_asc_compressed_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_filtered_compressed_' + str(pages))
                
                memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_desktop_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_desktop_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_desktop_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_ios_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_ios_' + str(pages))
                memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_ios_' + str(pages))
                
                memcache.delete('member::' + str(member.num) + '::participated')
                memcache.delete('q_latest_16')
                memcache.delete('home_rendered')
                memcache.delete('home_rendered_mobile')
                if topic.replies < 50:
                    if config.fts_enabled:
                        try:
                            taskqueue.add(url='/index/topic/' + str(topic.num))
                        except:
                            pass
                # Twitter Sync
                if member.twitter_oauth == 1 and member.twitter_sync == 1:
                    access_token = OAuthToken.from_string(member.twitter_oauth_string)
                    twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                    if topic.replies > page_size:
                        link = 'http://' + self.request.headers['Host'] + '/t/' + str(topic.num) + '?p=' + str(pages) + '#r' + str(topic.replies)
                    else:
                        link = 'http://' + self.request.headers['Host'] + '/t/' + str(topic.num) + '#r' + str(topic.replies)
                    link_length = len(link)
                    reply_content_length = len(reply.content)
                    available = 140 - link_length - 1
                    if available > reply_content_length:
                        status = reply.content + ' ' + link
                    else:
                        status = reply.content[0:(available - 4)] + '... ' + link
                    self.write('Status: ' + status)
                    logging.error('Status: ' + status)
                    try:
                        twitter.PostUpdate(status.encode('utf-8'))
                    except:
                        logging.error("Failed to sync to Twitter for Reply #" + str(reply.num))
                if pages > 1:
                    self.redirect('/t/' + str(topic.num) + '?p=' + str(pages) + '#reply' + str(topic.replies))
                else:
                    self.redirect('/t/' + str(topic.num) + '#reply' + str(topic.replies))
            else:
                node = False
                section = False
                node = GetKindByNum('Node', topic.node_num)
                if (node):
                    section = GetKindByNum('Section', node.section_num)
                template_values['node'] = node
                template_values['section'] = section
                if browser['ios']:
                    path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                else:
                    path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                t=self.get_template(path, 'topic.html')
                self.finish(t.render(template_values))
        else:
            self.redirect('/signin')


class TopicEditHandler(BaseHandler):
    def get(self, topic_num):
        site = GetSite()
        browser = detect(self.request)
        template_values = {}
        template_values['site'] = site
        template_values['system_version'] = SYSTEM_VERSION
        errors = 0
        template_values['errors'] = errors
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        template_values['xsrf'] = self.xsrf_form_html()
        topic = False
        topic = GetKindByNum('Topic', int(topic_num))
        if topic:
            template_values['topic'] = topic
        can_edit = False
        ttl = 0
        if member:
            if member.level == 0:
                can_edit = True
            if topic.member_num == member.num:
                now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                if (now - topic.created).seconds < 300:
                    can_edit = True
                    ttl = 300 - (now - topic.created).seconds
                    template_values['ttl'] = ttl
        if (member):
            if (can_edit):
                template_values['member'] = member
                if (topic):
                    template_values['page_title'] = site.title + u' › ' + topic.title + u' › 编辑'
                    template_values['topic_title'] = topic.title
                    template_values['topic_content'] = topic.content
                    node = False
                    section = False
                    node = GetKindByNum('Node', topic.node_num)
                    if (node):
                        section = GetKindByNum('Section', node.section_num)
                    template_values['node'] = node
                    template_values['section'] = section
                    if site.use_topic_types:
                        types = site.topic_types.split("\n")
                        options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                        i = 0
                        for a_type in types:
                            i = i + 1
                            detail = a_type.split(':')
                            if detail[0] == topic.type:
                                options = options + '<option value="' + str(i) + '" selected="selected">' + detail[0] + '</option>'
                            else:
                                options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                        tt = '<div class="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                        template_values['tt'] = tt
                    else:
                        template_values['tt'] = ''
                    #q4 = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1 ORDER BY created ASC", topic.num)
                    q4 = Reply.selectBy(topic_num=topic.num, orderBy='created')
                    template_values['replies'] = q4
                    if browser['ios']:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile', 'edit_topic.html')
                        html= 'edit_topic.html'
                    else:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop', 'edit_topic.html')
                        html= 'edit_topic.html'
                else:
                    path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile', 'topic_not_found.html')
                    html= 'topic_not_found.html'
                t=self.get_template(path, html)
                self.finish(t.render(template_values))
            else:
                self.redirect('/t/' + str(topic_num))
        else:
            self.redirect('/signin')
    
    def post(self, topic_num):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        browser = detect(self.request)
        template_values['system_version'] = SYSTEM_VERSION
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        topic = False
        topic = GetKindByNum('Topic', int(topic_num))
        if (topic):
            template_values['topic'] = topic
        can_edit = False
        ttl = 0
        if member:
            if member.level == 0:
                can_edit = True
            if topic.member_num == member.num:
                now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                if (now - topic.created).seconds < 300:
                    can_edit = True
                    ttl = 300 - (now - topic.created).seconds
                    template_values['ttl'] = ttl
        if member:
            if can_edit:
                template_values['member'] = member
                if (topic):
                    template_values['page_title'] = site.title + u' › ' + topic.title + u' › 编辑'
                    #q2 = db.GqlQuery("SELECT * FROM Node WHERE num = :1", topic.node_num)
                    q2 = Node.selectBy(num=topic.node_num)
                    node = False
                    if (q2.count() == 1):
                        node = q2[0]
                    template_values['node'] = node
                    section = False
                    if node:
                        #q3 = db.GqlQuery("SELECT * FROM Section WHERE num = :1", node.section_num)
                        q3 = Section.selectBy(num=node.section_num)
                        if (q3.count() == 1):
                            section = q3[0]
                    template_values['section'] = section
                    errors = 0
                    # Verification: title
                    topic_title_error = 0
                    topic_title_error_messages = ['',
                        u'请输入主题标题',
                        u'主题标题长度不能超过 120 个字符'
                        ]
                    topic_title = self.request.arguments['title'][0].strip()
                    if (len(topic_title) == 0):
                        errors = errors + 1
                        topic_title_error = 1
                    else:
                        if (len(topic_title) > 120):
                            errors = errors + 1
                            topic_title_error = 2
                    template_values['topic_title'] = topic_title
                    template_values['topic_title_error'] = topic_title_error
                    template_values['topic_title_error_message'] = topic_title_error_messages[topic_title_error]
                    # Verification: content
                    topic_content_error = 0
                    topic_content_error_messages = ['',
                        u'主题内容长度不能超过 200000 个字符'
                    ]
                    topic_content = self.request.arguments['content'][0].strip()
                    topic_content_length = len(topic_content)
                    if (topic_content_length > 200000):
                        errors = errors + 1
                        topic_content_error = 1
                    template_values['topic_content'] = topic_content
                    template_values['topic_content_error'] = topic_content_error
                    template_values['topic_content_error_message'] = topic_content_error_messages[topic_content_error]
                    # Verification: type
                    if site.use_topic_types:
                        types = site.topic_types.split("\n")
                        if len(types) > 0:
                            topic_type = self.request.arguments['type'][0].strip()
                            try:
                                topic_type = int(topic_type)
                                if topic_type < 0:
                                    topic_type = 0
                                if topic_type > len(types):
                                    topic_type = 0
                                if topic_type > 0:
                                    detail = types[topic_type - 1].split(':')
                                    topic_type_label = detail[0]
                                    topic_type_color = detail[1]
                            except:
                                topic_type = 0
                        else:
                            topic_type = 0
                        options = '<option value="0">&nbsp;&nbsp;&nbsp;&nbsp;</option>'
                        i = 0
                        for a_type in types:
                            i = i + 1
                            detail = a_type.split(':')
                            if topic_type == i:
                                options = options + '<option value="' + str(i) + '" selected="selected">' + detail[0] + '</option>'
                            else:
                                options = options + '<option value="' + str(i) + '">' + detail[0] + '</option>'
                        tt = '<div class="sep5"></div><table cellpadding="5" cellspacing="0" border="0" width="100%"><tr><td width="60" align="right">Topic Type</td><td width="auto" align="left"><select name="type">' + options + '</select></td></tr></table>'
                        template_values['tt'] = tt
                    else:
                        template_values['tt'] = ''
                    template_values['errors'] = errors
                    if (errors == 0):
                        topic.title = topic_title
                        topic.content = topic_content
                        if topic_content_length > 0:
                            topic.has_content = True
                            topic.content_length = topic_content_length
                        else:
                            topic.has_content = False
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'portion')
                        t=self.get_template(path,'topic_content.html')
                        output = t.render({'topic' : topic})
                        topic.content_rendered = output.decode('utf-8')
                        if member.level != 0:
                            topic.last_touched = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
                        if site.use_topic_types:
                            if topic_type > 0:
                                topic.type = topic_type_label
                                topic.type_color = topic_type_color
                            else:
                                topic.type = ''
                                topic.type_color = ''        
                        topic.sync()
                        store.commit()  #jon add
                        memcache.delete('Topic_' + str(topic.num))
                        memcache.delete('q_latest_16')
                        memcache.delete('home_rendered')
                        memcache.delete('home_rendered_mobile')
                        if topic.replies < 50:
                            try:
                                taskqueue.add(url='/index/topic/' + str(topic.num))
                            except:
                                pass
                        self.redirect('/t/' + str(topic.num) + '#reply' + str(topic.replies))
                    else:
                        if browser['ios']:
                            path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                        else:
                            path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                        t=self.get_template(path, 'edit_topic.html')
                        self.finish(t.render(template_values))
                else:
                    path = os.path.join(os.path.dirname(__file__), 'tpl', 'mobile')
                    t=self.get_template(path, 'topic_not_found.html')
                    self.finish(t.render(template_values))
            else:
                self.redirect('/t/' + str(topic_num))
        else:
            self.redirect('/signin')

class TopicDeleteHandler(BaseHandler):
    def get(self, topic_num):
        site = GetSite()
        member = CheckAuth(self)
        t = self.request.arguments['t'][0]
        if member:
            if member.level == 0 and (str(member.created_ts) == str(t)):
                #q = db.GqlQuery("SELECT * FROM Topic WHERE num = :1", int(topic_num))
                q = Topic.selectBy(num=int(topic_num))
                if q.count() == 1:
                    topic = q[0]
                    # Bookmarks
                    #q5 = db.GqlQuery("SELECT * FROM TopicBookmark WHERE topic = :1", topic)
                    q5 = TopicBookmark.selectBy(topic=topic)
                    for bookmark in q5:
                        bookmark.delete()
                    # Take care of Node                
                    node = topic.node
                    node.topics = node.topics - 1
                    node.sync()
                    store.commit()  #jon add
                    # Take care of Replies
                    #q2 = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1", int(topic_num))
                    q2 = Reply.selectBy(topic_num=int(topic_num))
                    replies_count = q2.count()
                    if replies_count > 0:
                        for reply in q2:
                            reply.delete()
                        #q3 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'reply.total')
                        q3 = Counter.selectBy(name='reply.total')
                        if q3.count() == 1:
                            counter = q3[0]
                            counter.value = counter.value - replies_count
                            counter.sync()
                            store.commit()  #jon add
                    memcache.delete('Topic_' + str(topic.num))
                    topic.delete()
                    #q4 = db.GqlQuery('SELECT * FROM Counter WHERE name = :1', 'topic.total')
                    q4 = Counter.selectBy(name='topic.total')
                    if q4.count() == 1:
                        counter2 = q4[0]
                        counter2.value = counter2.value - 1
                        counter2.sync()
                        store.commit()  #jon add
                    memcache.delete('q_latest_16')
                    memcache.delete('home_rendered')
                    memcache.delete('home_rendered_mobile')
        self.redirect('/')
                    

class TopicPlainTextHandler(BaseHandler):
    def get(self, topic_num):
        site = GetSite()
        topic = GetKindByNum('topic', topic_num)
        if topic:
            template_values = {}
            template_values['topic'] = topic
            replies = memcache.get('topic_' + str(topic_num) + '_replies_asc')
            if replies is None:
                #q = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1 ORDER BY created ASC", topic.num)
                q = Reply.selectBy(topic_num=topic.num).orderBy('created')
                replies = q
                memcache.set('topic_' + str(topic_num) + '_replies_asc', q, 86400)
            if replies:
                template_values['replies'] = replies
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            t=self.get_template(path,'topic.txt')
            output = t.render(template_values)
            self.set_header('Content-type', 'text/plain;charset=UTF-8')
            self.write(output)
        else:
            self.error(404)


class TopicIndexHandler(BaseHandler):
    def get(self, topic_num):
        site = GetSite()
        if config.fts_enabled:
            if os.environ['SERVER_SOFTWARE'] == 'Development/1.0':
                try:
                    urlfetch.fetch('http://127.0.0.1:20000/index/' + str(topic_num), headers = {"Authorization" : "Basic %s" % base64.b64encode(config.fts_username + ':' + config.fts_password)})
                except:
                    pass
            else:
                urlfetch.fetch('http://' + config.fts_server + '/index/' + str(topic_num), headers = {"Authorization" : "Basic %s" % base64.b64encode(config.fts_username + ':' + config.fts_password)})

class ReplyEditHandler(BaseHandler):
    def get(self, reply_num):
        template_values = {}
        site = GetSite()
        template_values['site'] = site
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        template_values['xsrf'] = self.xsrf_form_html()
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › 编辑回复'
                template_values['member'] = member
                #q = db.GqlQuery("SELECT * FROM Reply WHERE num = :1", int(reply_num))
                q = Reply.selectBy(num=reply_num)
                if q[0]:
                    reply = q[0]
                    topic = reply.topic
                    node = topic.node
                    template_values['reply'] = reply
                    template_values['topic'] = topic
                    template_values['node'] = node
                    template_values['reply_content'] = reply.content
                    path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                    t=self.get_template(path,'edit_reply.html')
                    self.finish(t.render(template_values))
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/signin')
    
    def post(self, reply_num):
        template_values = {}
        site = GetSite()
        template_values['site'] = site
        member = CheckAuth(self)
        l10n = GetMessages(self, member, site)
        template_values['l10n'] = l10n
        if member:
            if member.level == 0:
                template_values['page_title'] = site.title + u' › 编辑回复'
                template_values['member'] = member
                #q = db.GqlQuery("SELECT * FROM Reply WHERE num = :1", int(reply_num))
                q = Reply.selectBy(num=reply_num)
                if q[0]:
                    reply = q[0]
                    topic = reply.topic
                    node = topic.node
                    template_values['reply'] = reply
                    template_values['topic'] = topic
                    template_values['node'] = node
                    # Verification: content
                    errors = 0
                    reply_content_error = 0
                    reply_content_error_messages = ['',
                        u'请输入回复内容',
                        u'回复内容长度不能超过 2000 个字符'
                    ]
                    reply_content = self.request.arguments['content'][0].strip()
                    if (len(reply_content) == 0):
                        errors = errors + 1
                        reply_content_error = 1
                    else:
                        if (len(reply_content) > 2000):
                            errors = errors + 1
                            reply_content_error = 2
                    template_values['reply_content'] = reply_content
                    template_values['reply_content_error'] = reply_content_error
                    template_values['reply_content_error_message'] = reply_content_error_messages[reply_content_error]
                    template_values['errors'] = errors
                    if (errors == 0):
                        reply.content = reply_content
                        reply.sync()
                        store.commit()  #jon add
                        memcache.delete('topic_' + str(topic.num) + '_replies_desc_compressed')
                        memcache.delete('topic_' + str(topic.num) + '_replies_asc_compressed')
                        memcache.delete('topic_' + str(topic.num) + '_replies_filtered_compressed')
                        
                        pages = 1
                        memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_desktop_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_desktop_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_desktop_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_desc_rendered_ios_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_asc_rendered_ios_' + str(pages))
                        memcache.delete('topic_' + str(topic.num) + '_replies_filtered_rendered_ios_' + str(pages))
                        
                        self.redirect('/t/' + str(topic.num) + '#reply' + str(topic.replies))
                    else:
                        path = os.path.join(os.path.dirname(__file__), 'tpl', 'desktop')
                        t=self.get_template(path, 'edit_reply.html')
                        self.finish(t.render(template_values))
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/signin')       

class TopicHitHandler(BaseHandler):
    def get(self, topic_key):
        topic = Topic.get(topic_key)
        if topic:
            topic.hits = topic.hits + 1
            topic.sync()
            store.commit()  #jon add

class PageHitHandler(BaseHandler):
    def get(self, page_key):
        page = Page.get(page_key)
        if page:
            page.hits = page.hits + 1
            page.sync()
            store.commit()  #jon add





