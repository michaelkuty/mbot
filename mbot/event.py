
import logging
import re
from re import search

from slugify import slugify

LOG = logging.getLogger(__name__)


class Event:

    DEFAULT_PATTERN = r":\s?(\S*['-]*|\w*.+|'[^']+')"

    def __init__(self, bot, backend, body):

        self.bot = bot
        self.backend = backend
        self.body = body

    def __repr__(self):
        return "%s" % self.body

    @property
    def user(self):
        """Return user if is present in body"""
        return self.get("user", None)

    @property
    def text(self):
        """Return text if is present in body"""
        return self.get("text", None)

    def reply(self, *args, **kwargs):
        """Simple reply on message
        """
        return self.backend.reply(self, *args, **kwargs)

    def clean(self, value):
        return re.sub(r"”|“", '"', value)

    def reply_snippet(self, name, content=None, file=None, format="bash",
                      ext="sh"):

        kwargs = {
            'content': content,
            'filetype': format,
            'channels': self.body['channel'],
            'filename': '.'.join([slugify(name), ext]),
            'initial_comment': name,
            'title': slugify(name)
        }

        if file:
            kwargs['file'] = file

        return self.reply(name,
                          attachments=[kwargs])

    def get(self, key, default=None):
        return self.body.get(key, default)

    def extract_parameters(self, parameters=None, pattern=None, default=None):
        """Extract parameters from message

        TODO: valid required parameters with typo
        """
        params = {}

        for key in parameters or self.parameters:
            if isinstance(key, (tuple, list)) and len(key) > 1:
                _default = key[1]
                key = key[0]
            else:
                _default = default
            param, new_text = self._extract_from_text(key, self.text, pattern)
            params[key] = self.clean(param) if param else _default
            _default = default

        LOG.debug("Parsed parameters: %s from %s" % (params, self.text))

        return params

    def _extract_from_text(self, key, text=None, reg=None):
        """Find `key` in `query`, return its value and a new query w/out the key

        Case-insensitive, always returns lowercase values.
        """

        text = text or self.get("text", None)

        # match both `key: value` and `key: "value with spaces"`
        regex = key.lower() + (reg or self.DEFAULT_PATTERN)
        text = text.lower()
        match = search(regex, text)

        if match is None:
            return None, text

        value = match.group(1).strip('"')
        new_text = text[:match.start()] + text[match.end():]

        return value, new_text
