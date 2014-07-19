import sys
import logging
import urllib
from google.appengine.ext import ndb
from google.appengine.api import memcache
from ebay_items import EbayItems
from google_api import GoogleCloudStorageAPI
import general_counter
import settings


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
    search_term = ndb.StringProperty(indexed=True)

    @classmethod
    def get_search_term_list(cls):
        q = cls.query(projection=[cls.search_term]).order(cls._key)
        return q.map(lambda rec: rec.search_term)

    @classmethod
    def get_all_filters(cls):
        q = cls.query().order(cls.search_term)
        return q.map(lambda rec: rec.to_dict())

    @classmethod
    def get_all_keys(cls):
        keys_list = []
        for k in cls.query().iter(keys_only=True):
            keys_list.append(k)
        return keys_list


class EbayItem(ndb.Model):
    bestoffer = ndb.BooleanProperty(indexed=False)
    buybid = ndb.StringProperty(indexed=False)
    buyitnow = ndb.BooleanProperty(indexed=False)
    category = ndb.StringProperty()
    condition = ndb.StringProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    details = ndb.StringProperty(indexed=False)
    feedbackScore = ndb.FloatProperty(indexed=False)
    itemID = ndb.StringProperty(indexed=False)
    max_price = ndb.FloatProperty(indexed=False)
    openbidding = ndb.BooleanProperty(indexed=False)
    percent = ndb.FloatProperty(indexed=False)
    photos = ndb.StringProperty(indexed=False)
    pictureURLSuperSize = ndb.StringProperty(indexed=False)
    positiveFeedbackPercent = ndb.FloatProperty(indexed=False)
    price = ndb.FloatProperty(indexed=False)
    quantity = ndb.IntegerProperty(indexed=False)
    search_term = ndb.StringProperty()
    search_term_lower = ndb.ComputedProperty(lambda self: self.search_term.lower())
#     filter_record = ndb.KeyProperty(kind=FilterRecord)
    sellerUserName = ndb.StringProperty(indexed=False)
    shipping = ndb.FloatProperty(indexed=False)
    viewitem = ndb.StringProperty(indexed=False)

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
            qr = qr.filter(ndb.AND((cls.condition >= condition), (cls.condition < condition + u"\ufffd")))
            qr = qr.order(cls.condition)
            logging.info(qr)
        if order_type:
            qr = qr.order(order_type)
            logging.info(qr)

        cache_key = "%s_%s_%s_%s" % ("EbayItem.count", category, search_term, condition)
        count = memcache.get(cache_key)
        if count is None:
            if search_term:
                count = qr.count()
            else:
                count = cls.get_count()
            memcache.set(cache_key, count)

        result = qr.map(lambda rec: rec.to_dict(), limit=PageSize, offset=StartIndex)
        return [result,count]

    @classmethod
    def get_all_keys(cls):
        keys_list = []
        for k in cls.query().iter(keys_only=True):
            keys_list.append(k)
        return keys_list

    @classmethod
    def delete_item(cls, search_term, itemID):
        ndb.Key(cls.__name__, itemID, parent=ndb.Key('Filter', search_term)).delete()
        return True

    @classmethod
    def save_item(cls, item):
        # logging.info("save item: " + item["itemID"])
        parent = ndb.Key('Filter', item["search_term"])
        item["pictureURLSuperSize"] = cls.save_photo(item["itemID"], item["pictureURLSuperSize"]) \
            if item["pictureURLSuperSize"] else ""
        record_key = cls(id=item["itemID"], parent=parent, **item).put()
        return record_key

    @staticmethod
    def save_photo(itemID, photo_url):
        """
        This method uploads photo to the Google Cloud Storage, and returns the URL
        """
        photo = urllib.urlopen(photo_url).read()
        if not photo:
            return None
        filename = str(itemID) + ".jpg"

        gcs_api = GoogleCloudStorageAPI()
        gcs_api.json_upload(filename=filename,
                            content=photo,
                            content_type="image/jpeg")
        result_url = "http://storage.googleapis.com/" + \
                     settings.GCS_BUCKET + \
                     "/" + filename
        return result_url

    @staticmethod
    def delete_photo(itemID):
        """
        This method deletes a photo from the Google Cloud Storage
        """
        filename = str(itemID) + ".jpg"
        gcs_api = GoogleCloudStorageAPI()
        return gcs_api.json_delete(filename)

    @classmethod
    def get_count(cls):
        return general_counter.get_count(cls.__name__)

    @classmethod
    def update_items(cls):
        try:
            Statistics.update_time_when_DB_was_updated()
            q = Filter.query()
            q.order(Filter._key)
            # overall_saved = 0
            old_key_list = cls.get_all_keys()
            current_key_list_backup = old_key_list[:]
            saved_items_keys = []
            for counter, entity in enumerate(q):
                # saved_items = 0
                logging.info(entity.search_term)
                data = EbayItems.search_items(search_term=entity.search_term,
                                              category=entity.category,
                                              condition=entity.condition,
                                              max_price=entity.max_price)
                for item in data:
                    item_key = ndb.Key(cls.__name__, item["itemID"], parent=ndb.Key('Filter', item["search_term"]))
                    if item_key in current_key_list_backup:
                        try:
                            old_key_list.remove(item_key)
                        except ValueError as e:
                            logging.info(str(e))
                            pass
                        continue
                    if item_key in saved_items_keys:
                        logging.info('Doubled save key: ' + str(item_key))
                        continue
                    saved_key = cls.save_item(item)
                    if saved_key:
                        saved_items_keys.append(saved_key)
                # overall_saved += len(saved_items_keys)
            deleted = len([item_key.delete() for item_key in old_key_list])
            logging.info('Entities=' + str(counter) +
                         '; Recorded Items=' + str(len(saved_items_keys)) +
                         '; Deleted Items=' + str(deleted))
            # logging.info('Saved keys: ' + str(saved_items_keys))

        except UpdateItemsError as e:
            error_info = sys.exc_info()
            logging.info(str(error_info)) 
            logging.info(e)

    @classmethod
    def _post_delete_hook(cls, key, future):
        # logging.info("_post_delete_hook: " + str(future.get_result()))
        general_counter.decrement(cls.__name__)
        cls.delete_photo(itemID=key.id())
        memcache.flush_all()

    def _post_put_hook(self, future):
        # logging.info("_post_put_hook: " + str(future.get_result()))
        general_counter.increment(self.__class__.__name__)
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

