import unittest
import mock

import pykicker

response_code = ""
headers = []

def start_response(_response_code, _headers):
    global response_code
    global headers
    response_code = _response_code
    headers = _headers


def redis_get_mock(unused_self, unused_key):
    return b'http://google.com/test this'


class TestPykicker(unittest.TestCase):

    def test_parse_request(self):
        path_info = 'test'
        self.assertEqual(('test', None), pykicker.parse_request(path_info))

    def test_parse_request_upper(self):
        path_info = 'Test'
        self.assertEqual(('test', None), pykicker.parse_request(path_info))

    def test_parse_request_uri(self):
        path_info = 'test/with/some?other=parameters&and=more'
        self.assertEqual(('test', 'with/some?other=parameters&and=more'),
                         tuple(pykicker.parse_request(path_info)))

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
        long_path = b'http://google.com/test this'
        ret = pykicker.return_redirct(start_response, long_path)
        self.assertEqual(0, len(ret))
        self.assertEqual('301 Redirect', response_code)
        self.assertEqual(('Location', 'http://google.com/test this'), headers[0])
        self.assertEqual(('cache-control',
                          'no-cache, no-store, max-age=0, must-revalidate'),
                         headers[1])
        self.assertEqual(2, len(headers))

    @mock.patch('redis.Redis.get', redis_get_mock)
    def test_application_ok(self):
        environ = {'PATH_INFO': '/test/'}
        ret = pykicker.application(environ, start_response)
        self.assertEqual(0, len(ret))
        self.assertEqual('301 Redirect', response_code)
        self.assertEqual(('Location', 'http://google.com/test this'), headers[0])
        self.assertEqual(('cache-control',
                          'no-cache, no-store, max-age=0, must-revalidate'),
                         headers[1])
        self.assertEqual(2, len(headers))
 
    @mock.patch('redis.Redis.get', redis_get_mock)
    def test_application_uri(self):
        environ = {
            'PATH_INFO': '/test/cool/something?new=mayhappen&iam=sure&about=it'
        }
        ret = pykicker.application(environ, start_response)
        self.assertEqual(0, len(ret))
        self.assertEqual('301 Redirect', response_code)
        self.assertEqual(('Location',
                          ('http://google.com/test this/cool/something'
                           '?new=mayhappen&iam=sure&about=it')),
                         headers[0])
        self.assertEqual(('cache-control',
                          'no-cache, no-store, max-age=0, must-revalidate'),
                         headers[1])
        self.assertEqual(2, len(headers))

    def test_application_empty_trailing_slash(self):
        environ = {'PATH_INFO': '/'}
        ret = pykicker.application(environ, start_response)
        self.assertEqual(0, len(ret))
        self.assertEqual('404 NOT FOUND', response_code)
        self.assertEqual(1, len(headers))

    def test_application_empty(self):
        environ = {'PATH_INFO': ''}
        ret = pykicker.application(environ, start_response)
        self.assertEqual(0, len(ret))
        self.assertEqual('404 NOT FOUND', response_code)
        self.assertEqual(1, len(headers))

    def test_bad_redis(self):
        environ = {
            'PATH_INFO': '/test/cool/something?new=mayhappen&iam=sure&about=it'
        }
        ret = pykicker.application(environ, start_response)
        self.assertEqual(0, len(ret))
        self.assertEqual('500 INTERNAL SERVER ERROR', response_code)


if __name__ == '__main__':
    unittest.main()
