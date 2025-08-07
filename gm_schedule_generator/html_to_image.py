import io
import logging
from requests import Response
from requests.auth import HTTPBasicAuth
import requests
from typing import Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HtmlToImage:
    def __init__(self, token: str = None):
        if not token:
            raise ValueError('token cannot be none')
        try:
            user_id, key = token.split(':')
        except ValueError:
            raise ValueError('token need to be user_id:api_key')

        session: requests.Session = requests.Session()
        session.auth = HTTPBasicAuth(user_id, key)
        self.session = session
        self.base_url = 'https://hcti.io/v1'

    def html_to_image(self, html: str) -> Tuple[io.BytesIO, str]:
        data: dict = {'html': html}
        resp: Response = self.session.post(
            url=self.base_url+'/image', data=data)
        if resp.status_code != 200:
            logger.error(
                f'error while generating image: {resp.content}, status code={resp.status_code}')
            return None, None
        url: str = resp.json().get('url', '')
        img = self.get_image(url)
        return io.BytesIO(img), url

    def get_image(self, url: str) -> bytes:
        resp: Response = self.session.get(url)
        return resp.content
