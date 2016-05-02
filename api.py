#!/usr/bin/env python
# coding=utf-8

import os
import re
import time
import datetime
import hashlib
import logging
import string
import random
import base64
import tornado.web


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
from v2ex.babel.ext.cookies import Cookies

from v2ex.babel.handlers import BaseHandler
#from django.utils import simplejson as json
import json

#template.register_template_library('v2ex.templatetags.filters')

from topic import TOPIC_PAGE_SIZE

class ApiHandler(BaseHandler):
    def write(self, output):
        if output is None:
            output = ''
        callback = self.request.arguments('callback')[0]
        if callback:
            if not isinstance(output, unicode):
                output = output.decode('utf-8')
            self.set_header('Content-type', 'application/javascript; charset=utf-8')
            output = '%s(%s)' % (callback, output)
        else:
            self.set_header('Content-type', 'application/json; charset=utf-8')
        self.write(output)

# Site
# /api/site/stats.json
class SiteStatsHandler(ApiHandler):
    def get(self):
        template_values = {}
        template_values['topic_max'] = GetKindByName('Counter', 'topic.max')
        template_values['member_max'] = GetKindByName('Counter', 'member.max')
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
        t = self.get_template(path, 'site_stats.json')
        self.write(t.render(template_values))

# /api/site/info.json
class SiteInfoHandler(ApiHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
        t = self.get_template(path, 'site_info.json')
        self.write(t.render(template_values))
# Nodes
# /api/nodes/all.json
class NodesAllHandler(ApiHandler):
    def get(self):
        output = memcache.get('api_nodes_all')
        if output is None:
            site = GetSite()
            template_values = {}
            template_values['site'] = site
            nodes = memcache.get('api_nodes_all')
            if nodes is None:
                #nodes = db.GqlQuery("SELECT * FROM Node")
                nodes = Node.select()
                memcache.set('api_nodes_all', nodes, 3600)
            template_values['nodes'] = nodes
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            t = self.get_template(path,'nodes_all.json')
            output = t.render(template_values)
            memcache.set('api_nodes_all', output, 86400)
            self.write(output)



# /api/nodes/show.json
class NodesShowHandler(ApiHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        method_determined = False
        parameter_id = self.request.arguments['id'][0]
        if parameter_id:
            method_determined = True
        if method_determined is not True:
            parameter_name = self.request.arguments['name'][0]
            if parameter_name:
                method_determined = True
        if method_determined is True:
            if parameter_id:
                node = GetKindByNum('Node', int(parameter_id))
            else:
                node = GetKindByName('Node', str(parameter_name))
            if node is not False:
                template_values['node'] = node
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                t = self.get_template(path,'nodes_show.json')
                output = t.render(template_values)
            else:
                template_values['message'] = 'Node not found'
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                t = self.get_template(path,'error.json')
                self.finish(t.render(template_values))
        else:
            template_values['message'] = "Required parameter id or name is missing"
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            t = self.get_template(path,'error.json')
            self.finish(t.render(template_values))
# Topics
# /api/topics/latest.json
class TopicsLatestHandler(ApiHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        topics = memcache.get('api_topics_latest')
        if topics is None:
            #topics = db.GqlQuery("SELECT * FROM Topic ORDER BY created DESC LIMIT 20")
            topics = Topic.selectBy(orderBy='-created').limit(20)
            memcache.set('api_topics_latest', topics, 120)
        template_values['topics'] = topics
        template_values['topics_count'] = topics.count()
        path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
        t = self.get_template(path,'topics_latest.json')
        self.finish(t.render(template_values))

# /api/topics/show.json
class TopicsShowHandler(ApiHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        method_determined = False
        parameter_id = self.request.arguments['id'][0]
        parameter_username = False
        parameter_node_id = False
        parameter_node_name = False
        if parameter_id:
            method_determined = True
        if method_determined is False:
            parameter_username = self.request.arguments['username'][0]
            if parameter_username:
                method_determined = True
        if method_determined is False:
            parameter_node_id = self.request.arguments['node_id'][0]
            if parameter_node_id:
                method_determined = True
        if method_determined is False:
            parameter_node_name = self.request.arguments['node_name'][0]
            if parameter_node_name:
                method_determined = True
        if method_determined is False:
            template_values['message'] = "Required parameter id, username, node_id or node_name is missing"
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            self.set_status(400, 'Bad Request')
            t = self.get_template(path,'error.json')
            self.finish(t.render(template_values))
        else:
            topics = False
            topic = False
            if parameter_id:
                try:
                    topic = GetKindByNum('Topic', int(parameter_id))
                    if topic is not False:
                        topics = []
                        topics.append(topic)
                        template_values['topic'] = topic
                except:
                    topics = False
            if topics is False:
                if parameter_username:
                    one = GetMemberByUsername(parameter_username)
                    if one is not False:
                        #topics = db.GqlQuery("SELECT * FROM Topic WHERE member_num = :1 ORDER BY created DESC LIMIT 20", one.num)
                        topics = Topic.selectBy(member_num=one.num).orderBy('-created').limit(20)
                        template_values['topics'] = topics
            if topics is False:
                try:
                    if parameter_node_id:
                        node = GetKindByNum('Node', int(parameter_node_id))
                        if node is not False:
                            #topics = db.GqlQuery("SELECT * FROM Topic WHERE node_num = :1 ORDER BY last_touched DESC LIMIT 20", node.num)
                            topics = Topic.selectBy(node_num=one.num).orderBy('-last_touched').limit(20)
                            template_values['topics'] = topics
                except:
                    topics = False
            if topics is False:
                if parameter_node_name:
                    node = GetKindByName('Node', str(parameter_node_name))
                    if node is not False:
                        #topics = db.GqlQuery("SELECT * FROM Topic WHERE node_num = :1 ORDER BY last_touched DESC LIMIT 20", node.num)
                        topics = Topic.selectBy(node_num=node.num).orderBy('-last_touched').limit(20)
                        template_values['topics'] = topics
            if topic or topics:
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                t=self.get_template(path,'topics_show.json')
                self.finish(t.render(template_values))
            else:
                template_values['message'] = "Failed to get topics"
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                self.set_status(400, 'Bad Request')
                t=self.get_template(path,'error.json')
                self.finish(t.render(template_values))

# /api/topics/create.json
class TopicsCreateHandler(BaseHandler):
    def post(self):
        authenticated = False
        if 'Authorization' in self.request.headers:
            auth = self.request.headers['Authorization']
            decoded = base64.b64decode(auth[6:])
            authenticated = True
        if authenticated:
            self.response.out.write('OK')
        else:    
            site = GetSite()
            template_values = {}
            template_values['site'] = site
            template_values['message'] = "Authentication required"
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            t = self.get_template(path,'error.json')
            output = t.render(template_values)
            self.set_status(401, 'Unauthorized')
            self.set_header('Content-type', 'application/json')
            self.set_header('WWW-Authenticate', 'Basic realm="' + site.domain + '"')
            self.write(output)

# Replies
# /api/replies/show.json
class RepliesShowHandler(ApiHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        method_determined = False
        topic_id = self.request.arguments['topic_id'][0]
        page = self.request.arguments['page'][0]
        if(page==None):
            page=1
        page_size = TOPIC_PAGE_SIZE

        if topic_id:
            page_start = (int(page) - 1) * page_size
            #replies = db.GqlQuery("SELECT * FROM Reply WHERE topic_num = :1 ORDER BY created ASC LIMIT " + str(page_start) + "," + str(page_size), int(topic_id))
            #replies = Reply.selectBy(topic_num=int(topic_id)).orderBy('created')[page_start:page_size]
            replies = Reply.select(Reply.q.topic_num==int(topic_id),orderBy='created').offset(page_start).limit(page_size)
            if replies:
                template_values['replies'] = replies
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                t=self.get_template(path,'replies_show.json')
                self.finish(t.render(template_values))
            else:
                template_values['message'] = "Failed to get replies"
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                self.set_status(400, 'Bad Request')
                t=self.get_template(path,'error.json')
                self.finish(t.render(template_values))
        else:
            template_values['message'] = "Required parameter topic_id is missing"
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            self.set_status(400, 'Bad Request')
            t=self.get_template(path,'error.json')
            self.finish(t.render(template_values))


# Members
# /api/members/show.json
class MembersShowHandler(ApiHandler):
    def get(self):
        site = GetSite()
        template_values = {}
        template_values['site'] = site
        username = self.request.arguments['username'][0]
        if username:
            one = GetMemberByUsername(username)
            if one is not False:
                if one.avatar_mini_url:
                    if (one.avatar_mini_url[0:1] == '/'):
                        one.avatar_mini_url = 'http://' + site.domain + one.avatar_mini_url
                        one.avatar_normal_url = 'http://' +  site.domain + one.avatar_normal_url
                        one.avatar_large_url = 'http://' + site.domain + one.avatar_large_url
                template_values['member'] = one
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                t=self.get_template(path,'members_show.json')
                self.finish(t.render(template_values))
            else:
                template_values['message'] = "Member not found"
                path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
                self.set_status(400, 'Bad Request')
                t=self.get_template(path,'error.json')
                self.finish(t.render(template_values))
        else:
            template_values['message'] = "Required parameter username is missing"
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            self.set_status(400, 'Bad Request')
            t=self.get_template(path,'error.json')
            self.finish(t.render(template_values))

                
class CurrencyHandler(ApiHandler):
    def get(self):
        codes = ['EUR', 'JPY', 'CNY', 'CHF', 'AUD', 'TWD', 'CAD', 'GBP', 'HKD', 'MYR', 'NZD', 'PHP', 'SGD', 'THB']
        template_values = {}
        o = memcache.get('currency.json')
        if o is not None:
            pass
        else:
            for code in codes:
                url = 'http://www.google.com/ig/calculator?hl=en&q=1USD=?' + code
                response = urlfetch.fetch(url)
                m = re.findall('rhs: "([0-9\.]+)', response.content)
                if len(m) > 0:
                    value = m[0].strip().replace(' ', '')
                else:
                    value = 0
                template_values[code.lower()] = value
            path = os.path.join(os.path.dirname(__file__), 'tpl', 'api')
            t=self.get_template(path,'currency.json')
            o = t.render(template_values)
            memcache.set('currency.json', o, 86400)
        self.write(o)
