import os
import spacy
from TitleNER.ner import get_entities
from Shopee.api import product_search, get_review_text, get_item_name

def get_competitors(title, prod_limit=50, rev_limit=None):
    entities = get_entities(title)
    print("Detected named entities: ", entities)

    ## information to be included in search list
    search_list = [
        'TYPE', 'DEMOGRAPHIC'
    ]
    search_list = [entities[k] for k in search_list]
    search_list = [e for ls in search_list for e in ls]

    ## construct Shopee search string here
    search_string = " ".join(search_list)
    search_string = search_string.split(' ')
    search_string = "_".join(search_string)
    print("Searching products similar to: ", search_string, ' ......')

    competitors = product_search(search_string, limit=prod_limit)
    competitors = [{
        'itemid' :  cp_itemid,
        'shopid' :  cp_shopid,
        'title' : get_item_name(cp_itemid, cp_shopid)
    } for cp_itemid, cp_shopid in competitors]

    return competitors


if __name__ == '__main__':
    title = 'Fjallraven Kanken Classic Backpack - Red Series'
    competitors = get_competitors(title, prod_limit=20)
    print(competitors)

