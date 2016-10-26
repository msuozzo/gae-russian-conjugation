from __future__ import print_function

import os
import re
import urllib2
import urlparse

from google.appengine.ext import vendor
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))

import BeautifulSoup as bs


_CAPTURE_REGEXES = [
        r'1st singular',
        r'2nd singular',
        r'3rd plural',
        r'masculine',
        r'feminine']
_CAPTURE_REGEX_TEXT = '|'.join(
        '({})'.format(regex) for regex in _CAPTURE_REGEXES)
_CAPTURE_REGEX = re.compile(_CAPTURE_REGEX_TEXT)


def _UrlEncodeNonAscii(b):
    return re.sub('[\x80-\xff]', lambda c: '%%%02x' % ord(c.group(0)), b)


def _IriToUri(iri):
    """Converts an IRI to a URI."""
    parts = urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else _UrlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts))


def _GetStrings(elem):
    ret = []
    for child in elem.contents:
        if isinstance(child, basestring):
            ret.append(child)
        else:
            ret.extend(_GetStrings(child))
    return ret


def GetConjugationTable(word):
    """Returns the conjugation table for a Russian verb.

    Args:
        word: unicode, The UTF-8 encoded Russian verb to be conjugated.

    Returns:
        A list of 2-tuples of the form (verb_form, conjugation) filtered to
        those verb forms matching _CAPTURE_REGEXES.
    """
    url = u'https://en.wiktionary.org/wiki/{}'.format(word)
    url = _IriToUri(url)
    response = urllib2.urlopen(url)

    content = response.read()

    soup = bs.BeautifulSoup(content)
    elem = soup.findAll('div', 'NavContent')[0]
    rows = []
    for row in elem.findAll('tr')[1:]:
        new_row = []

        header = row.findAll('th')[0]
        labels = _GetStrings(header)
        if not labels: continue

        parts = filter(None, map(lambda s: s.strip(), labels))
        if parts:
            try:
                label = parts[parts.index('(') + 1]
            except ValueError:
                label = ' '.join(parts)
        else:
            label = ''
        if not _CAPTURE_REGEX.findall(label): continue
        new_row.append(label)

        for col in row.findAll('td')[:1]:
            spans = col.findAll('span')
            if not spans: continue

            label = _GetStrings(spans[0])[0]
            if not label: continue
            new_row.append(label)
        if len(new_row) < 2:
            new_row.append('')
        rows.append(new_row)
    return rows
