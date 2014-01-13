import json
import logging
from ebay.finding import findItemsByKeywords
from ebay.shopping import GetMultipleItems
from settings import InstallRecord


class EbayItemError(Exception):
    pass

class EbayItems(object):
    @staticmethod
    def item_attr(data, attr_array, default=''):
        result_temp = data
        result = None
        try:
            for attr in attr_array:
                result_temp = result_temp[attr]
            result = result_temp
        except Exception as e:
            logging.info('no such attribute in item: ' + str(e))
            return default
        else:
            return result
    
    @classmethod
    def search_items(cls,
                     search_term=None,
                     category=None,
                     buyitnow=None,
                     condition=None,
                     max_price=None,
                     Zip=None):
        logging.info(str(locals()))
        if not search_term:
            return []
        if not Zip:
            Zip = InstallRecord.get_field('Zip')
        itemFilter = []
        if max_price:
            itemFilter = [{'name': 'MaxPrice',
                           'value': str(float(max_price)),
                           'paramName': 'Currency',
                           'paramValue': 'USD'}]
        if condition:
            itemFilter.append({'name': 'Condition',
                               'value': condition})
        outputSelector = ('PictureURLSuperSize', 'SellerInfo')
    
        json_str = findItemsByKeywords(keywords=search_term,
                                       buyerPostalCode=Zip,
                                       itemFilter=itemFilter,
                                       outputSelector=outputSelector)
        logging.info(json_str)
        data = json.loads(json_str)
        items_count = int(cls.item_attr(data, ['findItemsByKeywordsResponse', 0,
                                                'searchResult', 0, '@count'], '0'))
        if items_count == 0:
            return []
        items = cls.item_attr(data, ['findItemsByKeywordsResponse', 0, 
                                     'searchResult', 0, 'item'], [])
        data_items = []
        for item in items:
            try:
                processed_item = cls.process_item(item,
                                                  search_term,
                                                  category,
                                                  buyitnow,
                                                  max_price)
            except EbayItemError:
                processed_item = None
            if processed_item:
                data_items.append(processed_item)
        return data_items

    @classmethod
    def process_item(cls, item, search_term, category, buyitnow, max_price):
        #First check 'Buy It Now' price, if it doesn't exist, get current price
        if cls.item_attr(item, ["listingInfo", 0,
                            'buyItNowAvailable', 0]) == 'true':
            item_price = cls.item_attr(item, ["listingInfo", 0, "buyItNowPrice", 0,
                                              "__value__"])
            item_buyitnow = True
        else:
            #if buyitnow option enabled - continue the cycle
            if buyitnow:
                return None
            item_buyitnow = False
            item_price = cls.item_attr(item, ['sellingStatus', 0, 'currentPrice', 0,
                                          '__value__'], 'no')
            if item_price == 'no':
                return None
        if max_price:
            if float(item_price) > float(max_price):
                return None
        item_bestOffer = cls.item_attr(item, ["listingInfo", 0, 'bestOfferEnabled', 0], False)
        item_bestOffer = True if (item_bestOffer == "true") else False
        if(cls.item_attr(item, ["listingInfo", 0, 'listingType', 0]) == "StoreInventory") or\
            (cls.item_attr(item, ["listingInfo", 0, 'listingType', 0]) == "FixedPrice"):
            item_buyitnow = True
        item_openbidding = False
        #AuctionWithBIN
        if(cls.item_attr(item, ["listingInfo", 0, 'listingType', 0]) == "AuctionWithBIN"):
            item_buyitnow = True
            item_openbidding = True
        #Auction
        if(cls.item_attr(item, ["listingInfo", 0, 'listingType', 0]) == "Auction"):
            item_openbidding = True
        item_condition = cls.item_attr(item, ['condition', 0, 'conditionDisplayName', 0])
#         if condition:
#             if condition.lower() not in item_condition.lower():
#                 continue
        item = {
             'itemID': cls.item_attr(item, ['itemId', 0]),
             'search_term': search_term,
             'category': category,
             'condition': item_condition,
             'description': cls.item_attr(item, ['title', 0]),
             'price': float(item_price),
             'max_price': float(max_price),
             'buyitnow': item_buyitnow,
             'bestoffer': item_bestOffer,
             'openbidding': item_openbidding,
             'percent': int(round((float(max_price) - float(item_price))
                                  / float(item_price)*100)),
             'shipping': float(cls.item_attr(item, ['shippingInfo', 0, 
                                                    'shippingServiceCost', 0, 
                                                    '__value__'], '0')),
             'details': cls.item_attr(item, ['itemId', 0]),
             'photos': cls.item_attr(item, ['galleryURL', 0]),
             'viewitem': cls.item_attr(item, ['viewItemURL', 0]),
             'buybid': cls.item_attr(item, ['viewItemURL', 0]),
             'pictureURLSuperSize': cls.item_attr(item, 
                                                  ['pictureURLSuperSize',
                                                    0]),
             'sellerUserName': cls.item_attr(item, ['sellerInfo', 0,
                                                    'sellerUserName', 0]),
             'feedbackScore': float(cls.item_attr(item, ['sellerInfo', 0,
                                                         'feedbackScore', 0])),
             'positiveFeedbackPercent': float(cls.item_attr(item, ['sellerInfo',
                                                                    0, 
                                                                   'positiveFeedbackPercent',
                                                                    0]))
        }
        return item

    @staticmethod
    def quantity(itemID):
        result = 'no info'
        json_str = GetMultipleItems(item_id=itemID)
#             logging.info(json_str)
        data = json.loads(json_str)
#             logging.info(data)
        for item in data['Item']:
            try:
                quantity = item["Quantity"]
                quantity_sold = item["QuantitySold"]
                quantity_available = quantity - quantity_sold
                itemID = item["ItemID"]
                result = quantity_available
            except Exception as e:
                logging.error(e)
        return result
