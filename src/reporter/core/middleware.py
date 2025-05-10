import re

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin


class ReporterSecurityMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.redirect = settings.SECURE_SSL_REDIRECT
        self.redirect_host = settings.SECURE_SSL_HOST
        self.redirect_exempt = [re.compile(r) for r in settings.SECURE_REDIRECT_EXEMPT]

    def process_request(self, request):
        path = request.path.lstrip("/")
        if (
            self.redirect
            and not request.is_secure()
            and not any(pattern.search(path) for pattern in self.redirect_exempt)
            and not request.method == "POST"
        ):
            host = self.redirect_host or request.get_host()
            return HttpResponsePermanentRedirect(
                "https://%s%s" % (host, request.get_full_path())
            )
        return None


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
        return cls.RE_MULTI_BREAK.sub(b"\n", content)
