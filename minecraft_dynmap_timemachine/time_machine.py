import logging
import io
import aiohttp
import requests
import asyncio

from . import projection
from PIL import Image


class TimeMachine(object):

    def __init__(self, dm_map):
        self._dm_map = dm_map
        # self.dynmap = dynmap.DynMap(url)

    async def get_aiohttp(self, session, data, dest_img, total_tiles, zoomed_scale, from_x, to_y):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
        }
        async with session.get(data['img_url'], headers=headers) as resp:
            logging.info('tile %d/%d [%d, %d]', data['processed'], total_tiles, data['x'], data['y'])
            logging.debug('download: %s', data['img_url'])
            
            if resp.status!=requests.codes.ok:
                logging.debug('Unable to download "%s": %s', data['img_url'], str(resp.status))
                return {'result': 'failed', 'processed': data['processed'], 'status': resp.status, 'url': data['img_url']}
                    
            img_data = await resp.read()
            logging.debug('length: %.2f KB', len(img_data) / 1000.0)
            stream = io.BytesIO(img_data)
            im = Image.open(stream)
                    
            box = (int(abs(data['x'] - from_x) * 128 / zoomed_scale), int((abs(to_y - data['y']) - zoomed_scale) * 128 / zoomed_scale))
            logging.debug('place to [%d, %d]', box[0], box[1])
            dest_img.paste(im, box)
            return {'result': 'ok', 'status': resp.status}
    
    async def create_dest_img(self, processed_data, dest_img, total_tiles, zoomed_scale, from_x, to_y, pause):
        timeout = aiohttp.ClientTimeout(total=3600)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for data in processed_data:
                tasks.append(asyncio.ensure_future(self.get_aiohttp(session=session, data=data, dest_img=dest_img, total_tiles=total_tiles, zoomed_scale=zoomed_scale, from_x=from_x, to_y=to_y)))
                
            tasks_data = await asyncio.gather(*tasks)
            for result in tasks_data:
                if result['result'] == 'failed':
                    print('-'*50)
                    print(f'Failed Download: {result["processed"]}')
                    print(f'URL: {result["url"]}')
                    print(f'Status Code: {result["status"]}')
                    print('-'*50)
            await session.close()

            # avoid throttle limit, don't overload the server
            #await asyncio.sleep(float(pause))


    def capture_single(self, tiles_url, map, t_loc, size, pause=0):
        from_tile, to_tile = t_loc.make_range(size[0], size[1])
        zoomed_scale = projection.zoomed_scale(t_loc.zoom)

        width, height = (abs(to_tile.x - from_tile.x) * 128 / zoomed_scale, abs(to_tile.y - from_tile.y) * 128 / zoomed_scale)
        logging.info('final size in px: [%d, %d]', width, height)
        dest_img = Image.new('RGB', (int(width), int(height)))

        logging.info('downloading tiles...')
        # logging.info('tile image path: %s', image_url)
        total_tiles = len(range(from_tile.x, to_tile.x, zoomed_scale)) * len(range(from_tile.y, to_tile.y, zoomed_scale))
        processed = 0
        processed_data =[]

        for x in range(from_tile.x, to_tile.x, zoomed_scale):
            for y in range(from_tile.y, to_tile.y, zoomed_scale):
                img_rel_path = map.image_url(projection.TileLocation(x, y, t_loc.zoom), tiles_url)
                img_url = self._dm_map.url + img_rel_path
                processed += 1
                
                data = {
                    'processed': processed,
                    'x': x,
                    'y': y,
                    'img_url': img_url,
                }
            
                processed_data.append(data)
                
        asyncio.run(self.create_dest_img(
                    dest_img=dest_img,
                    processed_data=processed_data,
                    total_tiles=total_tiles,
                    zoomed_scale=zoomed_scale,
                    from_x=from_tile.x,
                    to_y=to_tile.y,
                    pause=pause
                ))        
        
        return dest_img

    def compare_images(self, image1, image2):
        file1data = list(image1.getdata())
        file2data = list(image2.getdata())

        diff = 0
        for i in range(len(file1data)):
            if file1data[i] != file2data[i]:
                diff += 1

        return float(diff) / len(file1data)
