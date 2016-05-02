SYSTEM_VERSION = '2.5.0-dev-7'

import datetime
import hashlib
from v2ex.babel.memcached import mc as memcache

#from sqlobject import *
from v2ex.babel.ext import *
from storm.locals import *

from storm.sqlobject import PropertyAdapter

class BLOBCol(PropertyAdapter, RawStr):
    pass



class Member(SQLObject):
    num = IntCol(length=11,default=0)
    auth = StringCol(length=255,default='')
    deactivated = IntCol(length=11,default=0)
    username = StringCol(length=255,default='')
    username_lower = StringCol(length=255,default='')
    password = StringCol(length=255,default='')
    email = StringCol(length=255,default='')
    email_verified = IntCol(length=11,default=0)
    website = StringCol(length=255,default='')
    psn = StringCol(length=255,default='')
    twitter = StringCol(length=255,default='')
    twitter_oauth = IntCol(length=11,default=0)
    twitter_oauth_key = StringCol(length=255,default='')
    twitter_oauth_secret = StringCol(length=255,default='')
    twitter_oauth_string = StringCol(length=255,default='')
    twitter_sync = IntCol(length=11,default=0)
    twitter_id = IntCol(length=11,default=0)
    twitter_name = StringCol(length=255,default='')
    twitter_screen_name = StringCol(length=255,default='')
    twitter_location = StringCol(length=255,default='')
    twitter_description = StringCol(default='')
    twitter_profile_image_url = StringCol(length=255,default='')
    twitter_url = StringCol(length=255,default='')
    twitter_statuses_count = IntCol(length=11,default=0)
    twitter_followers_count = IntCol(length=11,default=0)
    twitter_friends_count = IntCol(length=11,default=0)
    twitter_favourites_count = IntCol(length=11,default=0)
    use_my_css = IntCol(length=11,default=0)
    my_css = StringCol(default='')
    my_home = StringCol(length=255,default='')
    location = StringCol(length=255,default='')
    tagline = StringCol(default='')
    bio = StringCol(default='')
    avatar_large_url = StringCol(length=255,default='')
    avatar_normal_url = StringCol(length=255,default='')
    avatar_mini_url = StringCol(length=255,default='')
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()
    last_signin = UtcDateTimeCol()
    blocked = StringCol(default='')
    l10n = StringCol(length=255,default='en')
    favorited_nodes = IntCol( default=0)
    favorited_topics = IntCol( default=0)
    favorited_members = IntCol( default=0)
    followers_count = IntCol(length=11,default=0)
    level = IntCol(length=11,default=1000)
    notifications = IntCol(length=11,default=0)
    notification_position = IntCol(length=11,default=0)
    private_token = StringCol(length=255,default='')
    ua = StringCol(length=255,default='')
    newbie = IntCol(length=11,default=0)
    noob = IntCol(length=11,default=0)
    show_home_top = IntCol(length=11,default=1)
    show_quick_post = IntCol(length=11,default=0)
    btc = StringCol(length=255,default='')
    github = StringCol(length=255,default='')
    
    @property
    def username_lower_md5(self):
        return hashlib.md5(self.username_lower).hexdigest()
    
    @property
    def created_ts(self):
        return self.created.strftime("%s")
    
    def hasFavorited(self, something):
        if type(something).__name__ == 'Node':
            n = 'r/n' + str(something.num) + '/m' + str(self.num)
            r = memcache.get(n)
            if r:
                return r
            else:
                #q = db.GqlQuery("SELECT * FROM NodeBookmark WHERE node =:1 AND member = :2", something, self)
                q = NodeBookmark.selectBy(node=something, member=self)
                if q.count() > 0:
                    memcache.set(n, True, 86400 * 14)
                    return True
                else:
                    memcache.set(n, False, 86400 * 14)
                    return False
        else:
            if type(something).__name__ == 'Topic':
                n = 'r/t' + str(something.num) + '/m' + str(self.num)
                r = memcache.get(n)
                if r:
                    return r
                else:
                    #q = db.GqlQuery("SELECT * FROM TopicBookmark WHERE topic =:1 AND member = :2", something, self)
                    q = TopicBookmark.selectBy(topic=something, member=self)
                    if q.count() > 0:
                        memcache.set(n, True, 86400 * 14)
                        return True
                    else:
                        memcache.set(n, False, 86400 * 14)
                        return False
            else:
                if type(something).__name__ == 'Member':
                    n = 'r/m' + str(something.num) + '/m' + str(self.num)
                    r = memcache.get(n)
                    if r:
                        return r
                    else:
                        #q = db.GqlQuery("SELECT * FROM MemberBookmark WHERE one =:1 AND member_num = :2", something, self.num)
                        q = MemberBookmark.selectBy(member=something, member_num=self.num)
                        if q.count() > 0:
                            memcache.set(n, True, 86400 * 14)
                            return True
                        else:
                            memcache.set(n, False, 86400 * 14)
                            return False
                else:
                    return False
    
class Counter(SQLObject):
    name = StringCol(length=255,default='')
    value = IntCol(length=11,default=0)
    created = UtcDateTimeCol()
    last_increased = UtcDateTimeCol()
    
class Section(SQLObject):
    num = IntCol(length=11,default=0)
    name = StringCol(length=255,default='')
    title = StringCol(length=255,default='')
    title_alternative = StringCol(length=255,default='')
    header = StringCol(default='')
    footer = StringCol(default='')
    nodes = IntCol(length=11,default=0)
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()
    
class Node(SQLObject):
    num = IntCol(length=11,default=0)
    section_num = IntCol(length=11,default=0)
    name = StringCol(length=255,default='')
    title = StringCol(length=255,default='')
    title_alternative = StringCol(length=255,default='')
    header = StringCol(default='')
    footer = StringCol(default='')
    sidebar = StringCol(default='')
    sidebar_ads = StringCol(default='')
    category = StringCol(length=255,default='')
    topics = IntCol(length=11,default=0)
    parent_node_name = StringCol(length=255,default='')
    avatar_large_url = StringCol(length=255,default='')
    avatar_normal_url = StringCol(length=255,default='')
    avatar_mini_url = StringCol(length=255,default='')
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()

class Topic(SQLObject):
    num = IntCol(length=11,default=0)
    node = ForeignKey('Node', dbName="node_id")
    node_num = IntCol(length=11,default=0)
    node_name = StringCol(length=255,default='')
    node_title = StringCol(length=255,default='')
    member = ForeignKey('Member', dbName="member_id")
    member_num = IntCol(length=11,default=0)
    title = StringCol(length=255,default='')
    content = StringCol(default='')
    content_rendered = StringCol(default='')
    content_length = IntCol(length=11,default=0)
    has_content = BoolCol(default=True)
    hits = IntCol(length=11,default=0)
    stars = IntCol(length=11,default=0)
    replies = IntCol(length=11,default=0)
    created_by = StringCol(length=255,default='')
    last_reply_by = StringCol(length=255,default='')
    source = StringCol(length=255,default='')
    type = StringCol(length=255,default='')
    type_color = StringCol(length=255,default='')
    explicit = IntCol(length=11,default=0)
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()
    last_touched = UtcDateTimeCol()
    
class Reply(SQLObject):
    num = IntCol(length=11,default=0)
    topic = ForeignKey('Topic', dbName="topic_id")
    topic_num = IntCol(length=11,default=0)
    member = ForeignKey('Member', dbName="member_id")
    member_num = IntCol(length=11,default=0)
    content = StringCol(default='')
    source = StringCol(length=255,default='')
    created_by = StringCol(length=255,default='')
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()
    highlighted = IntCol(length=11,default=0)
    
class Avatar(SQLObject):
    num = IntCol(length=11,default=0)
    name = StringCol(length=255,default='')
    content = BLOBCol()
    
class Note(SQLObject):
    num = IntCol(length=11,default=0)
    member = ForeignKey('Member', dbName="member_id")
    member_num = IntCol(length=11,default=0)
    title = StringCol(length=255,default='')
    content = StringCol()
    body = StringCol(default='')
    length = IntCol(length=11,default=0)
    edits = IntCol(length=11,default=1)
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()

class PasswordResetToken(SQLObject):
    token = StringCol(length=255,default='')
    email = StringCol(length=255,default='')
    member = ForeignKey('Member', dbName="member_id")
    valid = IntCol(length=11,default=1)
    timestamp = IntCol(length=11,default=0)

class Place(SQLObject):
    num = IntCol(length=11,default=0)
    ip = StringCol(length=255,default='')
    name = StringCol(length=255,default='')
    visitors = IntCol(length=11,default=0)
    longitude = FloatCol(default=0.0)
    latitude = FloatCol(default=0.0)
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()

class PlaceMessage(SQLObject):
    num = IntCol(length=11,default=0)
    place = ForeignKey('Place', dbName="place_id")
    place_num = IntCol(length=11,default=0)
    member = ForeignKey('Member', dbName="member_id")
    content = StringCol(default='')
    in_reply_to = ForeignKey('PlaceMessage', dbName="placemessage_id")
    source = StringCol(length=255,default='')
    created = UtcDateTimeCol()

class Checkin(SQLObject):
    place = ForeignKey('Place', dbName="place_id")
    member = ForeignKey('Member', dbName="member_id")
    last_checked_in = UtcDateTimeCol()
    
class Site(SQLObject):
    num = IntCol(length=11,default=0)
    title = StringCol(length=255,default='')
    slogan = StringCol(length=255,default='')
    description = StringCol(default='')
    domain = StringCol(length=255,default='')
    analytics = StringCol(length=255,default='')
    home_categories = StringCol(default='')
    meta = StringCol(default='')
    home_top = StringCol(default='')
    theme = StringCol(length=255,default='default')
    l10n = StringCol(length=255,default='en')
    use_topic_types = BoolCol(default=False)
    topic_types = StringCol(default='')
    topic_view_level = IntCol(length=11,default=-1)
    topic_create_level = IntCol(length=11,default=1000)
    topic_reply_level = IntCol(length=11,default=1000)
    data_migration_mode = IntCol(length=11,default=0)
    
class Minisite(SQLObject):
    num = IntCol(length=11,default=0)
    name = StringCol(length=255,default='')
    title = StringCol(length=255,default='')
    description = StringCol(default='')
    pages = IntCol(length=11,default=0)
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()

class Page(SQLObject):
    num = IntCol(length=11,default=0)
    name = StringCol(length=255,default='')
    title = StringCol(length=255,default='')
    minisite = ForeignKey('Minisite', dbName="minisite_id")
    content = StringCol(default='')
    content_rendered = StringCol(default='')
    content_type = StringCol(length=255,default='text/html')
    weight = IntCol(length=11,default=0)
    mode = IntCol(length=11,default=0)
    hits = IntCol(length=11,default=0)
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()

class NodeBookmark(SQLObject):
    node = ForeignKey('Node', dbName="node_id")
    member = ForeignKey('Member', dbName="member_id")
    created = UtcDateTimeCol()

class TopicBookmark(SQLObject):
    topic = ForeignKey('Topic', dbName="topic_id")
    member = ForeignKey('Member', dbName="member_id")
    created = UtcDateTimeCol()

class MemberBookmark(SQLObject):
    member = ForeignKey('Member', dbName="member_id")
    member_num = IntCol(length=11,default=0)
    created = UtcDateTimeCol()

# Notification type: mention_topic, mention_reply, reply
class Notification(SQLObject):
    num = IntCol(length=11,default=0)
    member = ForeignKey('Member', dbName="member_id")
    for_member_num = IntCol(length=11,default=0)
    type = StringCol(length=255,default='')
    payload = StringCol(length=255,default='')
    label1 = StringCol(length=255,default='')
    link1 = StringCol(length=255,default='')
    label2 = StringCol(length=255,default='')
    link2 = StringCol(length=255,default='')
    created = UtcDateTimeCol()

class Item(SQLObject):
    title = StringCol(length=255,default='')
    description = StringCol()
    price = StringCol(length=255,default='')
    category = StringCol(length=255,default='gadgets')
    column = IntCol(length=11,default=1)
    link_official = StringCol(length=255,default='')
    link_picture = StringCol(length=255,default='')
    link_buy = StringCol(length=255,default='')
    node_name = StringCol(length=255,default='')
    published = IntCol(length=11,default=0)
    created = UtcDateTimeCol()
    last_modified = UtcDateTimeCol()