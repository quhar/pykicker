import unittest

import pykicker

reponse_code = ""
headers = []

def start_response(_response_code, _headers):
    global response_code
    global headers
    response_code = _response_code
    headers = _headers


class TestPykicker(unittest.TestCase):

    def test_parse_request(self):
        path_info = 'test'
        self.assertEqual('test', pykicker.parse_request(path_info))

    def test_parse_request_upper(self):
        path_info = 'Test'
        self.assertEqual('test', pykicker.parse_request(path_info))

    def test_parse_requst_invalid(self):
        path_info = 'path&with?invalid+chars'
        self.assertRaises(ValueError, pykicker.parse_request, path_info)

    def test_return404(self):
        ret = pykicker.return404(start_response)
        self.assertEqual(0, len(ret))
        self.assertEqual('404 NOT FOUND', response_code)
        self.assertEqual(('Content-Type', 'text/plain'), headers[0])
        self.assertEqual(1, len(headers))

    def test_resturn500(self):
        ret = pykicker.return500(start_response)
        self.assertEqual(0, len(ret))
        self.assertEqual('500 INTERNAL SERVER ERROR', response_code)
        self.assertEqual(('Content-Type', 'text/plain'), headers[0])
        self.assertEqual(1, len(headers))

    def test_return_redirect(self):
        long_path = 'http://google.com/test this'
        ret = pykicker.return_redirct(start_response, long_path)
        self.assertEqual(0, len(ret))
        self.assertEqual('301 Redirect', response_code)
        self.assertEqual(('Location', 'http://google.com/test%20this'), headers[0])
        self.assertEqual(
                ('cache-control', 'no-cache, no-store, max-age=0, must-revalidate'),
                headers[1])
        self.assertEqual(2, len(headers))



if __name__ == '__main__':
    unittest.main()
