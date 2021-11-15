from TitleNER.ner import get_entities
from Shopee.api import product_search, get_review_text
# from Absa.rule_based_adsa import Rule_Based_ADSA


def get_competitors(title, prod_limit=50, rev_limit=50):
    entities = get_entities(title)

    ## information to be included in search list
    search_list = [
        'TYPE', 'DEMOGRAPHIC',
    ]
    search_list = [entities[k] for k in search_list]
    search_list = [e for ls in search_list for e in ls]

    ## construct Shopee search string here
    search_string = ' '.join(search_list)

    competitors = product_search(search_string, limit=prod_limit)

    competitors = [{
        'itemid' :  cp_itemid,
        'shopid' :  cp_shopid,
        'reviews' : get_review_text(cp_itemid, cp_shopid, limit=rev_limit)
    } for cp_itemid, cp_shopid in competitors]  # retrieve title too?

    return competitors


if __name__ == '__main__':
    title = 'Fjallraven Kanken Classic Backpack - Red Series'
    competitors = get_competitors(title, rev_limit=50)
    print(competitors)