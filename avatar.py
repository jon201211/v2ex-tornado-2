#!/usr/bin/env python
# coding=utf-8

from v2ex.babel.memcached import mc as memcache
from jinja2 import Template, Environment, FileSystemLoader

from v2ex.babel import Avatar
from v2ex.babel.handlers import BaseHandler

from v2ex.babel.security import *
from v2ex.babel.da import *
        
class AvatarHandler(BaseHandler):
    def get(self, member_num, size):
        avatar = GetKindByName('Avatar', 'avatar_' + str(member_num) + '_' + str(size))
        if avatar:
            self.set_header('Content-Type', "image/png")
            self.set_header('Cache-Control', "max-age=172800, public, must-revalidate")
            self.set_header('Expires', "Sun, 25 Apr 2011 20:00:00 GMT")
            self.write(avatar.content)
        else:
            self.redirect('/static/img/avatar_' + str(size) + '.png')

class NodeAvatarHandler(BaseHandler):
    def get(self, node_num, size):
        avatar = GetKindByName('Avatar', 'node_' + str(node_num) + '_' + str(size))
        if avatar:
            self.set_header('Content-Type', "image/png")
            self.set_header('Cache-Control', "max-age=172800, public, must-revalidate")
            self.set_header('Expires', "Sun, 25 Apr 2011 20:00:00 GMT")
            self.write(avatar.content)
        else:
            self.error(404)
            
