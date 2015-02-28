"""python wrapper for the duck duck go zero-click api"""

import json as jsonlib
import re
import urllib.request, urllib.error, urllib.parse


def get_as_html_list(query, useragent, results_priority):
    results = search(query, useragent)

    if not results:
        return []

    output_items = []
    rex_list = re.compile(r'(results|related).([0-9]+)')
    for item in results_priority:
        match_list = rex_list.match(item)
        if match_list is not None:
            elements = getattr(results, match_list.group(1))
            index = int(match_list.group(2))
            if index < len(elements):
                result = elements[index]
                output_items.append((item, result.as_html()))
        elif hasattr(results, item) and getattr(results, item):
            output_items.append((item, getattr(results, item).as_html()))

    return [x for x in output_items if x[1]]


def search(query, useragent, **kwargs):
    params = {
        'q': query,
        'format': 'json',
        'pretty': '1',
        'no_redirect': '1',
        'no_html': '1',
        'skip_disambig': '1',
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


def html_url(url, display=None):
    if not display:
        display = url
    return '<a href="{0}">{1}</a>'.format(url, display)


class Results(object):
    def __init__(self, json):
        self.json = jsonlib.dumps(json, indent=2)
        self.type = {'A': 'article', 'D': 'disambiguation',
                     'C': 'category', 'N': 'name',
                     'E': 'exclusive', '': 'nothing'}[json['Type']]
        self.answer = Answer(json)
        self.results = [Result(elem) for elem in json.get('Results', [])]
        self.related = [Result(elem) for elem in json.get('RelatedTopics', [])]
        self.abstract = Abstract(json)
        self.definition = Definition(json)
        self.redirect = Redirect(json)


class Result(object):
    def __init__(self, json):
        self.html = json.get('Result', '') if json else ''
        self.text = json.get('Text', '') if json else ''
        self.url = json.get('FirstURL', '') if json else ''

        self.name = json.get('Name', '') if json else ''
        self.topics = [Result(elem) for elem in json.get('Topics', [])]

    def as_html(self):
        html = ''
        if self.html:
            html = Result._rex_sub.sub('a> ', self.html)
        elif self.text:
            html = self.text
        if self.name and self.topics:
            html_topics = [x.as_html() for x in self.topics]
            html_topics = [x for x in html_topics if x]
            if html_topics:
                html += '<h2>{0}</h2>'.format(self.name)
                html += '<br>'.join(html_topics)
        return html

    _rex_sub = re.compile(r'a>(?! )')


class Abstract(object):
    def __init__(self, json):
        self.html = json['Abstract']
        self.text = json['AbstractText']
        self.url = json['AbstractURL']
        self.source = json['AbstractSource']
        self.heading = json['Heading']

    def as_html(self):
        html_list = []
        if self.heading:
            html_list.append('<b>{0}</b>'.format(self.heading))
        if self.html:
            html_list.append(self.html)
        elif self.text:
            html_list.append(self.text)
        if self.url:
            html_list.append(html_url(self.url, self.source))
        return ' - '.join(html_list)


class Answer(object):
    def __init__(self, json):
        self.text = json['Answer']
        self.type = json['AnswerType']
        self.url = None

    def as_html(self):
        if not self.text:
            return None
        html = self.text
        if self.type:
            html = '<b>[{0}]</b> {1}'.format(self.type, html)
        return html


class Definition(object):
    def __init__(self, json):
        self.text = json['Definition']
        self.url = json['DefinitionURL']
        self.source = json['DefinitionSource']

    def as_html(self):
        if self.text and self.url:
            return self.text + ' - ' + html_url(self.url, self.source)
        elif self.text:
            return self.text
        elif self.url:
            return html_url(self.url, self.source)


class Redirect(object):
    def __init__(self, json):
        self.url = json['Redirect']

    def as_html(self):
        return html_url(self.url) if self.url else None
