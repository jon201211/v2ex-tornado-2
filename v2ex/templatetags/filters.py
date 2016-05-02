import re, string
import logging
from v2ex.babel.ext import bleach

import datetime
import urllib, hashlib

import pytz
import calendar
import dateutil
from dateutil.parser import parser

# Configuration for urlize() function
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']

# list of possible strings used for bullets in bulleted lists
DOTS = ['&middot;', '*', '\xe2\x80\xa2', '&#149;', '&bull;', '&#8226;']

unencoded_ampersands_re = re.compile(r'&(?!(\w+|#\d+);)')
word_split_re = re.compile(r'(\s+)')
punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
    '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
link_target_attribute_re = re.compile(r'(<a [^>]*?)target=[^\s>]+')
html_gunk_re = re.compile(r'(?:<br clear="all">|<i><\/i>|<b><\/b>|<em><\/em>|<strong><\/strong>|<\/?smallcaps>|<\/?uppercase>)', re.IGNORECASE)
hard_coded_bullets_re = re.compile(r'((?:<p>(?:%s).*?[a-zA-Z].*?</p>\s*)+)' % '|'.join([re.escape(x) for x in DOTS]), re.DOTALL)
trailing_empty_content_re = re.compile(r'(?:<p>(?:&nbsp;|\s|<br \/>)*?</p>\s*)+\Z')
del x # Temporary variable

def timezone(value, offset):
    #if offset > 12:
    #    offset = 12 - offset
    return value #+ timedelta(hours=offset)


def autolink2(text):
    return bleach.linkify(text)


def autolink(text, trim_url_limit=None, nofollow=False):
    """
    Converts any URLs in text into clickable links. Works on http://, https:// and
    www. links. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right thing.

    If trim_url_limit is not None, the URLs in link text will be limited to
    trim_url_limit characters.

    If nofollow is True, the URLs in link text will get a rel="nofollow" attribute.
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (x[:limit] + (len(x) >=limit and '...' or ''))  or x
    words = word_split_re.split(text)
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or ('@' not in middle and not middle.startswith('http://') and not middle.startswith('https://') and \
                    len(middle) > 0 and middle[0] in string.letters + string.digits and \
                    (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                middle = '<a href="http://%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = '<a href="%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and not ':' in middle \
                and simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return ''.join(words)


# auto convert img.ly/abcd links to image tags
def imgly(value):
    imgs = re.findall('(http://img.ly/[a-zA-Z0-9]+)\s?', value)
    if (len(imgs) > 0):
        for img in imgs:
            img_id = re.findall('http://img.ly/([a-zA-Z0-9]+)', img)
            if (img_id[0] != 'system' and img_id[0] != 'api'):
                value = value.replace('http://img.ly/' + img_id[0], '<a href="http://img.ly/' + img_id[0] + '" target="_blank"><img src="http://picky-staging.appspot.com/img.ly/show/large/' + img_id[0] + '" class="imgly" border="0" /></a>')
        return value
    else:
        return value


# auto convert cl.ly/abcd links to image tags
def clly(value):
    #imgs = re.findall('(http://cl.ly/[a-zA-Z0-9]+)\s?', value)
    #if (len(imgs) > 0):
    #    for img in imgs:
    #        img_id = re.findall('http://cl.ly/([a-zA-Z0-9]+)', img)
    #        if (img_id[0] != 'demo' and img_id[0] != 'whatever'):
    #            value = value.replace('http://cl.ly/' + img_id[0], '<a href="http://cl.ly/' + img_id[0] + '" target="_blank"><img src="http://cl.ly/' + img_id[0] + '/content" class="imgly" border="0" /></a>')
    #    return value
    #else:
    #    return value
    return value


# auto convert *.sinaimg.cn/*/*.jpg and bcs.baidu.com/*.jpg links to image tags
def sinaimg(value):
    imgs = re.findall('(http://ww[0-9]{1}.sinaimg.cn/[a-zA-Z0-9]+/[a-zA-Z0-9]+.[a-z]{3})\s?', value)
    for img in imgs:
        value = value.replace(img, '<a href="' + img + '" target="_blank"><img src="' + img + '" class="imgly" border="0" /></a>')
    baidu_imgs = re.findall('(http://(bcs.duapp.com|img.xiachufang.com|i.xiachufang.com)/([a-zA-Z0-9\.\-\_\/]+).jpg)\s?', value)
    for img in baidu_imgs:
        value = value.replace(img[0], '<a href="' + img[0] + '" target="_blank"><img src="' + img[0] + '" class="imgly" border="0" /></a>')
    return value


# auto convert youtube.com links to player
def youtube(value):
    videos = re.findall('(http://www.youtube.com/watch\?v=[a-zA-Z0-9\-\_]+)\s?', value)
    if (len(videos) > 0):
        for video in videos:
            video_id = re.findall('http://www.youtube.com/watch\?v=([a-zA-Z0-9\-\_]+)', video)
            value = value.replace('http://www.youtube.com/watch?v=' + video_id[0], '<object width="620" height="500"><param name="movie" value="http://www.youtube.com/v/' + video_id[0] + '?fs=1&amp;hl=en_US"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/' + video_id[0] + '?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="620" height="500"></embed></object>')
        return value
    else:
        return value


# auto convert youku.com links to player
# example: http://v.youku.com/v_show/id_XMjA1MDU2NTY0.html
def youku(value):
    videos = re.findall('(http://v.youku.com/v_show/id_[a-zA-Z0-9\=]+.html)\s?', value)
    logging.error(value)
    logging.error(videos)
    if (len(videos) > 0):
        for video in videos:
            video_id = re.findall('http://v.youku.com/v_show/id_([a-zA-Z0-9\=]+).html', video)
            value = value.replace('http://v.youku.com/v_show/id_' + video_id[0] + '.html', '<embed src="http://player.youku.com/player.php/sid/' + video_id[0] + '/v.swf" quality="high" width="638" height="420" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>')
        return value
    else:
        return value


# auto convert tudou.com links to player
# example: http://www.tudou.com/programs/view/ro1Yt1S75bA/
def tudou(value):
    videos = re.findall('(http://www.tudou.com/programs/view/[a-zA-Z0-9\=]+/)\s?', value)
    logging.error(value)
    logging.error(videos)
    if (len(videos) > 0):
        for video in videos:
            video_id = re.findall('http://www.tudou.com/programs/view/([a-zA-Z0-9\=]+)/', video)
            value = value.replace('http://www.tudou.com/programs/view/' + video_id[0] + '/', '<embed src="http://www.tudou.com/v/' + video_id[0] + '/" quality="high" width="638" height="420" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>')
        return value
    else:
        return value


# auto convert @username to clickable links
def mentions(value):
    ms = re.findall('(@[a-zA-Z0-9\_]+\.?)\s?', value)
    if (len(ms) > 0):
        for m in ms:
            m_id = re.findall('@([a-zA-Z0-9\_]+\.?)', m)
            if (len(m_id) > 0):
                if (m_id[0].endswith('.') != True):
                    value = value.replace('@' + m_id[0], '@<a href="/member/' + m_id[0] + '">' + m_id[0] + '</a>')
        return value
    else:
        return value


# gravatar filter
def gravatar(value,arg):
    default = "http://v2ex.appspot.com/static/img/avatar_" + str(arg) + ".png"
    if type(value).__name__ != 'Member':
        return '<img src="' + default + '" border="0" align="absmiddle" />'
    if arg == 'large':
        number_size = 73
        member_avatar_url = value.avatar_large_url
    elif arg == 'normal':
        number_size = 48
        member_avatar_url = value.avatar_normal_url
    elif arg == 'mini':
        number_size = 24
        member_avatar_url = value.avatar_mini_url
        
    if member_avatar_url:
        return '<img src="'+ member_avatar_url +'" border="0" alt="' + value.username + '" />'
    else:
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(value.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'s' : str(number_size), 'd' : default})
        return '<img src="' + gravatar_url + '" border="0" alt="' + value.username + '" align="absmiddle" />'


# avatar filter
def avatar(value, arg):
    default = "/static/img/avatar_" + str(arg) + ".png"
    if type(value).__name__ not in ['Member', 'Node']:
        return '<img src="' + default + '" border="0" />'
    if arg == 'large':
        number_size = 73
        member_avatar_url = value.avatar_large_url
    elif arg == 'normal':
        number_size = 48
        member_avatar_url = value.avatar_normal_url
    elif arg == 'mini':
        number_size = 24
        member_avatar_url = value.avatar_mini_url
        
    if value.avatar_mini_url:
        return '<img src="'+ member_avatar_url +'" border="0" />'
    else:
        return '<img src="' + default + '" border="0" />'


# github gist script support
def gist(value):
    return re.sub(r'(http://gist.github.com/[\d]+)', r'<script src="\1.js"></script>', value)


_base_js_escapes = (
    ('\\', r'\u005C'),
    ('\'', r'\u0027'),
    ('"', r'\u0022'),
    ('>', r'\u003E'),
    ('<', r'\u003C'),
    ('&', r'\u0026'),
    ('=', r'\u003D'),
    ('-', r'\u002D'),
    (';', r'\u003B'),
    (u'\u2028', r'\u2028'),
    (u'\u2029', r'\u2029')
)

# Escape every ASCII character with a value less than 32.
_js_escapes = (_base_js_escapes +
               tuple([('%c' % z, '\\u%04X' % z) for z in range(32)]))

def escapejs(value):
    """Hex encodes characters for use in JavaScript strings."""
    for bad, good in _js_escapes:
        value = value.replace(bad, good)
    return value



def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.

    The concept is defined in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None

# add from https://github.com/angelbot/geoincentives/blob/7b156fc0d223a1e9376e83651c7c8ad5deaa2b0f/coffin/template/defaultfilters.py
TIMESINCE_CHUNKS = (
    (60 * 60 * 24 * 365, ('%d year', '%d years')),
    (60 * 60 * 24 * 30, ('%d month', '%d months')),
    (60 * 60 * 24 * 7, ('%d week', '%d weeks')),
    (60 * 60 * 24, ('%d day', '%d days')),
    (60 * 60, ('%d hour', '%d hours')),
    (60, ('%d minute', '%d minutes'))
)

def avoid_wrapping(value):
    """
    Avoid text wrapping in the middle of a phrase by adding non-breaking
    spaces where there previously were normal spaces.
    """
    return value.replace(" ", "\xa0")

def timesince2(d, now=None, reversed=False):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.
    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.
    Adapted from
    http://web.archive.org/web/20060617175230/http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now(pytz.utc if is_aware(d) else None)

    delta = (d - now) if reversed else (now - d)

    # Deal with leapyears by subtracing the number of leapdays
    delta -= datetime.timedelta(calendar.leapdays(d.year, now.year))

    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return avoid_wrapping(('0 minutes'))
    for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):
        count = since // seconds
        if count != 0:
            break
    result = avoid_wrapping(name % count)
    if i + 1 < len(TIMESINCE_CHUNKS):
        # Now get the second item
        seconds2, name2 = TIMESINCE_CHUNKS[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result += (', ') + avoid_wrapping(name2 % count2)
    return result


def timesince(d):

    time1 = datetime.datetime.utcnow()
    format = '%Y-%m-%d %H:%M:%S'
    delta = time1 - d.replace(tzinfo=None)
    before = delta.days * 24 * 60 * 60 + delta.seconds
    if before <= 60:
        return 'just now'
    else:
        return datetime.timedelta(seconds=before)



def timeuntil(d, now=None):
    """
    Like timesince, but returns a string measuring the time until
    the given time.
    """
    return timesince2(d, now, reversed=True)


def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    return s

re_newlines = re.compile(r'\r\n|\r')  # Used in normalize_newlines

def normalize_newlines(text):
    """Normalizes CRLF and CR newlines to just LF."""
    text = force_text(text)
    return re_newlines.sub('\n', text)


def escape(text):
    """
    Returns the given text with ampersands, quotes and angle brackets encoded
    for use in HTML.

    This function always escapes its input, even if it's already escaped and
    marked as such. This may result in double-escaping. If this is a concern,
    use conditional_escape() instead.
    """
    return force_text(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;').replace(' ', '&nbsp;')

def linebreaksbr(value, autoescape=True):
    """
    Converts all newlines in a piece of plain text to HTML line breaks
    (``<br />``).
    """
    value = normalize_newlines(value)
    if autoescape:
        value = escape(value)
    return (value.replace('\n', '<br />'))
    #return value


def date(value, fmt=None):
    date = dateutil.parser.parse(str(value))
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format) 


def divisibleby(value, num):
    """Check if a variable is divisible by a number."""
    return value % num == 0

