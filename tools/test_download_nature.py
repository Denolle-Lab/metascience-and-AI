"""Offline Nature XML downloader checks; no keys or live network needed."""
import contextlib
from email.message import Message
from http.client import IncompleteRead
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request
import xml.etree.ElementTree as ET

import download_nature as dn

DOI = "10.1038/s41467-025-test"


def jats(doi=DOI, body=True, namespace=False):
    ns = ' xmlns="http://jats.nlm.nih.gov"' if namespace else ""
    fulltext = "<body><sec><title>Results</title><p>Full article text for transport tests.</p></sec></body>" if body else ""
    return (f'<article{ns} article-type="research-article"><front><article-meta>'
            f'<article-id pub-id-type="doi">{doi}</article-id></article-meta></front>'
            f'{fulltext}<back><ref-list/></back></article>').encode()


class Response(io.BytesIO):
    status = 200
    def __init__(self, body=None, length=None):
        body = body if body is not None else b"<response><records>" + jats() + b"</records></response>"
        super().__init__(body)
        self.headers = Message()
        self.headers["Content-Length"] = str(len(body) if length is None else length)


class NatureChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.limiter = Mock()

    def tearDown(self):
        self.temp.cleanup()

    def download(self, opener, budget=None, **kwargs):
        return dn.download_xml(DOI, self.folder, "oa", "secret-key", opener, self.limiter,
                               budget or dn.RequestBudget(450), **kwargs)

    def test_extracts_requested_fulltext_from_envelope_with_namespaces(self):
        payload = b'<response><query>secret-key</query><records>' + jats(namespace=True) + b'</records></response>'
        saved = dn.extract_article(payload, DOI)
        root = ET.fromstring(saved)
        self.assertEqual(dn.local_name(root), "article")
        self.assertNotIn(b"secret-key", saved)
        self.assertIn(b"Full article text", saved)

    def test_rejects_wrong_doi_even_if_requested_doi_in_reference(self):
        payload = jats("10.1038/other").replace(b"<ref-list/>", f'<ref-list><article-id pub-id-type="doi">{DOI}</article-id></ref-list>'.encode())
        with self.assertRaises(dn.ContentError):
            dn.extract_article(payload, DOI)

    def test_rejects_metadata_only_and_malformed_or_html_responses(self):
        for payload in [jats(body=False), b"<response><records/></response>", b"not xml", b"<html>Login</html>"]:
            with self.subTest(payload=payload), self.assertRaises(dn.ContentError):
                dn.extract_article(payload, DOI)

    def test_empty_results_are_unavailable_not_a_saved_xml(self):
        opener = Mock()
        opener.open.return_value = Response(b"<response><result><total>0</total></result><records/></response>")
        result = self.download(opener)
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(list(self.folder.iterdir()))

    def test_entity_declarations_rejected(self):
        with self.assertRaises(dn.ContentError):
            dn.extract_article(b'<!DOCTYPE article [<!ENTITY test "expanded">]>' + jats(), DOI)

    def test_success_requests_current_oa_endpoint_and_saves_article_only(self):
        opener = Mock()
        opener.open.return_value = Response()
        budget = dn.RequestBudget(5)
        result = self.download(opener, budget)
        req = opener.open.call_args.args[0]
        parsed = urlsplit(req.full_url)
        self.assertEqual(parsed.netloc, "api.springernature.com")
        self.assertEqual(parsed.path, "/openaccess/jats")
        self.assertEqual(parse_qs(parsed.query), {"q": ["doi:" + DOI], "p": ["1"], "s": ["1"], "api_key": ["secret-key"]})
        self.assertIn("TextDataMining", req.get_header("User-agent"))
        self.assertEqual(result["status"], "downloaded")
        self.assertTrue(dn.existing_article(Path(result["path"]), DOI))
        self.assertEqual(budget.used, 1)
        self.assertNotIn("secret-key", str(result))

    def test_resume_checks_actual_doi_and_body_before_skipping(self):
        path = dn.xml_path(self.folder, DOI)
        path.write_bytes(jats())
        opener = Mock()
        budget = dn.RequestBudget(1)
        result = self.download(opener, budget)
        self.assertEqual(result["status"], "existing")
        self.assertEqual(budget.used, 0)
        opener.open.assert_not_called()
        path.write_bytes(jats("10.1038/other"))
        opener.open.return_value = Response()
        self.assertEqual(self.download(opener)["status"], "downloaded")

    def test_429_retries_honor_wait_and_count_attempts(self):
        headers = Message()
        headers["Retry-After"] = "61"
        opener = Mock()
        opener.open.side_effect = [HTTPError("secret-key-in-url", 429, "Quota", headers, io.BytesIO()), Response()]
        budget = dn.RequestBudget(3)
        with patch.object(dn.time, "sleep") as sleep, contextlib.redirect_stdout(io.StringIO()):
            result = self.download(opener, budget, retries=1)
        self.assertEqual((result["status"], result["attempts"], budget.used), ("downloaded", 2, 2))
        sleep.assert_called_once_with(61)

    def test_request_budget_stops_retries_before_network(self):
        opener = Mock()
        opener.open.side_effect = URLError("secret-key-in-url")
        budget = dn.RequestBudget(1)
        with patch.object(dn.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
            result = self.download(opener, budget, retries=2)
        self.assertEqual(result["status"], "budget_exhausted")
        self.assertEqual(opener.open.call_count, 1)
        self.assertEqual(budget.used, 1)
        self.assertNotIn("secret-key", str(result))

    def test_incomplete_xml_retried_without_leaving_partial(self):
        opener = Mock()
        opener.open.side_effect = [Response(length=99999), Response()]
        with patch.object(dn.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
            result = self.download(opener, retries=1)
        self.assertEqual(result["status"], "downloaded")
        self.assertEqual(result["attempts"], 2)
        self.assertFalse(list(self.folder.glob("*.part")))

    def test_network_errors_never_log_secret_urls(self):
        opener = Mock()
        opener.open.side_effect = URLError("https://api.example?api_key=secret-key")
        result = self.download(opener, retries=0)
        self.assertEqual(result["status"], "failed")
        self.assertNotIn("secret-key", str(result))

    def test_refuses_redirects_to_keep_query_credentials_on_origin(self):
        with self.assertRaises(URLError):
            dn.NoRedirects().redirect_request(Request(dn.ENDPOINTS["oa"]), None, 302, "Found", {}, "https://elsewhere.example?api_key=secret-key")

    def test_tdm_credential_composition_and_whitespace_rejection(self):
        with patch.dict(dn.os.environ, {"SPRINGER_TDM_API_KEY": "key", "SPRINGER_TDM_METRIC": "metric"}, clear=True):
            self.assertEqual(dn.get_credential("tdm"), "key/metric")
        with patch.dict(dn.os.environ, {"SPRINGER_TDM_API_KEY": "bad credential"}, clear=True), self.assertRaises(ValueError):
            dn.get_credential("tdm")

    def test_csv_doi_urls_and_case_are_deduplicated(self):
        source = self.folder / "input.csv"
        source.write_text('\ufeffTitle,DOI\n"A, B",https://doi.org/10.1038/ABC%2Fx\nOther,doi:10.1038/abc/x\n')
        self.assertEqual(dn.read_dois(source), ["10.1038/abc/x"])

    def test_dry_run_no_key_no_network_no_output(self):
        source = self.folder / "dois.txt"
        source.write_text(DOI + "\n")
        output = self.folder / "out"
        with patch.object(dn, "get_credential") as key, patch.object(dn, "build_opener") as network, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dn.main([str(source), "--output", str(output), "--dry-run"]), 0)
        key.assert_not_called()
        network.assert_not_called()
        self.assertFalse(output.exists())

    def test_auth_failure_stops_batch_and_log_contains_no_credentials(self):
        source = self.folder / "dois.txt"
        source.write_text(DOI + "\n10.1038/another\n")
        opener = Mock()
        opener.open.side_effect = HTTPError("secret-key-url", 401, "Rejected", Message(), io.BytesIO())
        output = self.folder / "out"
        with patch.object(dn, "get_credential", return_value="secret-key"), patch.object(dn, "build_opener", return_value=opener), contextlib.redirect_stdout(io.StringIO()):
            result = dn.main([str(source), "--output", str(output)])
        self.assertEqual(result, 1)
        opener.open.assert_called_once()
        self.assertNotIn("secret-key", (output / "results.csv").read_text())

    def test_exhausted_429_stops_before_next_doi(self):
        source = self.folder / "dois.txt"
        source.write_text(DOI + "\n10.1038/another\n")
        opener = Mock()
        opener.open.side_effect = HTTPError("secret-key-url", 429, "Quota", Message(), io.BytesIO())
        with patch.object(dn, "get_credential", return_value="secret-key"), \
             patch.object(dn, "build_opener", return_value=opener), contextlib.redirect_stdout(io.StringIO()):
            result = dn.main([str(source), "--output", str(self.folder / "out"), "--retries", "0"])
        self.assertEqual(result, 1)
        opener.open.assert_called_once()

    def test_tdm_uses_migrated_endpoint_and_metric(self):
        opener = Mock()
        opener.open.return_value = Response()
        result = dn.download_xml(DOI, self.folder, "tdm", "key/metric", opener, self.limiter, dn.RequestBudget(1))
        query = urlsplit(opener.open.call_args.args[0].full_url)
        self.assertEqual(query.path, "/xmldata/jats")
        self.assertEqual(parse_qs(query.query)["api_key"], ["key/metric"])
        self.assertEqual(result["status"], "downloaded")

    def test_missing_key_without_terminal_cannot_echo_prompt(self):
        with patch.dict(dn.os.environ, {}, clear=True), patch.object(dn.sys.stdin, "isatty", return_value=False), \
             patch.object(dn.getpass, "getpass") as prompt, self.assertRaises(ValueError):
            dn.get_credential("oa")
        prompt.assert_not_called()


if __name__ == "__main__":
    unittest.main()
