from lxml import html
import requests
import string
from bs4 import BeautifulSoup
import json

import math

MFC_ITEMS_PER_PAGE = 64

def getUserFigures(username, page_n=1, items_per_page=32):

    item_f = page_n * items_per_page / MFC_ITEMS_PER_PAGE

    real_page_n = math.ceil(item_f)

    url_template = string.Template('https://myfigurecollection.net/users.v4.php?mode=view&username=$username&tab=collection&rootId=0&status=2&page=$page')
    url = url_template.substitute(username=username, page=real_page_n)

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'lxml')
    tags = soup.find_all("a", class_="item-root-0")

    item_lower_bound = (item_f - items_per_page / MFC_ITEMS_PER_PAGE) * MFC_ITEMS_PER_PAGE
    item_upper_bound = item_f * MFC_ITEMS_PER_PAGE

    result = {
        'items': {
            'count': int(soup.find(class_="count").get_text().replace(',', '')),
            'pages': int(soup.title.string.split('Collection (')[1].split('|')[0].split('of ')[1].split(')')[0]),
            'item': []
        }
    }
    for tag in tags:
        figure = {
            'id': int(tag.get('href').split('/')[-1]),
            'name': tag.img.get('alt')
        }
        result['items']['item'].append(figure)

    if item_lower_bound > len(result['items']['item']):
        result['items']['item'] = []
    else:
        item_upper_bound = math.max(item_upper_bound, len(result['items']['item']))
        result['items']['item'] = result['items']['item'][item_lower_bound:item_upper_bound]
    return result

f = open("result.json", "w")
f.write(json.dumps(getUserFigures('ciro22'), ensure_ascii=False, sort_keys=True, indent=4))