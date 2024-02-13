import os
import time
import requests
import shutil
import aiohttp
import asyncio
import hashlib
import urllib.request
from tqdm import tqdm
import async_timeout


def download(filename, url, md5=None, retries=5):
    if type(url) == str:
        return _download(filename, url, md5, retries)
    elif type(url) == list:
        for cur_url in url:
            try:
                return _download(filename, cur_url, md5, retries)
            except RuntimeError:
                continue
        raise RuntimeError('Max Retries exceeded!')
    else:
        raise ValueError("The url should be string or list of string.")


async def _asyncdownload(filename, url):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(120):
            async with session.get(url) as response:
                with open(filename, 'wb') as file:
                    async for data in response.content.iter_chunked(512):
                        file.write(data)


def _download(filename, url, md5, retries):
    if retries <= 0:
        raise RuntimeError('Max Retries exceeded!')
    if not os.path.exists(filename):
        print(f'\nDownloading to {filename}...')
        if retries % 3 == 1:
            try:
                down_res = requests.get(url, stream=True)
                file_size = int(down_res.headers.get('Content-Length', 0))
                with tqdm.wrapattr(down_res.raw, "read", total=file_size) as content:
                    with open(filename, 'wb') as file:
                        shutil.copyfileobj(content, file)
            except requests.exceptions.ConnectionError as err:
                print('Warning: Network error. Retrying...\n', err)
                return download(filename, url, md5, retries - 1)
        elif retries % 3 == 2:
            try:
                asyncio.run(_asyncdownload(filename, url))
            except:
                return _download(filename, url, md5, retries - 1)
        else:
            try:
                urllib.request.urlretrieve(url, filename)
            except:
                return _download(filename, url, md5, retries - 1)
            
    if md5 is not None:
        md5_returned = _get_md5(filename)
        if md5 != md5_returned:
            print('Warning: MD5 check failed for the downloaded content. Retrying...')
            os.remove(filename)
            time.sleep(1)
            return _download(filename, url, md5, retries - 1)
    return filename


def _get_md5(filename):
    hash_md5 = hashlib.md5()
    chunk = 8192
    with open(filename, 'rb') as file_to_check:
        while True:
            buffer = file_to_check.read(chunk)
            if not buffer:
                break
            hash_md5.update(buffer)
        md5_returned = hash_md5.hexdigest()
        return md5_returned