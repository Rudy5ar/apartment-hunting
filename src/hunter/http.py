import http.client
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

_read_status = http.client.HTTPResponse._read_status


def _read_status_skip_early_hints(self):
    line, status, reason = _read_status(self)
    while status == 103:
        while True:
            header = self.fp.readline(http.client._MAXLINE + 1)
            if header in (b"\r\n", b"\n", b""):
                break
        line, status, reason = _read_status(self)
    return line, status, reason


http.client.HTTPResponse._read_status = _read_status_skip_early_hints

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)


def get_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "sr-RS,sr;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="replace")
