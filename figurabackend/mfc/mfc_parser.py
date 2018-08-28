from lxml import html
import requests
import string
from bs4 import BeautifulSoup
import json
import math

MFC_ITEMS_PER_PAGE = 88

# Warning those who enter here

def getUserFigures(username, page_n=1, items_per_page = 22):

    item_f = page_n * items_per_page / MFC_ITEMS_PER_PAGE

    real_page_n = math.ceil(item_f)

    url_template = string.Template('https://myfigurecollection.net/users.v4.php?mode=view&username=$username&tab=collection&rootId=0&status=2&page=$page')
    url = url_template.substitute(username=username, page=real_page_n)
    
    page = requests.get(url)

    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.content, 'lxml')
    tags = soup.find_all("a", class_="item-root-0")

    items = []

    for tag in tags:
        figure = {
            'id': int(tag.get('href').split('/')[-1]),
            'name': tag.img.get('alt')
        }
        items.append(figure)

    # Calculate lower and upper bounds for which figures to get and leave only those
    # (part of page remapping)

    item_lower_bound = item_f - items_per_page / MFC_ITEMS_PER_PAGE
    item_lower_bound -= math.floor(item_lower_bound)
    item_lower_bound *= MFC_ITEMS_PER_PAGE
    item_lower_bound = int(item_lower_bound)

    item_upper_bound = item_lower_bound + (items_per_page / MFC_ITEMS_PER_PAGE) * MFC_ITEMS_PER_PAGE
    item_upper_bound = int(item_upper_bound)

    if item_lower_bound > len(items):
        items = []
    else:
        item_upper_bound = min(item_upper_bound, len(items))
        s = items[item_lower_bound:item_upper_bound]

        items = s

    count = soup.find(class_="listing-count-value")

    if count:
        count = int(count.get_text().replace(',', '').split(' items')[0])
    else:
        count = 0
    pages = 0
    if 'Collection (' in soup.title.string:
        pages = int(soup.title.string.split('Collection (')[1].split('|')[0].split('of ')[1].split(')')[0])

    result = {
        'items': {
            'count': count,
            'pages': pages,
            'item': items
        }
    }

    return result