duckduckgo2html
===============

Python 3 library to retrieve results from the
[DuckDuckGo zero-click API](https://api.duckduckgo.com) in simple HTML format.

Use examples
------------

###### Retrieving html from a query result

```python
import duckduckgo2html

results = duckduckgo2html.search("DuckDuckGo")
html = duckduckgo2html.results2html(results)
```

```html
<div>
  <h1>Abstract</h1>
  <p><b>DuckDuckGo</b> - DuckDuckGo is an Internet search engine that emphasizes protecting searchers' privacy and avoiding the filter bubble of personalized search results. DuckDuckGo distinguishes itself from other search engines by not profiling its users and by deliberately showing all users the same search results for a given search term. DuckDuckGo emphasizes returning the best results, rather than the most results, and generates those results from over 400 individual sources, including key crowdsourced sites such as Wikipedia, and other search engines like Bing, Yahoo!, Yandex, and Yummly. - <a href="https://en.wikipedia.org/wiki/DuckDuckGo">Wikipedia</a></p>
  <h1>Results</h1>
  <p><a href="https://duckduckgo.com/">Official site</a> <a href="https://duckduckgo.com/"/> </p>
  <h1>Infobox</h1>
  <p><b>Type of site</b> Web search engine<br/><b>Owner</b> Duck Duck Go, Inc.<br/><b>Created by</b> Gabriel Weinberg<br/><b>Launched</b> September 25, 2008<br/><b>Alexa rank</b> 468 (June 10, 2017)</p>
  <footer>
    <small>Results from DuckDuckGo</small>
  </footer>
</div>
```

###### Striping out just the answer

```python
duckduckgo2html.results2html(
    duckduckgo2html.search("sunrise"),
    section_priority=["answer"],
    hide_headers=True,
    hide_footer=True))
```

```html
<p>On 16 Jun 2017, sunrise in Barcelona, Catalonia is at 6:17 AM; sunset at 9:27 PM</p>
```

###### Command-line usage

```
$ ./duckduckgo2html.py --pretty-print query
```

API
---

```python
duckduckgo2html.results2html(
    results,                     # Results of a query.
    section_priority=None,       # List of section names to be displayed in the given order
    max_number_of_sections=None, # Maximum number of sections to be displayed
    ignore_incomplete=True,      # Ignore incomplete sections
    always_show_related=False,   # Always show "Related topics" section
    header_start_level=1,        # Level to start the html header hierarchy
    hide_headers=False,          # Hide html headers
    hide_footer=False)           # Hide "Results from DuckDuckGo" footer
```

Default section names priority: answer, abstract, definition, results, infobox,
redirect, related.

Licence
-------

`duckduckgo.py` is a modification (ported to Python 3) of the duckduckgo module
of [ddg](https://github.com/jshrake/ddg) by Justin Shrake.

Which is a modification from http://github.com/crazedpsyc/python-duckduckgo.

Which is a modification of the original duckduckgo module from
http://github.com/mikejs/python-duckduckgo by Michael Stephens <me@mikej.st>,
released under a BSD-style license.
