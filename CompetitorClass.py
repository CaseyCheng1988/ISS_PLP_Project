import os, requests, json
import spacy

class CompetitorSpace:
    def __init__(self, ner_model):
        self.ner_model = spacy.load(ner_model)
        self.product_search_header = {  'accept':           '*/*',
                                        'accept-encoding':  'gzip, deflate, br',
                                        'accept-language':  'en-US,en;q=0.9',
                                        'cookie':           'SPC_F=2aHPKEYQhfCgZfDr4WEgQdbqEmUXdPEV; REC_T_ID=a4fb901c-aef8-11eb-85df-b496914cc898; _gcl_au=1.1.416473468.1620369880; _fbp=fb.1.1620369882438.362055518; G_ENABLED_IDPS=google; SPC_CLIENTID=MmFIUEtFWVFoZkNnfbxiinmlinhmvcsq; SC_DFP=klVNzMeTvvZKowBNXzitKlKlnafodvVp; SPC_PC_HYBRID_ID=66; csrftoken=TlcvIdflbP5mlJSrgGvpZH6ZlW5ucQKs; welcomePkgShown=true; SPC_IVS=; UYOMAPJWEMDGJ=; SPC_IA=-1; _gcl_aw=GCL.1625448809.CjwKCAjwuIWHBhBDEiwACXQYsTRt9hkjQd7sxCurjmipeJVAN-dP-g6lUTccudUs2OdYcmmDYsk2ABoCnukQAvD_BwE; _gac_UA-61921742-7=1.1625448810.CjwKCAjwuIWHBhBDEiwACXQYsTRt9hkjQd7sxCurjmipeJVAN-dP-g6lUTccudUs2OdYcmmDYsk2ABoCnukQAvD_BwE; SPC_SI=mall.jfiOg6Ulro6H5qQktNMQv156QDtxvvlr; _gid=GA1.2.992328712.1625644644; SPC_U=57559719; SPC_EC=rmDX3JQpc9jhl9CxZZg7yVj1FSIiOA1hcwuBvp0/ye8D4Lkw6WZj3ARVBb8cOKjYiFFDSFJM1SONxxC5x0W4+NEMTxeZ6QBTxk5SuMlVh9Scn0mzQYwwijixexfDSUUZbGIntOHYsAudWS9KVsCDFQ==; SPC_SC_UD=57559719; SPC_STK="emk2eGecSbktuy2kViGTzb0VgCe8XBG85zb/N9KxdnyHLbVHDyLhZOIyKu4KbcYgfM6XC2L+vUvtPyOg6BWSdCgmo7OTUgFh+kP2tnGUxZiX3geCv8VOudhmMLlzmdAr04JvqxuGZGYM8Ap0MtvT4oD8+OGZidQLtlht4WtGEhY="; SPC_SC_TK=0895213e806d2e90fe2feb9d527b23bd; _med=refer; SPC_SSN=o; SPC_WSS=o; AMP_TOKEN=%24NOT_FOUND; SPC_R_T_ID="q95mbs9b/vzp7YX20E55/x4N5vmeNa9euLeV3BcHRr4kgQIWcVG6x0eMWir/5bc8c5DW0Dddyo/06orRY79x7yUzU46EExrajc8/qfMJyGc="; SPC_T_IV="dVz6p+x/ii2Cs68LwdwlVQ=="; SPC_R_T_IV="dVz6p+x/ii2Cs68LwdwlVQ=="; SPC_T_ID="q95mbs9b/vzp7YX20E55/x4N5vmeNa9euLeV3BcHRr4kgQIWcVG6x0eMWir/5bc8c5DW0Dddyo/06orRY79x7yUzU46EExrajc8/qfMJyGc="; _ga=GA1.2.1554149993.1620369882; _dc_gtm_UA-61921742-7=1; CTOKEN=527fAN%2FQEeu3G8y7%2Fl38%2Fg%3D%3D; _ga_4572B3WZ33=GS1.1.1625737081.89.1.1625737394.50',
                                        'if-none-match':    '838023431f8d957fd7a1ae813f3130f3',
                                        'if-none-match-':   '55b03-b2a8a9a1bc913419879ecd087db9dce0',
                                        'referer':          'https://shopee.sg/product/258374675/6448952050/',
                                        'sec-ch-ua':        '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                                        'sec-ch-ua-mobile': '?0',
                                        'sec-fetch-dest':   'empty',
                                        'sec-fetch-mode':   'cors',
                                        'sec-fetch-site':   'same-origin',
                                        'user-agent':       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                        'x-api-source':     'pc',
                                        'x-requested-with': 'XMLHttpRequest',
                                        'x-shopee-language':'en' }

    def product_search(self, search_term, limit=20, ad_suppression=True):
        # If ad suppression is used, request additional 5 entries as buffer.
        if ad_suppression:
            limit += 5

        search_fmt = '%20'.join(search_term.split(' '))
        params = {
            'by': 'relevancy',
            'keyword': search_fmt,
            'limit': limit,
            'newest': 0,
            'order': 'desc',
            'page_type': 'search',
            'scenario': 'PAGE_GLOBAL_SEARCH',
            'version': 2
        }
        url = 'https://shopee.sg/api/v4/search/search_items'
        r = requests.get(url, headers=self.product_search_header, params=params)
        js = r.json()

        # Ad suppression removes all advert products from results.
        if ad_suppression:
            ad_count = 0
            if js['items'] == None:
                print(search_term, len(search_term), js)
            for item in js['items']:
                if item['adsid'] != None:
                    ad_count += 1
                else:
                    break
            js['items'] = js['items'][ad_count:ad_count + limit - 5]

        return [(prod['itemid'], prod['shopid']) for prod in js['items']]

    # Get the reviews in text for a product.
    def get_review_text(self, item_id, shop_id, limit=50):
        res = []

        # API has an internal limit of <60 reviews per request
        MAX_RESULTS_PER_REQUEST = 50
        params = {
            'filter': 1,
            'flag': 1,
            'itemid': item_id,
            'shopid': shop_id,
            'limit': min(limit, MAX_RESULTS_PER_REQUEST),
            'offset': 0,
            'type': 0
        }

        url = f'https://shopee.sg/api/v2/item/get_ratings'

        # Make an initial request to get total available results.
        r = requests.get(url, headers=self.product_search_header, params=params)
        limit = min(limit, int(r.json()['data']['item_rating_summary']['rcount_with_context']))

        # Iteratively make requests until desired limit is fulfilled.
        for i in range(limit // MAX_RESULTS_PER_REQUEST + 1):
            params['offset'] = i * MAX_RESULTS_PER_REQUEST
            r = requests.get(url, headers=self.product_search_header, params=params)
            res += [rating['comment'] for rating in r.json()['data']['ratings']]
        return res

    def get_item_name(self, item_id, shop_id):
        url = f'https://shopee.sg/api/v4/item/get?itemid={item_id}&shopid={shop_id}'
        r = requests.get(url, headers=self.product_search_header)
        js = r.json()
        return js['data']['name']

    def get_entities(self, text):
        doc = self.ner_model(text)
        output = {'BRAND': [], 'MODEL': [], 'TYPE': [], 'VAR_SIZE': [], 'VAR_COLOUR': [], 'VAR_QTY': [],
                  'DEMOGRAPHIC': []}
        buffer = []
        buffer_type = ''
        for idx, token in enumerate(doc):
            if token.ent_iob_ == 'B':
                if len(buffer) != 0:
                    output[buffer_type].append(' '.join(buffer))
                    buffer = []
                buffer.append(str(token))
                buffer_type = token.ent_type_

            elif token.ent_iob_ == 'O':
                continue

            else:
                buffer.append(str(token))

        if len(buffer) != 0:
            output[buffer_type].append(' '.join(buffer))

        return output

    def get_competitors(self, title, prod_limit=50, rev_limit=None):
        entities = self.get_entities(title)
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

        competitors = self.product_search(search_string, limit=prod_limit)
        competitors = [{
            'itemid': cp_itemid,
            'shopid': cp_shopid,
            'title': self.get_item_name(cp_itemid, cp_shopid)
        } for cp_itemid, cp_shopid in competitors]

        return competitors

if __name__ == "__main__":
    PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
    NER_MODEL = os.path.join(PROJ_DIR, 'TitleNER', 'title_model')
    search_engine = CompetitorSpace(ner_model=NER_MODEL)
    title = 'Fjallraven Kanken Classic Backpack - Red Series'
    competitors = search_engine.get_competitors(title, prod_limit=10)
    print(competitors)
