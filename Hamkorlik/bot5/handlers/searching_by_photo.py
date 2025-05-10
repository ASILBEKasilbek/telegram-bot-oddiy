import json
import requests

async def searching_anime_by_photo(path):
    try:
        file_path = f"{path}"
        search_url = 'https://yandex.ru/images/search'
        files = {'upfile': ('blob', open(file_path, 'rb'), 'image/jpeg')}
        params = {'rpt': 'imageview', 'format': 'json', 'request': '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}'}
        response = requests.post(search_url, params=params, files=files)
        query_string = json.loads(response.content)['blocks'][0]['params']['url']
        img_search_url = search_url + '?' + query_string
        
        return img_search_url
    except: 
        return "Error"
        
    