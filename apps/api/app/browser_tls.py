"""Route pytubefix requests through curl_cffi with browser TLS impersonation.

YouTube drops TLS handshakes that look like scripting tools (python-urllib),
which makes pytubefix fail with URLError "EOF occurred in violation of
protocol" or BotDetection. Sending the same requests with a Chrome TLS
fingerprint gets through. Apply before importing/using pytubefix.
"""
import email.message
import json
import socket

from curl_cffi import requests as browser_requests

IMPERSONATE = "chrome"
DEFAULT_TIMEOUT = 30


class _ResponseAdapter:
    def __init__(self, response):
        self._response = response
        self._content = response.content
        self._pos = 0
        self.status = response.status_code
        self.url = response.url

    def read(self, size=-1):
        if size is None or size < 0:
            size = len(self._content) - self._pos
        chunk = self._content[self._pos:self._pos + size]
        self._pos += len(chunk)
        return chunk

    def info(self):
        msg = email.message.Message()
        for name, value in self._response.headers.items():
            msg[name] = value
        return msg

    def getcode(self):
        return self.status

    def close(self):
        self._response.close()


def apply():
    from pytubefix import request as pytubefix_request
    from pytubefix import innertube as pytubefix_innertube

    def _execute_request(url, method=None, headers=None, data=None,
                         timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        base_headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}
        if headers:
            base_headers.update(headers)
        if data is not None and not isinstance(data, bytes):
            data = bytes(json.dumps(data), encoding="utf-8")
        if not url.lower().startswith("http"):
            raise ValueError("Invalid URL")

        if url.startswith("https://youtube.com/"):
            url = "https://www.youtube.com/" + url[len("https://youtube.com/"):]

        if timeout is socket._GLOBAL_DEFAULT_TIMEOUT:
            timeout = DEFAULT_TIMEOUT

        response = browser_requests.request(
            method=method or ("POST" if data is not None else "GET"),
            url=url,
            headers=base_headers,
            data=data,
            timeout=timeout,
            impersonate=IMPERSONATE,
        )
        return _ResponseAdapter(response)

    pytubefix_request._execute_request = _execute_request

    pytubefix_innertube.InnerTube.base_url = property(
        lambda self: "https://youtubei.googleapis.com/youtubei/v1"
    )
