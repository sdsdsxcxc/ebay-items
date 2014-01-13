import logging
import json
import webapp2
from google.appengine.ext import ndb


class InstallRecord(ndb.Model):
    DeveloperKey = ndb.StringProperty()
    ApplicationKey = ndb.StringProperty()
    CertificateKey = ndb.StringProperty()
    Token = ndb.TextProperty()
    Zip = ndb.StringProperty()

    @classmethod
    def get_field(cls,field):
        InstallSettings = cls.query()
        settings = InstallSettings.get()
        if not settings:
            raise Exception
        try:
            result = getattr(settings,field)
        except:
            logging.info('*** get_field: BAD Attribute ***')
            logging.info('***' + field + '***')
            raise Exception
        else:
            return result


class MainJsonPage(webapp2.RequestHandler):
    def get(self):
        InstallSettings = InstallRecord.query()
        settings = InstallSettings.get()
        try:
            template_values = {
                'DeveloperKey': settings.DeveloperKey,
                'ApplicationKey': settings.ApplicationKey,
                'CertificateKey': settings.CertificateKey,
                'Token': settings.Token,
                'Zip': settings.Zip,
                'operation_success': False
            }
        except AttributeError:
            template_values = {
                 'operation_success': "Error"
            }
        return self.response.write(json.dumps(template_values))

    def post(self):
        #CLEAR PREVIOUS RECORD
#         for prop in InstallRecord._properties:
#             if not self.request.get(prop):
#                 return {'operation_success': 'Please fill in all fields!'}
#         record = InstallRecord.query().fetch(1)
#         if not record.count():
#             record = InstallRecord()
#         for prop in InstallRecord._properties:
#             record.set(prop, self.request.get(prop))
#         record.put()
        query = InstallRecord.query()
        record = query.get()
        
        logging.info(self.request.POST)
        try:
            params = json.loads(self.request.POST.items()[0][0])
            if not record:
                record = InstallRecord(
                        DeveloperKey = params["DeveloperKey"] or '',
                        ApplicationKey = params["ApplicationKey"] or '',
                        CertificateKey = params["CertificateKey"] or '',
                        Token = params["Token"] or '',
                        Zip = params["Zip"] or '')
            else:
                record.DeveloperKey = params["DeveloperKey"] or record.DeveloperKey
                record.ApplicationKey = params["ApplicationKey"] or record.ApplicationKey
                record.CertificateKey = params["CertificateKey"] or record.CertificateKey
                record.Token = params["Token"] or record.Token
                record.Zip = params["Zip"] or record.Zip
             
            record.put()
        
            template_values = {
                'DeveloperKey': record.DeveloperKey,
                'ApplicationKey': record.ApplicationKey,
                'CertificateKey': record.CertificateKey,
                'Token': record.Token,
                'Zip': record.Zip,
                'operation_success': "Your changes are saved!"
            }
        except Exception as e:
            logging.debug(e)
            template_values = {
                'operation_success': e
            }
        return self.response.write(json.dumps(template_values))


app = webapp2.WSGIApplication([('/settings', MainJsonPage)], debug=True)

"""
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
"""