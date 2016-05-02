# coding: UTF-8
import os
import re
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.autoreload
import unicodedata
from tornado.options import define, options
from jinja2 import Template, Environment, FileSystemLoader

#import filter

#from handlers import *
#import session
#from mongoengine import *



from api import *
from avatar import *
from backstage import *
from blog import *
from css import *
from favorite import *
from feed import *
from images import *
from member import *
from misc import *
from money import *
from my import *
from notes import *
from notifications import *
from page import *
from place import *
from queue import *
from sso import *
from t import *
from template import *
from topic import *
#from xmpp import *
from main import *



#def markdown_tag(str):
#    return markdown.markdown(str)

define("port", default=8888, help="run on the given port", type=int)
#define("mongo_host", default="127.0.0.1:3306", help="database host")
#define("mongo_database", default="quora", help="database name")



class Application(tornado.web.Application):

    def __init__(self):
        settings = dict(
            app_name=u"我知",
            template_path=os.path.join(os.path.dirname(__file__), "tpl"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="81o0TzKaPpGtYdkL5gEmGepeuuYi7EPnp2XdTP1o&Vo=",
            login_url="/login",
            session_secret='08091287&^(01',
            session_dir=os.path.join(os.path.dirname(__file__), "tmp/session"),
        )

        handlers = [
        # xmpp handlers chat
        #('/_ah/xmpp/message/chat/', XMPPHandler),

        # topic handlers !!!
        ('/new/(.*)', NewTopicHandler),
        ('/t/([0-9]+)', TopicHandler),
        ('/t/([0-9]+).txt', TopicPlainTextHandler),
        ('/edit/topic/([0-9]+)', TopicEditHandler),
        ('/delete/topic/([0-9]+)', TopicDeleteHandler),
        ('/index/topic/([0-9]+)', TopicIndexHandler),
        ('/edit/reply/([0-9]+)', ReplyEditHandler),
        ('/hit/topic/(.*)', TopicHitHandler),
        ('/hit/page/(.*)', PageHitHandler),


        # template handlers
        ('/my/nodes', MyNodesHandler),

        # twitter handlers
        ('/twitter/?', TwitterHomeHandler),
        ('/twitter/mentions/?', TwitterMentionsHandler),
        ('/twitter/inbox/?', TwitterDMInboxHandler),
        ('/twitter/user/([a-zA-Z0-9\_]+)', TwitterUserTimelineHandler),
        ('/twitter/link', TwitterLinkHandler),
        ('/twitter/unlink', TwitterUnlinkHandler),
        ('/twitter/oauth', TwitterCallbackHandler),
        ('/twitter/tweet', TwitterTweetHandler),
        ('/twitter/api/?', TwitterApiCheatSheetHandler),

        # sso handlers
        ('/sso/v0', SSOV0Handler),
        ('/sso/x0', SSOX0Handler),

        # queue handlers
        ('/add/star/topic/(.*)', AddStarTopicHandler),
        ('/minus/star/topic/(.*)', MinusStarTopicHandler),

        # place handlers
        ('/place/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', PlaceHandler),
        ('/remove/place_message/(.*)', PlaceMessageRemoveHandler),

        # page handlers
        ('/about', AboutHandler),
        ('/faq', FAQHandler),
        ('/mission', MissionHandler),
        ('/advertise', AdvertiseHandler),
        ('/advertisers', AdvertisersHandler),

        # notification handlers
        ('/notifications/?', NotificationsHandler),
        ('/notifications/check/(.+)', NotificationsCheckHandler),
        ('/notifications/reply/(.+)', NotificationsReplyHandler),
        ('/notifications/topic/(.+)', NotificationsTopicHandler),
        ('/n/([a-z0-9]+).xml', NotificationsFeedHandler),

        # note handlers
        ('/notes', NotesHomeHandler),
        ('/notes/new', NotesNewHandler),
        ('/notes/([0-9]+)', NotesItemHandler),
        ('/notes/([0-9]+)/erase', NotesItemEraseHandler),
        ('/notes/([0-9]+)/edit', NotesItemEditHandler),

        # my handlers
        ('/my/nodes', MyNodesHandler),
        ('/my/topics', MyTopicsHandler),
        ('/my/following', MyFollowingHandler),

        # money handler
        ('/money/dashboard/?', MoneyDashboardHandler),

        # misc handlers
        ('/time/?', WorldClockHandler),
        ('/(md5|sha1)/?', MD5Handler),
        ('/bfbcs/poke/(ps3|360|pc)/(.*)', BFBCSPokeHandler),

        # member handlers
        ('/member/([a-z0-9A-Z\_\-]+)', MemberHandler),
        ('/member/([a-z0-9A-Z\_\-]+).json', MemberApiHandler),
        ('/settings', SettingsHandler),
        ('/settings/password', SettingsPasswordHandler),
        ('/settings/avatar', SettingsAvatarHandler),
        ('/block/(.*)', MemberBlockHandler),
        ('/unblock/(.*)', MemberUnblockHandler),

        # images handlers
        ('/images/upload', ImagesUploadHandler),
        ('/images/upload/rules', ImagesUploadRulesHandler),
        ('/images/?', ImagesHomeHandler),

        # feed handlers
        ('/index.xml', FeedHomeHandler),
        ('/read.xml', FeedReadHandler),
        ('/feed/v2ex.rss', FeedHomeHandler),
        ('/feed/([0-9a-zA-Z\-\_]+).xml', FeedNodeHandler),

        # favorite handlers
        ('/favorite/node/([a-zA-Z0-9]+)', FavoriteNodeHandler),
        ('/unfavorite/node/([a-zA-Z0-9]+)', UnfavoriteNodeHandler),
        ('/favorite/topic/([0-9]+)', FavoriteTopicHandler),
        ('/unfavorite/topic/([0-9]+)', UnfavoriteTopicHandler),
        ('/follow/([0-9]+)', FollowMemberHandler),
        ('/unfollow/([0-9]+)', UnfollowMemberHandler),

        # css handlers
        ('/css/([a-zA-Z0-9]+).css', CSSHandler),

        # blog handlers
        ('/blog/([a-z0-9A-Z\_\-]+)', BlogHandler),
        ('/entry/([0-9]+)', BlogEntryHandler),
        # backend handlers
        ('/backstage', BackstageHomeHandler),
        ('/backstage/new/minisite', BackstageNewMinisiteHandler),
        ('/backstage/minisite/(.*)', BackstageMinisiteHandler),
        ('/backstage/remove/minisite/(.*)', BackstageRemoveMinisiteHandler),
        ('/backstage/new/page/(.*)', BackstageNewPageHandler),
        ('/backstage/page/(.*)', BackstagePageHandler),
        ('/backstage/remove/page/(.*)', BackstageRemovePageHandler),
        ('/backstage/new/section', BackstageNewSectionHandler),
        ('/backstage/section/(.*)', BackstageSectionHandler),
        ('/backstage/new/node/(.*)', BackstageNewNodeHandler),
        ('/backstage/node/([a-z0-9A-Z]+)', BackstageNodeHandler),
        ('/backstage/node/([a-z0-9A-Z]+)/avatar', BackstageNodeAvatarHandler),
        ('/backstage/remove/reply/(.*)', BackstageRemoveReplyHandler),
        ('/backstage/tidy/reply/([0-9]+)', BackstageTidyReplyHandler),
        ('/backstage/tidy/topic/([0-9]+)', BackstageTidyTopicHandler),
        ('/backstage/deactivate/user/(.*)', BackstageDeactivateUserHandler),
        ('/backstage/move/topic/(.*)', BackstageMoveTopicHandler),
        ('/backstage/site', BackstageSiteHandler),
        ('/backstage/topic', BackstageTopicHandler),
        ('/backstage/remove/mc', BackstageRemoveMemcacheHandler),
        ('/backstage/member/(.*)', BackstageMemberHandler),
        ('/backstage/members', BackstageMembersHandler),
        ('/backstage/remove/notification/(.*)', BackstageRemoveNotificationHandler),
        # avartar handlers
        ('/avatar/([0-9]+)/(large|normal|mini)', AvatarHandler),
        ('/navatar/([0-9]+)/(large|normal|mini)', NodeAvatarHandler),
        # api handlers
        ('/api/site/stats.json', SiteStatsHandler),
        ('/api/site/info.json', SiteInfoHandler),
        ('/api/nodes/all.json', NodesAllHandler),
        ('/api/nodes/show.json', NodesShowHandler),
        ('/api/topics/latest.json', TopicsLatestHandler),
        ('/api/topics/show.json', TopicsShowHandler),
        ('/api/topics/create.json', TopicsCreateHandler),
        ('/api/replies/show.json', RepliesShowHandler),
        ('/api/members/show.json', MembersShowHandler),
        ('/api/currency.json', CurrencyHandler),


        # main.py handlers
        ('/', HomeHandler),
        ('/planes/?', PlanesHandler),
        ('/recent', RecentHandler),
        ('/ua', UAHandler),
        ('/signin', SigninHandler),
        ('/signup', SignupHandler),
        ('/signout', SignoutHandler),
        ('/forgot', ForgotHandler),
        ('/reset/([0-9]+)', PasswordResetHandler),
        ('/go/([a-zA-Z0-9]+)/graph', NodeGraphHandler),
        ('/go/([a-zA-Z0-9]+)', NodeHandler),
        ('/n/([a-zA-Z0-9]+).json', NodeApiHandler),
        ('/q/(.*)', SearchHandler),
        ('/_dispatcher', DispatcherHandler),
        ('/changes', ChangesHandler),
        ('/(.*)', RouterHandler)

        ]

        #self.session_manager = session.TornadoSessionManager(settings["session_secret"], settings["session_dir"])
        tornado.web.Application.__init__(self, handlers, **settings)

        # Connection MongoDB
        #connect(options.mongo_database)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__ == "__main__":
    main()
