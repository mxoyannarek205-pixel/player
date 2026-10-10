"""Локальный сервер для сайта. Нужен, чтобы работали эквалайзер и реверберация."""
import os, re, sys, mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8765
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        if not m:
            return super().send_head()
        size = os.path.getsize(path)
        g1, g2 = m.groups()
        if g1 == "" and g2 != "":
            start, end = max(0, size - int(g2)), size - 1
        else:
            start = int(g1 or 0)
            end = int(g2) if g2 else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416)
            return None
        f = open(path, "rb")
        f.seek(start)
        self._left = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self._left))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        try:
            left = getattr(self, "_left", None)
            if left is None:
                return super().copyfile(source, outputfile)
            while left > 0:
                chunk = source.read(min(65536, left))
                if not chunk:
                    break
                outputfile.write(chunk)
                left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Сайт запущен: http://localhost:{PORT}/")
    print("Чтобы остановить, закрой это окно (или Ctrl+C).")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
