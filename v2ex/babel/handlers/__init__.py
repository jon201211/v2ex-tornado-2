#!/usr/bin/env python
# coding=utf-8

import os
import random
import re

import tornado.web

from v2ex.babel import Member, Site
from v2ex.babel.memcached import mc as memcache
from jinja2 import Template, Environment, FileSystemLoader

from v2ex.babel.ext.cookies import Cookies
from v2ex.templatetags.filters import *

from v2ex.babel.ext import *

class BaseHandler(tornado.web.RequestHandler):

    _path_to_env = {}

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        #self.session = session.TornadoSession(application.session_manager, self)
        #self._title = self.settings['app_name']

    def set_template_path(self, template_path):
        self.settings['template_path'] = template_path

    def get_template_path(self):
        """ 获取模板路径 """
        return self.settings['template_path']

    def create_template_loader(self, template_path):
        """ 根据template_path创建相对应的Jinja2 Environment """
        temp_path = template_path
        if isinstance(template_path, (list, tuple)):
            temp_path = template_path[0]

        env = BaseHandler._path_to_env.get(temp_path)
        if not env:
            _loader = FileSystemLoader(template_path)
            env = Environment(loader = _loader)
            BaseHandler._path_to_env[temp_path] = env
        return env

    def render_string(self, template_name, **kwargs):
        """ 使用Jinja2模板引擎 """
        env = self.create_template_loader(self.get_template_path())
        env.filters['timezone'] = timezone
        env.filters['autolink2'] = autolink2
        env.filters['autolink'] = autolink
        env.filters['imgly'] = imgly
        env.filters['clly'] = clly
        env.filters['sinaimg'] = sinaimg
        env.filters['avatar'] = avatar
        env.filters['youtube'] = youtube
        env.filters['youku'] = youku
        env.filters['tudou'] = tudou
        env.filters['mentions'] = mentions
        env.filters['gravatar'] = gravatar
        env.filters['avatar'] = avatar
        env.filters['gist'] = gist
        env.filters['escapejs'] = escapejs
        env.filters['timesince'] = timesince
        #env.filters['escape'] = escape
        t = env.get_template(template_name)
        namespace = self.get_template_namespace()
        namespace.update(kwargs)
        return t.render(**namespace)

    def get_template(self,path,template_name):
        """ 使用Jinja2模板引擎 """
        self.set_template_path(path)
        env = self.create_template_loader(self.get_template_path())
        env.filters['timezone'] = timezone
        env.filters['autolink2'] = autolink2
        env.filters['autolink'] = autolink
        env.filters['imgly'] = imgly
        env.filters['clly'] = clly
        env.filters['sinaimg'] = sinaimg
        env.filters['avatar'] = avatar
        env.filters['youtube'] = youtube
        env.filters['youku'] = youku
        env.filters['tudou'] = tudou
        env.filters['mentions'] = mentions
        env.filters['gravatar'] = gravatar
        env.filters['avatar'] = avatar
        env.filters['gist'] = gist
        env.filters['escapejs'] = escapejs
        env.filters['timesince'] = timesince
        #env.filters['escape'] = escape
        env.filters['linebreaksbr'] = linebreaksbr
        env.filters['date'] = date
        env.filters['divisibleby'] = divisibleby
        t = env.get_template(template_name)
        return t

    @property
    def values(self):
        if not hasattr(self, "_values"):
            self._values = {}
            self._values['rnd'] = random.randrange(1, 100)
            self._values['site'] = self.site
            self._values['member'] = self.member
            self._values['l10n'] = self.l10n
            self._values['browser'] = self.browser
        return self._values

    @property
    def browser(self):
        if not hasattr(self, "_browser"):
            result = {}
            if 'User-Agent' in self.request.headers:
                user_agent = self.request.headers['User-Agent']
                if (re.search('iPod|iPhone|Android|Opera Mini|BlackBerry|webOS|UCWEB|Blazer|PSP', user_agent)):
                    result['ios'] = True
                else:
                    result['ios'] = False
            else:
                user_agent = ''
                result['ios'] = False
            result['ua'] = user_agent
            self._browser = result
        return self._browser
    
    @property
    def site(self):
        if not hasattr(self, "_site"):
            site = memcache.get('site')
            if site is not None:
                self._site = site
            else:
                #q = db.GqlQuery("SELECT * FROM Site WHERE num = 1")
                q = Site.selectBy(num=1)
                if q.count() == 1:
                    site = q[0]
                    if site.l10n is None:
                        site.l10n = 'en'
                    if site.meta is None:
                        site.meta = ''
                    memcache.set('site', site, 86400)
                    self._site = site
                else:
                    site = Site()
                    site.num = 1
                    site.title = 'V2EX'
                    site.domain = 'v2ex.appspot.com'
                    site.slogan = 'way to explore'
                    site.l10n = 'en'
                    site.description = ''
                    site.meta = ''
                    site.sync()
                    store.commit()  #jon add

                    memcache.set('site', site, 86400)
                    self._site = site
        return self._site
    
    @property
    def member(self):
        if not hasattr(self, "_member"):
            ip = False
            member = False
            if 'X-Real-IP' in self.request.headers:
                ip = self.request.headers['X-Real-IP']
            else:
                ip = self.request.remote_ip
            #cookies = Cookies(self, max_age = 86400 * 14, path = '/')
            auth = self.get_cookie('auth')
            #if 'auth' in cookies:
            if auth is not None:
                #auth = cookies['auth']
                member_num = memcache.get(auth)
                if member_num > 0:
                    member = memcache.get('Member_' + str(member_num))
                    if member is None:
                        #q = db.GqlQuery("SELECT * FROM Member WHERE num = :1", member_num)
                        q = Member.selectBy(num=member_num)
                        if q.count() == 1:
                            member = q[0]
                            memcache.set('Member_' + str(member_num), member, 86400 * 14)
                    if member:
                        member.ip = ip
                else:
                    #q = db.GqlQuery("SELECT * FROM Member WHERE auth = :1", auth)
                    q = Member.selectBy(auth=auth)
                    if (q.count() == 1):
                        member_num = q[0].num
                        member = q[0]
                        memcache.set(auth, member_num, 86400 * 14)
                        memcache.set('Member_' + str(member_num), member, 86400 * 14)
                        member.ip = ip
            self._member = member
        return self._member
    
    @property
    def l10n(self):
        if not hasattr(self, "_l10n"):
            if self.member is not False:
                if self.member.l10n == 'en':
                    from v2ex.babel.l10n.messages import en as messages
                if self.member.l10n == 'zh-Hans':
                    from v2ex.babel.l10n.messages import zhHans as messages
            else:
                if self.site.l10n == 'en':
                    from v2ex.babel.l10n.messages import en as messages
                if self.site.l10n == 'zh-Hans':
                    from v2ex.babel.l10n.messages import zhHans as messages
            self._l10n = messages
        return self._l10n
    
    def set_title(self, title):
        self.values['page_title'] = self.site.title + u' › ' + title
    
    def finalize(self, template_name, mobile_optimized=False, template_root='desktop', template_type='html'):
        """Insert common values into handler's dictionary for template.
        
        Load proper template according to current browser capacity.
        
        Mobile optimized templates are optional. Default to False.
        """
        if self.browser['ios'] and mobile_optimized:
            path = os.path.join('tpl', 'mobile')
        else:
            path = os.path.join('tpl', template_root)

        t = self.get_template(path,template_name + '.' + template_type)
        self.finish(t.render(self.values))

    def get(self):
        pass
        
    def post(self):
        pass
    
    def escape(self, text):
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text