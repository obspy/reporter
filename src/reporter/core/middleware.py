# -*- coding: utf-8 -*-
"""
Custom middleware.
"""
import re


RE_MULTI_SPACE = re.compile(r"[ ]{2,}")
RE_MULTI_BREAK = re.compile(r"[\n]{2,}")
RE_LEFT_SPACE = re.compile(r"\n[ ]+")
RE_RIGHT_SPACE = re.compile(r"[ ]+\n")


class MinifyHTMLMiddleware(object):
    """
    Minifies HTML content - does not respect <code>, <textarea> or <pre> tags!
    """
    def process_response(self, request, response):  # @UnusedVariable
        # fix "Bad value X-UA-Compatible for attribute http-equiv" W3C
        response['X-UA-Compatible'] = 'IE=edge,chrome=1'
        # compress
        try:
            content_type = response['content-type']
        except:
            return response
        if 'text/html' in content_type:
            return self._minify(request, response)
        return response

    def _minify(self, request, response):  # @UnusedVariable
        response.content = RE_LEFT_SPACE.sub(r"\n", response.content)
        response.content = RE_RIGHT_SPACE.sub(r"\n", response.content)
        response.content = RE_MULTI_SPACE.sub(r" ", response.content)
        response.content = RE_MULTI_BREAK.sub(r"\n", response.content)
        return response
