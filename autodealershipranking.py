import logging
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.api.datastore import Key
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
import random
import datetime
import hashlib
import simplejson
from google.appengine.api import mail
from HtmlTemplate import HtmlTemplate
from sets import Set
import re

class Dealership(db.Model):
    Location_Code = db.StringProperty()
    Location_Name = db.StringProperty()
    Location_Brand = db.StringProperty()
    Location_Brand_List = db.StringListProperty()
    Location_Brand2 = db.StringProperty()
    Location_Brand3 = db.StringProperty()
    Location_Brand4 = db.StringProperty()
    Location_Address = db.StringProperty()
    Location_City = db.StringProperty()
    Location_State = db.StringProperty()
    Location_Zip = db.StringProperty()
    Average_star_ranking_across_sites = db.FloatProperty()
    Reputation_Score = db.IntegerProperty()
    ScoreWeighted_Rating = db.IntegerProperty()
    ScoreVisibility = db.IntegerProperty()
    ScoreSpread = db.IntegerProperty()
    ScoreVolume = db.IntegerProperty()
    ScoreTime = db.IntegerProperty()
    ScoreLength = db.IntegerProperty()
    Total_number_of_reviews = db.IntegerProperty()
    Number_of_review_sites_with_reviews = db.IntegerProperty()
    abs_total = db.IntegerProperty()

    One_Review = db.TextProperty()
    One_Review_Name = db.StringProperty()
    One_Review_Location = db.StringProperty()
    One_Review_Date = db.StringProperty()
    One_Review_Ranking = db.FloatProperty()

    Two_Review = db.TextProperty()
    Two_Review_Name = db.StringProperty()
    Two_Review_Location = db.StringProperty()
    Two_Review_Date = db.StringProperty()
    Two_Review_Ranking = db.FloatProperty()

    Three_Review = db.TextProperty()
    Three_Review_Name = db.StringProperty()
    Three_Review_Location = db.StringProperty()
    Three_Review_Date = db.StringProperty()
    Three_Review_Ranking = db.FloatProperty()

    Locations_ranking_in_State = db.IntegerProperty()
    Locations_Ranking_by_brand = db.IntegerProperty()

class Order(db.Model):
    email = db.StringProperty()
    dealershipName = db.StringProperty()
    packageSelected = db.StringProperty()
    personName = db.StringProperty()
    phoneNumber = db.StringProperty()
    optimusUserId = db.StringProperty()

class Session(db.Expando):
    brand_list = db.TextProperty()
    state_list = db.TextProperty()
    user_email = db.StringProperty()

def makeQuery(filters={}, orderBy=None, fetchQty=0,  memcache_key=None):
    memcache_key = memcache_key + "_" + "_".join([str(filters[key]['value']) for key in filters.keys() if filters[key]['value']])
    query = memcache.get(memcache_key)
    if query is None:
        query = db.Query(Dealership)
        if orderBy:
            query.order(orderBy)
        keys = [key for key in filters.keys() if filters[key]['value'] and filters[key]['value']]
        for key in keys:
            query.filter(key + ' ' + filters[key]['operator'] + ' ', filters[key]['value'])
        memcache.set(memcache_key, query or '', 60)
    return query.fetch(fetchQty)

def adjCase(string):
    wrgBrands = ['Bmw', 'Gmc', 'Saab']
    string = string.title()
    if any([word in wrgBrands for word in string.split(' ')]):
        return string.replace('Bmw', 'BMW').replace('Gmc', 'GMC').replace('Saab', 'SAAB')
    else:
        return string

class BasePage(webapp.RequestHandler):
    def init_session(self):
        ''' Sets self.session to a models.Session object '''
        self.additionalScript = ''
        session_id = self.request.cookies.get('session_id')
        if session_id:
            session = Session.get_by_key_name(session_id)
        else:
            session = None

        if not session:
            session_id = ''.join(random.choice('012345689abcdefghijklmnopqrstuvwxyz') for i in range(32))
            #all_dealerships = makeQuery(orderBy='-Reputation_Score', fetchQty=1000000, memcache_key='all_dealerships')
            brand_list = 'Acura|Aston Martin|Audi|Bentley|BMW|Buick|Cadillac|Chevrolet|Chyrsler|Dodge|Ferrari|Fiat|Ford|GMC|Honda|Hyundai|Infiniti|Isuzu|Jaguar|Jeep|Kia|Lamborghini|Land Rover|Lexus|Lincoln|Lotus|Maserati|Maybach|Mazda|Mercedes-Benz|Mercury|Mini|Mitsubishi|Nissan|Oldsmobile|Porsche|Ram|Rolls-Royce|SAAB|Scion|Smart|Subaru|Suzuki|Tesla|Toyota|Volkswagen|Volvo|Yamaha|Zap'
            state_list = 'AK|AL|AR|AZ|CA|CO|CT|DE|FL|GA|HI|IA|ID|IL|IN|KS|KY|LA|MA|MD|ME|MI|MN|MO|MS|MT|NC|ND|NE|NH|NJ|NM|NV|NY|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VA|VT|WA|WI|WV|WY'
            session = Session(key_name=session_id, brand_list=brand_list, state_list=state_list)
            #session = Session(key_name=session_id, brand_list=self.getPropertiesList(all_dealerships, 'Location_Brand'), state_list=self.getPropertiesList(all_dealerships, 'Location_State'))
            session.put()
            self.response.headers.add_header('Set-Cookie', 'session_id=%s; Path=/' % session_id)

        self.session = session
        
    def getPropertiesList(self, all_dealerships_query, property, sort=True):
        if property == 'Location_Brand':
            property_list = list(set(d.Location_Brand.split(",")[0] for d in all_dealerships_query if d.Location_Brand))
        elif property == 'Location_State':
            property_list = list(set(d.Location_State for d in all_dealerships_query if d.Location_State))
        if sort:
            property_list.sort()
        return ('|'.join(property_list))
        
    def getTemplate(self, htmlPage, title, pageSpecificHeaders=[]):
        myTemplate = HtmlTemplate()
        myTemplate.addBody(open(htmlPage).read()).addTitle(title)
        myTemplate.addHeaders([
            "https://cert01.securepaypage.litle.com/LitlePayPage/litle-api.js",
            "http://quickui.org/release/quickui.catalog.css",
            "http://code.jquery.com/jquery-1.7.2.min.js",
            "http://quickui.org/release/quickui.js",
            "/static/js/jquery.colorbox.js",
            "/static/js/enhanceselect.js",
            "/static/js/score1.js",
            "/static/js/score2.js",
            "/static/js/currencyFormat.js",
            "/static/js/G.js",
            "/static/js/controls/textField.js",
            "/static/js/controls/submitButton.js",
            "/static/js/controls/stardisplay.js",
            "/static/js/controls/reviewrow.js",
            "/static/js/controls/dealershipResultRow.js",
            "/static/js/controls/rankresult.js",
            "/static/js/controls/rankresult2.js",
            "/static/js/controls/locationentry.js",
            "/static/js/pages/storepage.js",
            "/static/js/pages/buypage.js",
            "/static/js/pages/finddealershippage.js",
            "/static/js/pages/homepage.js",
            "/static/js/pages/publicrankingpage.js"
        ]);
        myTemplate.addHeaders(pageSpecificHeaders)
        self.template = myTemplate
    
    def renderPage(self):
        self.response.out.write(self.template.addScript(self.additionalScript).buildPage())
        
        

class Splash(BasePage):
    def get(self):
        self.init_session()
        self.getTemplate(htmlPage='Splash.html', title="R4D - Home", pageSpecificHeaders=["/static/css/styles.css", "/static/js/supersized.js", "/static/css/supersized.css"])
        self.additionalScript = """
            $(function() {
                $.supersized({
                    slides  :      [ {image : 'static/images/bg_splash.jpeg', title : ''} ]
                });                
            });
        """

        self.renderPage()

class MainRankPage(BasePage):
    def get(self):
        self.init_session()
        self.getTemplate(htmlPage='MainRankPage.html', title="R4D - Ranking", pageSpecificHeaders=["/static/css/styles.css"])

        brandFilter = self.request.get('brand')
        stateFilter = self.request.get('state')

        data = {}

        data['brands_list'] = self.session.brand_list.split('|')
        data['states_list'] = self.session.state_list.split('|')

        dealerships_query = makeQuery(filters={
            'Location_Brand_List': {
                'value': brandFilter,
                'operator': '='
            },
            'Location_State': {
                'value': stateFilter,
                'operator': '='
            },
        }, orderBy='-Reputation_Score', fetchQty=20, memcache_key='dealerships')
        data['rankResults'] = []
        for rank, d in enumerate(dealerships_query):
            data['rankResults'].append({
                'rank': rank + 1,
                'hrefPath': '/store/%s' % d.key().name(),
                'dealership': adjCase(d.Location_Name),
                'state': d.Location_State,
                'numberReviews': d.Total_number_of_reviews,
                'score': d.Reputation_Score
            })

        self.additionalScript = """
                $(function() {
                    $(".inline").colorbox({inline:true, width:"880", height:"700"});
                    $("#root").append(
                        G.controls.Home.create()
                            .pageData(%s)
                            .filterChosen({
                                'brand': '%s',
                                'state': '%s'
                            })
                    )
                });
            """ % (
                   simplejson.dumps(data),
                   brandFilter or 'All Brands',
                   stateFilter or 'All States'
                )

        self.renderPage()

class PublicComparison(BasePage):
    def get(self, locationCode):
        self.init_session()
        self.getTemplate(htmlPage='PublicComparisonPage.html', title="R4D - Listings", pageSpecificHeaders=["/static/css/styles.css"])

        dealership = Dealership.get_by_key_name(str(locationCode))

        brandFilter = self.request.get('brand')
        stateFilter = self.request.get('state')

        data = {
            'dealershipName': adjCase(dealership.Location_Name),
            'dealershipLocationCode': dealership.key().name(),
            'address': {
                'street': dealership.Location_Address,
                'region': '%s, %s %s' % (dealership.Location_City, dealership.Location_State, dealership.Location_Zip)
            },
            'brands_list': (),
            'rankResults': []
        }

        data['brands_list'] = self.session.brand_list.split('|')
        data['states_list'] = self.session.state_list.split('|')

        dealerships_query = makeQuery(filters={
            'Location_Brand_List': {
                'value': brandFilter,
                'operator': '='
            },
            'Location_State': {
                'value': stateFilter,
                'operator': '='
            },
        }, orderBy='-Reputation_Score', fetchQty=20, memcache_key='dealerships_public')

        if brandFilter or stateFilter:
            dealership_rank = len(makeQuery(filters={
                'Location_Brand_List': {
                    'value': brandFilter,
                    'operator': '='
                },
                'Location_State': {
                    'value': stateFilter,
                    'operator': '='
                },
                'Reputation_Score': {
                    'value': dealership.Reputation_Score,
                    'operator': '>'
                }
            }, orderBy='-Reputation_Score', fetchQty=10000000, memcache_key='dealerships_public'))
        else:
            dealership_rank = dealership.abs_total or 0
        
        if dealership_rank <= 20 and all(d.key() != dealership.key() for d in dealerships_query):
            dealerships_query.insert(dealership_rank, dealership)

        for rank, d in enumerate(dealerships_query):
            data['rankResults'].append({
                'hrefPath': '/store/%s' % d.key().name(),
                'highlight': d.key() == dealership.key(),
                'rank': rank + 1,
                'dealership': adjCase(d.Location_Name),
                'state': d.Location_State,
                'numberReviews': d.Total_number_of_reviews,
                'score': d.Reputation_Score
            })

        if dealership_rank > 20:
            data['rankResults'].append({
                'highlight': True,
                'rank': dealership_rank,
                'hrefPath': '/store/%s' % dealership.key().name(),
                'dealership': adjCase(dealership.Location_Name),
                'state': d.Location_State,
                'numberReviews': dealership.Total_number_of_reviews,
                'score': dealership.Reputation_Score
            })


        self.additionalScript = """
                $(function() {
                    $(".inline").colorbox({inline:true, width:"880", height:"700"});
                    $("#root").append(
                        G.controls.PublicRankingPage.create()
                            .pageData(%s)
                            .filterChosen({
                                'brand': '%s',
                                'state': '%s'
                            })
                    )
                });
            """ % (
                   simplejson.dumps(data),
                   brandFilter or 'All Brands',
                   stateFilter or 'All States'
                )

        self.renderPage()

class FindDealer(BasePage):
    def get(self):
        self.init_session()
        self.getTemplate(htmlPage='FindDealerPage.html', title="R4D - Find Dealer", pageSpecificHeaders=["/static/css/styles.css"])

        stateFilter = self.request.get('state')
        zipFilter = self.request.get('zip')
        cityFilter = self.request.get('city')

        data = {
            'zipFilter': zipFilter,
            'stateFilter': stateFilter,
            'states_list': ['Select State'] + self.session.state_list.split('|'),
            'dealerships_list': []
        }

        if any([zipFilter, cityFilter, stateFilter]):
            dealerships_query = makeQuery(filters={
                'Location_Zip': {
                    'value': zipFilter,
                    'operator': '='
                },
                'Location_City': {
                    'value': cityFilter.title(),
                    'operator': '='
                },
                'Location_State': {
                    'value': stateFilter,
                    'operator': '='
                }
            }, fetchQty=1000000, memcache_key='dealerships_find') 

            for d in dealerships_query:
                data['dealerships_list'].append({
                    'hrefPath': '/store/%s' % d.key().name(),
                    'name': adjCase(d.Location_Name),
                    'address': '%s <br/> %s, %s %s' % (d.Location_Address, d.Location_City, d.Location_State, d.Location_Zip)
                })

            self.response.out.write(simplejson.dumps(data))
        else:
            self.additionalScript = """
                    $(function() {
                        $("#root").append(
                            G.controls.FindDealershipPage.create()
                                .pageData(%s)
                        )
                    });
                """ % simplejson.dumps(data)


            self.renderPage()

class Buy(BasePage):
    def get(self):
        self.init_session()
        self.getTemplate(htmlPage='buy2.html', title="R4D - Products", pageSpecificHeaders=["/static/css/styles.css"])

        self.additionalScript = """
                 var page;
                var statusCodes = {
                    1 : "Success",
                    2 : "The same email already exists",
                    3 : "Billing failure",
                    4 : "Other failture",
                    5 : "Product exists",
                    6 : "Email missing",
                    7 : "User creation failure",
                    8 : "Membership creation failure",
                    9 : "Bad product name",
                    10 : "Cancelation failure",
                    11 : "Partner authorization failure",
                    12 : "Suspension failure",
                    13 : "Reactivation failure",
                    14 : "Bad product ID",
                    15 : "Already active",
                    16 : "Zipcode not matching",
                    17 : "Membership does not exist",
                    18 : "Zipcode missing",
                    19 : "Duplicate Username"
                }
                var accountInfo = {
                    "account_email":"",
                    "account_first_name":"",
                    "account_middle_name":"",
                    "account_last_name":"",
                    "account_number":null,
                    "account_birth_year":"",
                    "account_birth_month":"",
                    "account_birth_day":"",
                    "payment_method_type": null,
                    "exp_year":"2012",
                    "exp_month":"01",
                    "address1":null,
                    "address2":null,
                    "address_city":null,
                    "address_zip":null,
                    "address_state":null,
                    "address_country":null,
                    "phone":null,
                    "password":null,
                    "region_id":233,
                    "partner_id":0,
                    "verify_email":false,
                    "welcome_email":true,
                    "show_password":true,
                    "autoprotect":false,
                    "transaction_id":null,
                    "litle_paypageRegistrationId":null,
                    "litle_type":null,
                    "officer_number":null,
                    "routing_number":null,
                    "username":null
                }

                var responseCodes = {
                    1 : 'Timeout contacting server. Please retry.',
                    2 : 'Litle API not loaded. Please reload the page.',
                    871 : 'Invalid card number. (Not Mod10)',
                    872 : 'Invalid card number. (Too short)',
                    873 : 'Invalid card number. (Too long)',
                    874 : 'Invalid card number. (Not a number)',
                    875 : 'We are experiencing technical difficulties. Please try again later or call 877-720-6488',
                    876 : 'Invalid card number. (Failure from Server)',
                    889 : 'We are experiencing technical difficulties. Please try again later or call 877-720-6488'
                }

                $(function() {

                    $("#root").append(
                       page = G.controls.BuyPage.create()
                    )
                });
            """

        self.renderPage()

class Confirmation(BasePage):
    def get(self):
        self.init_session()
        self.additionalScript = """
                $(function() {
                    $('#user_email').attr({
                        href: "mailto:'(user_email)'"
                    }).append('%(user_email)s')
                });
            """  % { 'user_email': self.session.user_email }  
        self.getTemplate(htmlPage='paymentconfirmation.html', title="R4D - Confirmation", pageSpecificHeaders=["/static/css/styles.css"])
        self.renderPage()

class CreateAccount(BasePage):
    def get(self):
        self.init_session()
        email = self.request.get('email')
        self.session.user_email = email
        self.session.save()        
        dealershipName = self.request.get('dealershipName')
        packageSelected = self.request.get('packageSelected')
        personName = self.request.get('personName')
        phoneNumber = self.request.get('phoneNumber')
        optimusUserId = self.request.get('optimusUserId')

        o = Order(
            email=email,
            dealershipName=dealershipName,
            personName=personName,
            packageSelected=packageSelected,
            phoneNumber=phoneNumber,
            optimusUserId=optimusUserId
        )

        db.put(o)

        self.response.out.write("Successful")

class StorePage(BasePage):
    def get(self, locationCode):
        self.init_session()
        self.getTemplate(htmlPage='DealershipPage.html', title="R4D - Store", pageSpecificHeaders=["/static/css/stylesStorePage.css"])
        dealership = Dealership.get_by_key_name(str(locationCode))

        address = ''
        if dealership.Location_City and dealership.Location_State and dealership.Location_Zip:
            address = '%s, %s %s' % (dealership.Location_City, dealership.Location_State, dealership.Location_Zip)

        data = {
            'top_dealerships_by_brand': [],
            'top_dealerships_by_state': [],
            'location_code': locationCode,
            'reviews': [
                {
                 'review': dealership.One_Review or 'Not Found',
                 'reviewDate': dealership.One_Review_Date or '',
                 'reviewerName': dealership.One_Review_Name or '',
                 'reviewerLocation': dealership.One_Review_Location or '',
                 'rating': dealership.One_Review_Ranking or 0
                },
                {
                 'review': dealership.Two_Review or 'Not Found',
                 'reviewDate': dealership.Two_Review_Date or '',
                 'reviewerName': dealership.Two_Review_Name or '',
                 'reviewerLocation': dealership.Two_Review_Location or '',
                 'rating': dealership.Two_Review_Ranking or 0
                },
                {
                 'review': dealership.Three_Review or 'Not Found',
                 'reviewDate': dealership.Three_Review_Date or '',
                 'reviewerName': dealership.Three_Review_Name or '',
                 'reviewerLocation': dealership.Three_Review_Location or '',
                 'rating': dealership.Three_Review_Ranking or 0
                }
            ],
            'reviewCount': dealership.Total_number_of_reviews,
            'reviewSiteCount': dealership.Number_of_review_sites_with_reviews  ,
            'dealershipName': adjCase(dealership.Location_Name),
            'dealershipBrand': dealership.Location_Brand.split(',')[0].title() if dealership.Location_Brand else 'Brand',
            'dealershipState': dealership.Location_State or 'State',
            'averageStarRating': dealership.Average_star_ranking_across_sites,
            'address': {
                'street': dealership.Location_Address,
                'region': address
            }
        }


        top_dealerships_by_brand_query = makeQuery(filters={
            'Location_Brand_List': {
                'value': dealership.Location_Brand.split(',')[0],
                'operator': '='
            }
        }, orderBy='-Reputation_Score', fetchQty=10, memcache_key='dealerships_topBrand')


        top_dealerships_by_state_query = makeQuery(filters={
            'Location_State': {
                'value': dealership.Location_State,
                'operator': '='
            }
        }, orderBy='-Reputation_Score', fetchQty=10, memcache_key='dealerships_topState')

        dealership_rank_by_state = len(makeQuery(filters={
            'Location_State': {
                'value': dealership.Location_State,
                'operator': '='
            },
            'Reputation_Score': {
                'value': dealership.Reputation_Score,
                'operator': '>'
            }
        }, orderBy='-Reputation_Score', fetchQty=10000000, memcache_key='dealerships_rankState'))

        if dealership_rank_by_state <= 10 and all(d.key() != dealership.key() for d in top_dealerships_by_state_query):
            top_dealerships_by_state_query.insert(dealership_rank_by_state, dealership)

        dealership_rank_by_brand = len(makeQuery(filters={
            'Location_Brand_List': {
                'value': dealership.Location_Brand.split(',')[0],
                'operator': '='
            },
            'Reputation_Score': {
                'value': dealership.Reputation_Score,
                'operator': '>'
            }
        }, orderBy='-Reputation_Score', fetchQty=10000000, memcache_key='dealerships_rankBrand'))

        if dealership_rank_by_brand <= 10 and all(d.key() != dealership.key() for d in top_dealerships_by_brand_query):
            top_dealerships_by_brand_query.insert(dealership_rank_by_brand, dealership)


        for rank, d in enumerate(top_dealerships_by_brand_query):
            data['top_dealerships_by_brand'].append({
                'highlight': d.key() == dealership.key(),
                'locationCode': d.key().name(),
                'rank': rank + 1,
                'dealership': adjCase(d.Location_Name),
                'score': d.Reputation_Score
            })

        for rank, d in enumerate(top_dealerships_by_state_query):
            data['top_dealerships_by_state'].append({
                'highlight': d.key() == dealership.key(),
                'locationCode': d.key().name(),
                'rank': rank + 1,
                'dealership': adjCase(d.Location_Name),
                'score': d.Reputation_Score
            })

        if dealership_rank_by_state > 10:
            data['top_dealerships_by_state'].append({
                'highlight': True,
                'locationCode': dealership.key().name(),
                'rank': dealership_rank_by_state,
                'dealership': adjCase(dealership.Location_Name),
                'score': dealership.Reputation_Score
            })


        if dealership_rank_by_brand > 10:
            data['top_dealerships_by_brand'].append({
                'highlight': True,
                'locationCode': dealership.key().name(),
                'rank': dealership_rank_by_brand,
                'dealership': adjCase(dealership.Location_Name),
                'score': dealership.Reputation_Score
            })


        self.additionalScript = """
                $(function() {

                    $(".inline").colorbox({inline:true, width:"880", height:"700"});

                    $("#root").append(
                        G.controls.StorePage.create().pageData(%(pageData)s)
                    )
                    if (window.oRepStar === undefined) {
                        window.oRepStar = {};
                      }
                     window.oRepStar.oScore = new window.RepStar.Score(109466,
                         {
                             "overallScore":%(overallScore)s,
                             "averageRatingScore":%(weightedAverage)s,
                             "industryScore":%(recentness)s,
                             "lengthScore":%(length)s,
                             "timeScore":%(volume)s,
                             "recentnessScore":%(visibility)s,
                             "reviewerScore":%(spread)s
                        }
                    );
                     window.oRepStar.oScore.init();
                });
            """ % {
                'pageData': simplejson.dumps(data),
                'overallScore': simplejson.dumps(dealership.Reputation_Score),
                'weightedAverage': simplejson.dumps((dealership.Average_star_ranking_across_sites /5)*100),
                'volume': simplejson.dumps(dealership.ScoreVolume),
                'recentness': simplejson.dumps(dealership.ScoreTime),
                'length': simplejson.dumps(dealership.ScoreLength),
                'spread': simplejson.dumps(dealership.ScoreSpread),
                'visibility': simplejson.dumps(dealership.ScoreVisibility)
            }


        self.renderPage()

class Delete(webapp.RequestHandler):

    def get(self):
        
        '''
        query = db.Query(Dealership).fetch(1000000)
        toDelete = []
        for d in query:
            toDelete.append(d)
        db.delete(toDelete)
        '''
        print 'hi'

class InsertDataBig(webapp.RequestHandler):

    def get(self, offsetby):
        '''
        offsetby = int(offsetby) if offsetby else 0
        query = db.Query(Dealership).order('-Reputation_Score').fetch(500, offset=int(offsetby))
        entities = []
        i = 0
        if len(query):
            for d in query:
                i += 1
                d.abs_total = offsetby + i
                entities.append(d)
            db.put(entities)    
            self.redirect("/insertbig/" + str(int(offsetby) + 500))    
        else:
            return
  
        '''
        print 'hi'
        
application = webapp.WSGIApplication(
                                     [
                                         ('/rank', MainRankPage),
                                         ('/delete', Delete),
                                         ('/', Splash),
                                         ('/insertbig/([^/]+)?', InsertDataBig),
                                         ('/store/([^/]+)?', StorePage),
                                         ('/confirmation', Confirmation),
                                         ('/products', Buy),
                                         ('/publicranking/([^/]+)?', PublicComparison),
                                         ('/finddealer', FindDealer),
                                         ('/createAccount', CreateAccount)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
