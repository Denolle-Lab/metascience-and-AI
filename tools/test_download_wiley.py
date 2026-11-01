"""Offline checks. Run: python3 -m unittest -v test_download_wiley.py"""

import contextlib
from email.message import Message
from http.client import IncompleteRead
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

import download_wiley as dw


PDF = b"%PDF-1.7\nmock PDF bytes for transport tests\n%%EOF\n"


class Response(io.BytesIO):
    status = 200

    def __init__(self, body=PDF, length=None):
        super().__init__(body)
        self.headers = Message()
        self.headers["Content-Length"] = str(len(body) if length is None else length)


class DownloaderChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.limiter = Mock()

    def tearDown(self):
        self.temp.cleanup()

    def download(self, opener, **kwargs):
        return dw.download_pdf("10.1002/example/x", self.folder, "secret-token",
                               opener, self.limiter, **kwargs)

    def test_txt_urls_encoded_slashes_and_case_deduplicate(self):
        source = self.folder / "dois.txt"
        source.write_text("# comment\nhttps://doi.org/10.1002/ABC%2Fx\ndoi:10.1002/abc/x\n")
        self.assertEqual(dw.read_dois(source), ["10.1002/abc/x"])

    def test_csv_with_bom_and_other_columns(self):
        source = self.folder / "dois.csv"
        source.write_text('\ufeffTitle,DOI\n"A title, with comma",10.1111/test\n', encoding="utf-8")
        self.assertEqual(dw.read_dois(source), ["10.1111/test"])

    def test_invalid_input_prevents_requests(self):
        source = self.folder / "dois.txt"
        source.write_text("10.1111/good\nnot a doi\n")
        with self.assertRaisesRegex(ValueError, "line 2"):
            dw.read_dois(source)

    def test_success_encodes_doi_and_authenticates_only_initial_request(self):
        opener = Mock()
        opener.open.return_value = Response()
        result = self.download(opener)
        self.assertEqual(result["status"], "downloaded")
        self.assertEqual(Path(result["path"]).read_bytes(), PDF)
        request = opener.open.call_args.args[0]
        self.assertTrue(request.full_url.endswith("10.1002%2Fexample%2Fx"))
        self.assertEqual(request.get_header("Wiley-tdm-client-token"), "secret-token")
        redirected = dw.SafeRedirects().redirect_request(
            request, None, 302, "Found", {}, "https://download.wiley.com/resource")
        self.assertIsNone(redirected.get_header("Wiley-tdm-client-token"))
        self.assertNotIn("secret-token", str(result))

    def test_redirect_refuses_http(self):
        with self.assertRaises(URLError):
            dw.SafeRedirects().redirect_request(
                Request(dw.API + "10.1002%2Fx"), None, 302, "Found", {}, "http://example.org/file")

    def test_html_response_is_not_saved_as_pdf(self):
        opener = Mock()
        opener.open.return_value = Response(b"<html>Access denied</html>")
        result = self.download(opener)
        self.assertEqual(result["status"], "failed")
        self.assertFalse(list(self.folder.iterdir()))

    def test_resume_skips_existing_pdf_without_any_request(self):
        dw.pdf_path(self.folder, "10.1002/example/x").write_bytes(PDF)
        opener = Mock()
        result = self.download(opener)
        self.assertEqual(result["status"], "existing")
        opener.open.assert_not_called()
        self.limiter.wait.assert_not_called()

    def test_short_body_retried_and_partial_removed(self):
        opener = Mock()
        opener.open.side_effect = [Response(length=len(PDF) + 20), Response()]
        with patch.object(dw.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
            result = self.download(opener, retries=1)
        self.assertEqual(result["status"], "downloaded")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(self.limiter.wait.call_count, 2)
        self.assertFalse(list(self.folder.glob("*.part")))

    def test_429_honors_retry_after_and_never_logs_response_body(self):
        headers = Message()
        headers["Retry-After"] = "650"
        error = HTTPError(dw.API, 429, "secret-token", headers, io.BytesIO(b"secret-token"))
        opener = Mock()
        opener.open.side_effect = [error, Response()]
        with patch.object(dw.time, "sleep") as sleep, contextlib.redirect_stdout(io.StringIO()):
            result = self.download(opener, retries=1)
        sleep.assert_called_once_with(650)
        self.assertEqual(result["status"], "downloaded")
        self.assertNotIn("secret-token", str(result))
        self.assertEqual(dw.retry_delay({}, 1, 429), 600)

    def test_auth_failure_is_not_retried(self):
        opener = Mock()
        opener.open.side_effect = HTTPError(dw.API, 403, "Forbidden", Message(), io.BytesIO())
        result = self.download(opener)
        self.assertEqual(result["http_status"], 403)
        self.assertEqual(opener.open.call_count, 1)

    def test_interrupted_read_removes_partial(self):
        response = Response()
        real_read = response.read
        response.read = Mock(side_effect=[real_read(1024), KeyboardInterrupt()])
        opener = Mock()
        opener.open.return_value = response
        with self.assertRaises(KeyboardInterrupt):
            self.download(opener)
        self.assertFalse(list(self.folder.iterdir()))

    def test_rate_limiter_spaces_attempts(self):
        limiter = dw.RateLimiter(10.1)
        with patch.object(dw.time, "monotonic", side_effect=[100, 100, 104, 110.1]), \
             patch.object(dw.time, "sleep") as sleep:
            limiter.wait()
            limiter.wait()
        self.assertAlmostEqual(sleep.call_args.args[0], 6.1)

    def test_dry_run_needs_no_token_and_creates_no_downloads(self):
        source = self.folder / "dois.txt"
        source.write_text("10.1111/test\n")
        destination = self.folder / "output"
        with patch.dict(dw.os.environ, {}, clear=True), \
             patch.object(dw.getpass, "getpass") as prompt, \
             patch.object(dw, "build_opener") as network, \
             contextlib.redirect_stdout(io.StringIO()):
            code = dw.main([str(source), "--output", str(destination), "--dry-run"])
        self.assertEqual(code, 0)
        prompt.assert_not_called()
        network.assert_not_called()
        self.assertFalse(destination.exists())

    def test_batch_logs_success_and_missing_article_then_resumes(self):
        source = self.folder / "dois.txt"
        source.write_text("10.1111/one\n10.1111/two\n")
        output = self.folder / "downloads"
        opener = Mock()
        opener.open.side_effect = [Response(), HTTPError(dw.API, 404, "Missing", Message(), io.BytesIO())]
        with patch.dict(dw.os.environ, {"WILEY_TDM_TOKEN": "secret-token"}), \
             patch.object(dw, "build_opener", return_value=opener), \
             patch.object(dw.RateLimiter, "wait"), \
             contextlib.redirect_stdout(io.StringIO()):
            code = dw.main([str(source), "--output", str(output)])
            self.assertEqual(code, 1)
            opener.open.side_effect = [Response()]
            self.assertEqual(dw.main([str(source), "--output", str(output)]), 0)
        with (output / "results.csv").open(newline="") as handle:
            rows = list(dw.csv.DictReader(handle))
        self.assertEqual([row["status"] for row in rows],
                         ["downloaded", "failed", "existing", "downloaded"])
        self.assertEqual(opener.open.call_count, 3)
        self.assertNotIn("secret-token", (output / "results.csv").read_text())

    def test_batch_stops_after_invalid_token(self):
        source = self.folder / "dois.txt"
        source.write_text("10.1111/one\n10.1111/two\n")
        opener = Mock()
        opener.open.side_effect = HTTPError(dw.API, 403, "Forbidden", Message(), io.BytesIO())
        with patch.dict(dw.os.environ, {"WILEY_TDM_TOKEN": "secret-token"}), \
             patch.object(dw, "build_opener", return_value=opener), \
             patch.object(dw.RateLimiter, "wait"), \
             contextlib.redirect_stdout(io.StringIO()):
            code = dw.main([str(source), "--output", str(self.folder / "output")])
        self.assertEqual(code, 1)
        opener.open.assert_called_once()


if __name__ == "__main__":
    unittest.main()
