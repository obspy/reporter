import re


class MinifyHTMLMiddleware:
    """
    Minifies HTML content - does not respect <code>, <textarea> or <pre> tags!
    """

    RE_MULTI_SPACE = re.compile(b"[ ]{2,}")
    RE_MULTI_BREAK = re.compile(b"[\n]{2,}")
    RE_LEFT_SPACE = re.compile(b"\n[ ]+")
    RE_RIGHT_SPACE = re.compile(b"[ ]+\n")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_response(self, request, response):
        # skip admin pages
        if request.path.startswith("/admin"):
            return response
        # skip non-HTML pages
        content_type = response.get("content-type") or ""
        if not content_type.startswith("text/html"):
            return response
        # minimise
        response.content = self._minify_content(response.content)
        return response

    @classmethod
    def _minify_content(cls, content):
        content = cls.RE_LEFT_SPACE.sub(b"\n", content)
        content = cls.RE_RIGHT_SPACE.sub(b"\n", content)
        content = cls.RE_MULTI_SPACE.sub(b" ", content)
        content = cls.RE_MULTI_BREAK.sub(b"\n", content)
        return content
