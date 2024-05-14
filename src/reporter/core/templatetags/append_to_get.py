"""
Append parameters to a GET querystring (template tag)

This tag is designed to facilitate pagination in the case where both the page
number and other parameters (eg. search criteria) are passed via GET.

It takes one argument - a dictionary of GET variables to be added to the
current url

Example usage:

  {% for page_num in results.paginator.page_range %}
  <a href="{% append_to_get p=page_num %}">{{ page_num }}</a>
  {% endfor %}

Note that the passed arguments are evaluated within the template context.

see also: http://djangosnippets.org/snippets/1627/
"""

from django import template

register = template.Library()


def easy_tag(func):
    """
    Decorator to facilitate template tag creation
    deal with the repetitive parts of parsing template tags
    """

    def inner(parser, token):
        # print token
        try:
            return func(*token.split_contents())
        except TypeError:
            raise template.TemplateSyntaxError(
                'Bad arguments for tag "%s"' % token.split_contents()[0]
            )

    inner.__name__ = func.__name__
    inner.__doc__ = inner.__doc__
    return inner


class AppendGetNode(template.Node):
    def __init__(self, adict):
        self.dict_pairs = {}
        for pair in adict.split(","):
            pair = pair.split("=")
            self.dict_pairs[pair[0]] = template.Variable(pair[1])

    def render(self, context):
        get = context["request"].GET.copy()

        for key in self.dict_pairs:
            get[key] = self.dict_pairs[key].resolve(context)

        path = context["request"].META["PATH_INFO"]

        if len(get):
            path += "?%s" % "&amp;".join(
                [f"{key}={value}" for (key, value) in get.items() if value]
            )

        return path


@register.tag()
@easy_tag
def append_to_get(_tag_name, adict):
    return AppendGetNode(adict)
