import aiohttp
import requests
import logging
import binascii

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
}

async def download(url, binary=False):
    logging.debug('download: %s', url)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        response = await session.get(url=url, headers=headers)

        if response.status == requests.codes.ok:
            if binary:
                # data = binascii.unhexlify(data)
                data = await response.read()
            else:
                #response.encoding = 'utf8'
                data = await response.text()
                logging.debug('content: %s', data)

            logging.debug('length: %.2f KB', len(data) / 1000.0)
        else:
            raise Exception()
    return data
