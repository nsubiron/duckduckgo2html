"""Retrieve results from the DuckDuckGo zero-click API in simple HTML format"""

import json as jsonlib
import re
import urllib.request, urllib.error, urllib.parse


def results2html(results, results_priority=None, max_number_of_results=None,
                 ignore_incomplete=False, always_show_related=False,
                 header_start_level=1, hide_headers=False, hide_signature=False):
    if not results:
        return 'Sorry, no results found'

    if not results_priority:
        results_priority = ['answer', 'abstract', 'definition', 'results',
                            'redirect', 'related']

    if not always_show_related:
        other = [x for x in results_priority if x != 'related']
        if any(results.get(x).is_complete() for x in other):
            results_priority = other

    html_header = '<h{level:d}>{title}</h{level:d}>'
    html_paragraph = '<p>{contents}</p>'

    html_contents = []
    children = [results.get(x) for x in results_priority]
    results_count = 0
    for level, child in _iterchildren(header_start_level, children):
        html = child.as_html()
        valid = html and (not ignore_incomplete or child.is_complete())
        if not hide_headers and child.name and (valid or child.children()):
            header = html_header.format(title=child.name, level=level)
            html_contents.append(header)
        if valid:
            html_contents.append(html_paragraph.format(contents=html))
            results_count += 1
            if max_number_of_results and results_count >= max_number_of_results:
                break

    html_contents[:] = [x for x in html_contents if x]
    if not html_contents:
        return 'Sorry, no results found'

    if not hide_signature:
        html_contents.append('<footer><small>Results from DuckDuckGo</small></footer>')

    return ''.join(html_contents).strip()


def search(query, useragent='duckduckgo2html', **kwargs):
    params = {
        'q': query,
        'format': 'json',
        'pretty': '1',
        'no_redirect': '1',
        'no_html': '1',
        'skip_disambig': '0',
        }
    params.update(kwargs)
    enc_params = urllib.parse.urlencode(params)
    url = 'http://api.duckduckgo.com/?' + enc_params

    try:
        request = urllib.request.Request(url, headers={'User-Agent': useragent})
        response = urllib.request.urlopen(request)
        json = jsonlib.loads(response.read().decode('utf-8'))
        response.close()
        return Results(json)
    except urllib.error.HTTPError as err:
        print('Query failed with HTTPError code ' + str(err.code))
    except urllib.error.URLError as err:
        print('Query failed with URLError ' + str(err.reason))
    except Exception:
        print('Unhandled exception')
        raise
    return None


def _iterchildren(start_level, children):
    for item in children:
        grandchildren = item.children()
        yield start_level, item
        if grandchildren:
            for subitem in _iterchildren(start_level+1, grandchildren):
                yield subitem


def _html_url(url, display=None):
    if not display:
        display = url
    return '<a href="{0}">{1}</a>'.format(url, display)


class Results(object):
    def __init__(self, json):
        self.json = jsonlib.dumps(json, indent=2)
        self.type = json.get('Type')
        self.answer = Answer(json)
        self.results = _ResultList('Results', json.get('Results', []))
        self.related = _ResultList('Related Topics', json.get('RelatedTopics', []))
        self.abstract = Abstract(json)
        self.definition = Definition(json)
        self.redirect = Redirect(json)

    def get(self, name):
        if hasattr(self, name) and getattr(self, name):
            return getattr(self, name)
        return _ResultItemBase()


class _ResultItemBase(object):
    """Base class for results"""

    def __init__(self, name=None):
        self.name = name

    def is_complete(self):
        return False

    def children(self):
        return []

    def as_html(self):
        return ''


class _ResultList(_ResultItemBase):
    """A list of results"""

    def __init__(self, name, items):
        super().__init__(name)
        self.items = [Result(x) for x in items]
        print('Created list %r with %i children.' % (name, len(self.items)))

    def children(self):
        return self.items


class Result(_ResultItemBase):
    def __init__(self, json):
        super().__init__(json.get('Name', '') if json else '')
        self.topics = [Result(elem) for elem in json.get('Topics', [])]
        self.html = json.get('Result', '') if json else ''
        self.text = json.get('Text', '') if json else ''
        self.url = json.get('FirstURL', '') if json else ''

    def is_complete(self):
        return True if self.text else False

    def children(self):
        return self.topics

    def as_html(self):
        if self.html:
            return Result._rex_sub.sub('a> ', self.html)
        elif self.text:
            return self.text

    _rex_sub = re.compile(r'a>(?! )')


class Abstract(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Abstract')
        self.html = json['Abstract']
        self.text = json['AbstractText']
        self.url = json['AbstractURL']
        self.source = json['AbstractSource']
        self.heading = json['Heading']

    def is_complete(self):
        return True if self.html or self.text else False

    def as_html(self):
        html_list = []
        if self.heading:
            html_list.append('<b>{0}</b>'.format(self.heading))
        if self.html:
            html_list.append(self.html)
        elif self.text:
            html_list.append(self.text)
        if self.url:
            html_list.append(_html_url(self.url, self.source))
        return ' - '.join(html_list)


class Answer(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Answer')
        self.text = json['Answer']
        self.type = json['AnswerType']
        self.url = None

    def is_complete(self):
        return True if self.text else False

    def as_html(self):
        return self.text


class Definition(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Definition')
        self.text = json['Definition']
        self.url = json['DefinitionURL']
        self.source = json['DefinitionSource']

    def is_complete(self):
        return True if self.text else False

    def as_html(self):
        if self.text and self.url:
            return self.text + ' - ' + _html_url(self.url, self.source)
        elif self.text:
            return self.text
        elif self.url:
            return _html_url(self.url, self.source)


class Redirect(_ResultItemBase):
    def __init__(self, json):
        super().__init__('Redirect')
        self.url = json['Redirect']

    def as_html(self):
        return _html_url(self.url) if self.url else None