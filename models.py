import sys
import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache
from ebay_items import EbayItems


class UpdateItemsError(Exception):
    pass

class Statistics(ndb.Model):
    when_DB_was_updated = ndb.DateTimeProperty(auto_now=True)
    
    @classmethod
    def update_time_when_DB_was_updated(cls):
        entity = cls.query().get()
        if entity:
            entity.key.delete()
        cls().put()
        
    @classmethod
    def get_time_when_DB_was_updated(cls):
        n = Statistics.query()
        entity = n.get()
        if entity:
            return entity.when_DB_was_updated
        else:
            return None
    

class Filter(ndb.Model):
    category = ndb.StringProperty(default='default')
    condition = ndb.StringProperty()
    max_price = ndb.StringProperty()
    num_items = ndb.IntegerProperty(default=0)
    search_term = ndb.StringProperty(indexed = True)

    @classmethod
    def get_search_term_list(cls):
        q = cls.query(projection=[cls.search_term]).order(cls._key)
        return q.map(lambda rec: rec.search_term)

    @classmethod
    def get_all_filters(cls):
        q = cls.query().order(cls.search_term)
        return q.map(lambda rec: rec.to_dict())

        
class Item(ndb.Model):
    bestoffer = ndb.BooleanProperty(indexed=False)
    buybid = ndb.StringProperty(indexed=False)
    buyitnow = ndb.BooleanProperty(indexed=False)
    category = ndb.StringProperty()
    condition = ndb.StringProperty()
    description = ndb.StringProperty()
    details = ndb.StringProperty(indexed=False)
    feedbackScore = ndb.FloatProperty(indexed=False)
    itemID = ndb.StringProperty()
    max_price = ndb.FloatProperty(indexed=False)
    openbidding = ndb.BooleanProperty(indexed=False)
    percent = ndb.FloatProperty()
    photos = ndb.StringProperty(indexed=False)
    pictureURLSuperSize = ndb.StringProperty(indexed=False)
    positiveFeedbackPercent = ndb.FloatProperty(indexed=False)
    price = ndb.FloatProperty()
    quantity = ndb.IntegerProperty()
    search_term = ndb.StringProperty()
    search_term_lower = ndb.ComputedProperty(lambda self: self.search_term.lower())
#     filter_record = ndb.KeyProperty(kind=FilterRecord)
    sellerUserName = ndb.StringProperty()
    shipping = ndb.FloatProperty(indexed=False)
    viewitem = ndb.StringProperty(indexed=False)

    def put(self):
        """
        Make the field itemID - unique
        :return: nothing
        """
#        from google.appengine.api import memcache
        memcache_key = "itemID" + repr(self.itemID)
        assert memcache.incr(memcache_key) is None
        try:
            from google.appengine.ext.db import STRONG_CONSISTENCY
            key = Item.gql("WHERE itemID = :1", self.itemID)\
                .get(keys_only=True, read_policy=STRONG_CONSISTENCY)
            assert key is None or key == self.key
            ndb.Model.put(self)
        except AssertionError:
            logging.info("attempt to create "+self.itemID+" clone")
        finally:
            memcache.delete(memcache_key)

    @classmethod
    def get_items(cls,
                  StartIndex=0,
                  PageSize=20,
                  category=None,
                  search_term=None,
                  condition=None,
                  order_type=None):
        qr = cls.query()
        if category and category != 'default':
            qr = qr.filter(cls.category == category)
            logging.info(qr)
        if search_term:
            qr = qr.filter(cls.search_term_lower == search_term.lower())
            logging.info(qr)
        if condition:
            qr = qr.filter(ndb.AND((cls.condition >= condition),(cls.condition < condition + u"\ufffd")))
            qr = qr.order(cls.condition)
            logging.info(qr)
        if order_type:
            qr = qr.order(order_type)
            logging.info(qr)

        cache_key = "%s_%s_%s_%s" % ("Item.count", category, search_term, condition)
        count = memcache.get(cache_key)
        if count is None:
            count = qr.count()
            memcache.set(cache_key, count)

        result = qr.map(lambda rec: rec.to_dict(), limit=PageSize, offset=StartIndex)
        return [result,count]

    @classmethod
    def get_all_itemIDs(cls):
        q = cls.query(projection=[cls.itemID]).order(cls._key)
        return q.map(lambda rec: rec.itemID)

    @classmethod
    def delete_item(cls, itemID):
        record = cls.query(cls.itemID == itemID).get()
        record.key.delete()
        return True

    @classmethod
    def save_item(cls, item):
        cls(**item).put()
        return True

    @classmethod
    def update_items(cls):
        try:
            Statistics.update_time_when_DB_was_updated()
            q = Filter.query()
            q.order(Filter._key)
            overall_saved = 0
            current_key_list = cls.get_all_itemIDs()
            for counter, entity in enumerate(q):
                saved_items = 0
                logging.info(entity.search_term)
                data = EbayItems.search_items(search_term=entity.search_term,
                                             category=entity.category,
                                             condition=entity.condition,
                                             max_price=entity.max_price)
                for item in data:
                    if item["itemID"] in current_key_list:
                        current_key_list.remove(item["itemID"])
                        continue
                    if cls.save_item(item):
                        saved_items += 1
                overall_saved += saved_items
                entity.put()
            logging.info('Entities=' + str(counter) +
                         '; Recorded Items=' + str(overall_saved))
        except UpdateItemsError as e:
            error_info = sys.exc_info()
            logging.info(str(error_info)) 
            logging.info(e)

    @classmethod
    def _post_delete_hook(cls, key, future):
        logging.info("_post_delete_hook")
        memcache.flush_all()

    def _post_put_hook(self, future):
        logging.info("_post_put_hook")
        memcache.flush_all()


class Categories(ndb.Model):
    category = ndb.StringProperty()

    @classmethod
    def get_categories(cls):
        mem = memcache.Client()
        categories_cache = mem.get("Categories")
        if categories_cache is None:
            categories = cls.query()
            categories_cache = [category.category for category in categories]
            mem.set("Categories", categories_cache)
        return categories_cache or []
    
    @classmethod
    def add_category(cls, category):
    #    category = category.lower()
        mem = memcache.Client()
        categories_cache = cls.get_categories()
        #save category in DataStore
        if category not in categories_cache:
            cls(category = category).put()
            #save category list in MemCache
            categories_cache.append(category)
            mem.set("Categories", categories_cache)
        return True
    
    @classmethod
    def delete_category(cls, category):
        entities = cls.query(cls.category == category).fetch(keys_only=True)
        mem = memcache.Client()
        categories_cache = mem.get("Categories")
        if categories_cache:
            categories_cache.remove(category)
        ndb.delete_multi(entities)
        mem.set("Categories",categories_cache)
        return True

