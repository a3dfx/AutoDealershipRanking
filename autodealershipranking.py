import logging
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.api.datastore import Key
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

def makeQuery(filters, orderBy=None, fetchQty=0):
    query = db.Query(Dealership)
    if orderBy:
        query.order(orderBy)
    keys = [key for key in filters.keys() if filters[key]['value'] and filters[key]['value']]
    for key in keys:
        query.filter(key + ' ' + filters[key]['operator'] + ' ', filters[key]['value'])
    return query.fetch(fetchQty)

def getPropertiesList(all_dealerships_query, property, sort=True):
    if property == 'Location_Brand':
        property_list = list(set(d.Location_Brand.split(",")[0] for d in all_dealerships_query if d.Location_Brand))
    elif property == 'Location_State':
        property_list = list(set(d.Location_State for d in all_dealerships_query if d.Location_State))
    if sort:
        property_list.sort()
    return property_list   

class MainPage(webapp.RequestHandler):
    def get(self):

        html = open('MainRankPage.html').read()
        
        myTemplate = HtmlTemplate()
        
        myTemplate.addHeaders([
            "http://quickui.org/release/quickui.catalog.css",
            "http://code.jquery.com/jquery-1.7.2.min.js",
            "http://quickui.org/release/quickui.js",
            "/static/css/styles.css",
            "/static/js/enhanceselect.js",
            "/static/js/jquery.colorbox.js",
            "/static/js/G.js",
            "/static/js/controls/rankresult.js",
            "/static/js/pages/homepage.js"
        ]);
        
        brandFilter = self.request.get('brand')
        stateFilter = self.request.get('state')
        
        data = {}
        
        all_dealerships = db.Query(Dealership).fetch(1000000) 
        
        data['brands_list'] = getPropertiesList(all_dealerships, 'Location_Brand')
        data['states_list'] = getPropertiesList(all_dealerships, 'Location_State') 
        
        dealerships_query = makeQuery(filters={
            'Location_Brand': {
                'value': brandFilter,
                'operator': '='
            }, 
            'Location_State': {
                'value': stateFilter,
                'operator': '='
            }, 
        }, orderBy='-Reputation_Score', fetchQty=20)
        
        data['rankResults'] = []
        for rank, d in enumerate(dealerships_query):
            data['rankResults'].append({
                'rank': rank + 1,
                'hrefPath': '/store/%s' % d.key().name(),
                'dealership': d.Location_Name,
                'state': d.Location_State,
                'numberReviews': d.Total_number_of_reviews,
                'score': d.Reputation_Score
            })
            
        script = """
                $(document).ready(function() {
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

        self.response.out.write(myTemplate.addBody(html).addScript(script).buildPage()) 

class PublicComparison(webapp.RequestHandler):
    def get(self, locationCode):
        
        html = open('PublicComparisonPage.html').read()
        
        myTemplate = HtmlTemplate()
        
        myTemplate.addHeaders([
            "http://quickui.org/release/quickui.catalog.css",
            "http://code.jquery.com/jquery-1.7.2.min.js",
            "http://quickui.org/release/quickui.js",
            "/static/css/styles.css",
            "/static/js/enhanceselect.js",
            "/static/js/jquery.colorbox.js",
            "/static/js/G.js",
            "/static/js/controls/rankresult.js",
            "/static/js/pages/publicrankingpage.js"
        ]);
        
        dealership = Dealership.get_by_key_name(str(locationCode))
      
        brandFilter = self.request.get('brand')
        stateFilter = self.request.get('state')
        
        data = {
            'dealershipName': dealership.Location_Name,
            'dealershipLocationCode': dealership.key().name(),
            'address': {
                'street': dealership.Location_Address,
                'region': '%s, %s %s' % (dealership.Location_City, dealership.Location_State, dealership.Location_Zip)
            },
            'brands_list': (),
            'rankResults': []
        }
        
        all_dealerships = db.Query(Dealership).fetch(1000000) 
        
        data['brands_list'] = getPropertiesList(all_dealerships, 'Location_Brand')
        data['states_list'] = getPropertiesList(all_dealerships, 'Location_State')  

        dealerships_query = makeQuery(filters={
            'Location_Brand': {
                'value': brandFilter,
                'operator': '='
            }, 
            'Location_State': {
                'value': stateFilter,
                'operator': '='
            }, 
        }, orderBy='-Reputation_Score', fetchQty=20)
        
        dealership_rank = len(makeQuery(filters={
            'Location_Brand': {
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
        }, orderBy='-Reputation_Score', fetchQty=10000000))
        
        if dealership_rank <= 20 and not any([True for d in dealerships_query if d.key() == dealership.key()]):
            dealerships_query.insert(dealership_rank, dealership)  
        
        for rank, d in enumerate(dealerships_query):        
            data['rankResults'].append({
                'hrefPath': '/store/%s' % d.key().name(),
                'highlight': d.key() == dealership.key(),
                'rank': rank + 1,
                'dealership': d.Location_Name,
                'state': d.Location_State,
                'numberReviews': d.Total_number_of_reviews,
                'score': d.Reputation_Score
            })

        if dealership_rank > 20:
            data['rankResults'].append({
                'highlight': True,                                     
                'rank': dealership_rank,
                'hrefPath': '/store/%s' % dealership.key().name(),
                'dealership': dealership.Location_Name,
                'state': d.Location_State,
                'numberReviews': dealership.Total_number_of_reviews,
                'score': dealership.Reputation_Score
            })   
                   
            
        script = """
                G.html = $(%s)
                $(document).ready(function() {
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
                   simplejson.dumps(html), 
                   simplejson.dumps(data), 
                   brandFilter or 'All Brands', 
                   stateFilter or 'All States'
                )
            
        self.response.out.write(myTemplate.addBody(html).addScript(script).buildPage()) 

class FindDealer(webapp.RequestHandler):
    def get(self):
        
        html = open('FindDealerPage.html').read()
        
        myTemplate = HtmlTemplate()
        
        myTemplate.addHeaders([
            "http://quickui.org/release/quickui.catalog.css",
            "http://code.jquery.com/jquery-1.7.2.min.js",
            "http://quickui.org/release/quickui.js",
            "/static/css/stylesDealershipFind.css",
            "/static/js/enhanceselect.js",
            "/static/js/jquery.colorbox.js",
            "/static/js/G.js",
            "/static/js/controls/textField.js",
            "/static/js/controls/dealershipResultRow.js",
            "/static/js/pages/finddealershippage.js"
        ]);
        
        stateFilter = self.request.get('state')
        zipFilter = self.request.get('zip')
        cityFilter = self.request.get('city')  
               
        all_dealerships = db.Query(Dealership).fetch(1000000)        
               
        data = {
            'zipFilter': zipFilter,
            'stateFilter': stateFilter,
            'states_list': ['Select State'] + getPropertiesList(all_dealerships, 'Location_State'),
            'dealerships_list': []
        }     
        
        if any([zipFilter, cityFilter, stateFilter]):
            dealerships_query = makeQuery(filters={
                'Location_Zip': {
                    'value': zipFilter,
                    'operator': '='
                }, 
                'Location_City': {
                    'value': cityFilter,
                    'operator': '='
                },
                'Location_State': {
                    'value': stateFilter,
                    'operator': '='
                }                                                                                                
            }, fetchQty=1000000)
            
            for d in dealerships_query:
                data['dealerships_list'].append({
                    'hrefPath': '/publicranking/%s' % d.key().name(),
                    'name': d.Location_Name,
                    'address': '%s <br/> %s, %s %s' % (d.Location_Address, d.Location_City, d.Location_State, d.Location_Zip)
                })     
                        
            self.response.out.write(simplejson.dumps(data))
        else:
            script = """
                    $(document).ready(function() {
                        $("#root").append(
                            G.controls.FindDealershipPage.create()
                                .pageData(%s)
                        )               
                    });
                """ % simplejson.dumps(data)
                
                      
            self.response.out.write(myTemplate.addBody(html).addScript(script).buildPage()) 

class Buy(webapp.RequestHandler):
    def get(self):
        
        html = open('buy.html').read()
        
        myTemplate = HtmlTemplate()
        
        myTemplate.addHeaders([
            "https://reputation.securepaypage.litle.com/LitlePayPage/litle-api.js",
            "https://crypto-js.googlecode.com/files/2.5.3-crypto-sha256-hmac.js",
            "http://quickui.org/release/quickui.catalog.css",
            "http://code.jquery.com/jquery-1.7.2.min.js",
            "http://quickui.org/release/quickui.js",
            "/static/css/stylesBuyPage.css",
            "/static/js/enhanceselect.js",
            "/static/js/jquery.colorbox.js",
            "/static/js/enhanceselect.js",
            "/static/js/controls/textField.js",
            "/static/js/G.js",                               
            "/static/js/pages/buypage.js"
        ]);
        
        script = """
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
                    "account_email":"sdfzzzdsfTester@test.com",
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
                
                var entityInfos = [{
                    "is_primary": true,      
                    "plans":null,
                    "entity_type": "business",
                    "creation_profile_public": false,
                    "business_name":null,
                    "address1":null,
                    "address2":null,
                    "address_city":null,
                    "address_zip":null,
                    "address_state":null,
                    "address_country":"USA"
                }];                                         
                
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
                
                $(document).ready(function() {              
                
                    $("#root").append(
                       page = G.controls.BuyPage.create()
                    )               
                });
            """       

        self.response.out.write(myTemplate.addBody(html).addScript(script).buildPage()) 

class CreateAccount(webapp.RequestHandler):
    def get(self):
        
        email = self.request.get('email')
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
        
class StorePage(webapp.RequestHandler):
    def get(self, locationCode):
        
        html = open('DealershipPage.html').read()
        
        myTemplate = HtmlTemplate()
        
        myTemplate.addHeaders([
            "http://quickui.org/release/quickui.catalog.css",
            "http://code.jquery.com/jquery-1.7.2.min.js",
            "http://quickui.org/release/quickui.js",
            "/static/css/stylesStorePage.css",
            "/static/js/jquery.colorbox.js",
            "/static/js/score1.js",
            "/static/js/score2.js",
            "/static/js/G.js",
            "/static/js/controls/stardisplay.js",
            "/static/js/controls/reviewrow.js",
            "/static/js/controls/rankresult2.js",
            "/static/js/pages/storepage.js"
        ]);
        

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
                 'reviewerName': dealership.One_Review_Name or '',
                 'reviewerLocation': dealership.One_Review_Location or '',
                 'rating': dealership.One_Review_Ranking or 0
                },
                {
                 'review': dealership.Two_Review or 'Not Found',
                 'reviewerName': dealership.Two_Review_Name or '',
                 'reviewerLocation': dealership.Two_Review_Location or '',
                 'rating': dealership.Two_Review_Ranking or 0
                },
                {
                 'review': dealership.Three_Review or 'Not Found',
                 'reviewerName': dealership.Three_Review_Name or '',
                 'reviewerLocation': dealership.Three_Review_Location or '',
                 'rating': dealership.Three_Review_Ranking or 0
                }
            ],
            'reviewCount': dealership.Total_number_of_reviews,
            'reviewSiteCount': dealership.Number_of_review_sites_with_reviews  ,
            'dealershipName': dealership.Location_Name,
            'dealershipBrand': dealership.Location_Brand or 'Brand',
            'dealershipState': dealership.Location_State or 'State',
            'averageStarRating': dealership.Average_star_ranking_across_sites,
            'address': {
                'street': dealership.Location_Address,
                'region': address
            }
        }


        top_dealerships_by_brand_query = makeQuery(filters={
            'Location_Brand': {
                'value': dealership.Location_Brand,
                'operator': '='
            } 
        }, orderBy='-Reputation_Score', fetchQty=10)


        top_dealerships_by_state_query = makeQuery(filters={
            'Location_State': {
                'value': dealership.Location_State,
                'operator': '='
            } 
        }, orderBy='-Reputation_Score', fetchQty=10)   
        
        dealership_rank_by_state = len(makeQuery(filters={
            'Location_State': {
                'value': dealership.Location_State,
                'operator': '='
            },
            'Reputation_Score': {
                'value': dealership.Reputation_Score,
                'operator': '>'
            }
        }, orderBy='-Reputation_Score', fetchQty=10000000))
        
        if dealership_rank_by_state <= 10 and not any([True for d in top_dealerships_by_state_query if d.key() == dealership.key()]):
            top_dealerships_by_state_query.insert(dealership_rank_by_state, dealership)         
 
        dealership_rank_by_brand = len(makeQuery(filters={
            'Location_Brand': {
                'value': dealership.Location_Brand,
                'operator': '='
            },
            'Reputation_Score': {
                'value': dealership.Reputation_Score,
                'operator': '>'
            }
        }, orderBy='-Reputation_Score', fetchQty=10000000))
        
        if dealership_rank_by_brand <= 10 and not any([True for d in top_dealerships_by_brand_query if d.key() == dealership.key()]):
            top_dealerships_by_brand_query.insert(dealership_rank_by_brand, dealership)  
             

        for rank, d in enumerate(top_dealerships_by_brand_query):
            data['top_dealerships_by_brand'].append({
                'highlight': d.key() == dealership.key(),  
                'locationCode': d.key().name(),                                   
                'rank': rank + 1,
                'dealership': d.Location_Name,
                'score': d.Reputation_Score
            })

        for rank, d in enumerate(top_dealerships_by_state_query):            
            data['top_dealerships_by_state'].append({
                'highlight': d.key() == dealership.key(),
                'locationCode': d.key().name(),
                'rank': rank + 1,
                'dealership': d.Location_Name,
                'score': d.Reputation_Score
            }) 

        if dealership_rank_by_state > 10:
            data['top_dealerships_by_state'].append({
                'highlight': True,
                'locationCode': dealership.key().name(),                                     
                'rank': dealership_rank_by_state,
                'dealership': dealership.Location_Name,
                'score': dealership.Reputation_Score
            })              


        if dealership_rank_by_brand > 10:
            data['top_dealerships_by_brand'].append({
                'highlight': True,
                'locationCode': dealership.key().name(),                                     
                'rank': dealership_rank_by_brand,
                'dealership': dealership.Location_Name,
                'score': dealership.Reputation_Score
            })   

                                      
        script = """
                $(document).ready(function() {
            
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
                   

        self.response.out.write(myTemplate.addScript(script).addBody(html).buildPage()) 

class Delete(webapp.RequestHandler):
    
    def get(self):
        
        #query = db.Query(Dealership).fetch(1000000)
        #toDelete = []
        #for d in query:
        #    toDelete.append(d)
        #db.delete(toDelete)
        print 'hi'

class InsertDataBig(webapp.RequestHandler):
    
    def get(self):
        
        query = db.Query(Dealership).fetch(100000000)   
        
        for d in query:
            if d.Location_Brand:
                d.Location_Brand = d.Location_Brand.upper()   
                d.save() 

        d = Dealership.get_by_key_name(str('171'))
        d.Location_Name = 'Federico Chrysler Dodge Jeep'
        
        d.save()
        
        a = Dealership.get_by_key_name(str('18'))
        a.Location_Name = 'Wilde Chrysler Jeep Dodge'
        
        a.save()
      
        t= {'B93':{'city':'CITY OF INDUSTRY', 'state':'CA', 'zip':'91748'},
        'B92':{'city':'GAINSVILLE', 'state':'TX', 'zip':'76241'},
        'B91':{'city':'THOUSAND OAKS', 'state':'CA', 'zip':'91359'},
        'B90':{'city':'SHREVEPORT', 'state':'LA', 'zip':'71135'},
        'B9':{'city':'JACKSON', 'state':'MI', 'zip':'49202'},
        'B89':{'city':'DAVENPORT', 'state':'IA', 'zip':'52808'},
        'B88':{'city':'FORT SMITH', 'state':'AR', 'zip':'72913'},
        'B87':{'city':'GRAPEVINE', 'state':'TX', 'zip':'76099'},
        'B86':{'city':'BURLINGTON', 'state':'VT', 'zip':'5402'},
        'B85':{'city':'Kansas City', 'state':'MO', 'zip':'64154'},
        'B84':{'city':'CORAL SPRING', 'state':'FL', 'zip':'33071'},
        'B83':{'city':'IRVINE', 'state':'CA', 'zip':'92618'},
        'B82':{'city':'MASSILLON', 'state':'OH', 'zip':'44646'},
        'B81':{'city':'MERRIAM', 'state':'KS', 'zip':'66203'},
        'B80':{'city':'MERRIAM', 'state':'KS', 'zip':'66203'},
        'B79':{'city':'HUMBOLDT', 'state':'IA', 'zip':'50548'},
        'B77':{'city':'HARRISBURG', 'state':'PA', 'zip':'17112'},
        'B76':{'city':'SAN CARLOS', 'state':'CA', 'zip':'94070'},
        'B75':{'city':'FLORENCE', 'state':'KY', 'zip':'41042'},
        'B74':{'city':'VERNON', 'state':'CT', 'zip':'6066'},
        'B72':{'city':'LA MESA', 'state':'CA', 'zip':'91942'},
        'B70':{'city':'GEORGETOWN', 'state':'TX', 'zip':'78626'},
        'B7':{'city':'CHESAPEAKE', 'state':'VA', 'zip':'23322'},
        'B69':{'city':'LAS VEGAS', 'state':'NV', 'zip':'89118'},
        'B67':{'city':'BUENA PARK', 'state':'CA', 'zip':'90621'},
        'B66':{'city':'TOLEDO', 'state':'OH', 'zip':'43615'},
        'B65':{'city':'NAPERVILLE', 'state':'IL', 'zip':'60540'},
        'B64':{'city':'TUSCALOOSA', 'state':'AL', 'zip':'35405'},
        'B62':{'city':'FREMONT', 'state':'CA', 'zip':'94538'},
        'B61':{'city':'FREMONT', 'state':'CA', 'zip':'94538'},
        'B60':{'city':'TUNKHANNOCK', 'state':'PA', 'zip':'18657'},
        'B6':{'city':'CITY OF INDUSTRY', 'state':'CA', 'zip':'91748'},
        'B59':{'city':'MACOMB', 'state':'MI', 'zip':'48044'},
        'B58':{'city':'BROWNSBURG', 'state':'IN', 'zip':'46112'},
        'B56':{'city':'RIDGEWAY', 'state':'VA', 'zip':'24148'},
        'B55':{'city':'MURRAY', 'state':'UT', 'zip':'84107'},
        'B53':{'city':'ROCHESTER', 'state':'NY', 'zip':'14626'},
        'B52':{'city':'LANCASTER', 'state':'CA', 'zip':'93534'},
        'B51':{'city':'DECATUR', 'state':'GA', 'zip':'30030'},
        'B5':{'city':'OKLAHOMA CITY', 'state':'OK', 'zip':'73170'},
        'B49':{'city':'WARREN', 'state':'OH', 'zip':'44482'},
        'B48':{'city':'LIVINGSTON', 'state':'TX', 'zip':'77351'},
        'B46':{'city':'BEAUMONT', 'state':'TX', 'zip':'77713'},
        'B45':{'city':'BAY CITY', 'state':'MI', 'zip':'48706'},
        'B44':{'city':'ABILENE', 'state':'TX', 'zip':'79606'},
        'B43':{'city':'NEPTUNE', 'state':'NJ', 'zip':'7753'},
        'B42':{'city':'SHEBOYGAN', 'state':'WI', 'zip':'53081'},
        'B40':{'city':'FARMERS BRANCH', 'state':'TX', 'zip':'75234'},
        'B4':{'city':'MAYS LANDING', 'state':'NJ', 'zip':'8330'},
        'B39':{'city':'OTTAWA', 'state':'IL', 'zip':'61350'},
        'B38':{'city':'HARRISONBURG', 'state':'VA', 'zip':'22871'},
        'B37':{'city':'CHICAGO', 'state':'IL', 'zip':'60618'},
        'B36':{'city':'OREGON', 'state':'OH', 'zip':'43616'},
        'B35':{'city':'SAN FRANCISCO', 'state':'CA', 'zip':'94103'},
        'B33':{'city':'KENNER', 'state':'LA', 'zip':'70062'},
        'B32':{'city':'EAST MEADOW', 'state':'NY', 'zip':'11554'},
        'B31':{'city':'VESTAL', 'state':'NY', 'zip':'13850'},
        'B30':{'city':'BOULDER', 'state':'CO', 'zip':'80301'},
        'B3':{'city':'WESTBURY', 'state':'NY', 'zip':'11590'},
        'B29':{'city':'ROYAL OAK', 'state':'MI', 'zip':'48073'},
        'B28':{'city':'WARNER ROBINS', 'state':'GA', 'zip':'31047'},
        'B27':{'city':'LAWRENCE', 'state':'KS', 'zip':'66047'},
        'B26':{'city':'AUSTIN', 'state':'TX', 'zip':'78745'},
        'B25':{'city':'SEASIDE', 'state':'CA', 'zip':'93955'},
        'B24':{'city':'SAN ANGELO', 'state':'TX', 'zip':'76904'},
        'B23':{'city':'OMAHA', 'state':'NE', 'zip':'68118'},
        'B22':{'city':'LYNNWOOD', 'state':'WA', 'zip':'98037'},
        'B20':{'city':'SOUTH HOLLAND', 'state':'IL', 'zip':'60473'},
        'B2':{'city':'INVER GROVE HEIGHTS', 'state':'MN', 'zip':'55077'},
        'B19':{'city':'MATTOON', 'state':'IL', 'zip':'61938'},
        'B18':{'city':'IRVINE', 'state':'CA', 'zip':'92618'},
        'B17':{'city':'CHULA VISTA', 'state':'CA', 'zip':'91913'},
        'B14':{'city':'BEAVERTON', 'state':'OR', 'zip':'97006'},
        'B13':{'city':'BRANFORD', 'state':'CT', 'zip':'6405'},
        'B12':{'city':'WOODBRIDGE', 'state':'VA', 'zip':'22191'},
        'B11':{'city':'LAWRENCEVILLE', 'state':'GA', 'zip':'30043'},
        'B10':{'city':'232 SHERMAN OAKS', 'state':'CA', 'zip':'91423'},
        'B1':{'city':'DWIGHT', 'state':'IL', 'zip':'60420'},
        'A99':{'city':'El Cajon', 'state':'CA', 'zip':'92020'},
        'A98':{'city':'Lompoc', 'state':'CA', 'zip':'93436'},
        'A97':{'city':'Lakewood', 'state':'CA', 'zip':'90715'},
        'A95':{'city':'San Francisco', 'state':'CA', 'zip':'94103'},
        'A94':{'city':'Marietta', 'state':'GA', 'zip':'30060'},
        'A93':{'city':'Avenel', 'state':'NJ', 'zip':'7001'},
        'A92':{'city':'Louisville', 'state':'KY', 'zip':'40299'},
        'A91':{'city':'Jasper', 'state':'IN', 'zip':'47546'},
        'A90':{'city':'St. Dixon', 'state':'CA', 'zip':'95620'},
        'A9':{'city':'Riverhead', 'state':'NY', 'zip':'11901'},
        'A89':{'city':'Davie', 'state':'FL', 'zip':'33331'},
        'A88':{'city':'Albuquerque', 'state':'NM', 'zip':'87112'},
        'A87':{'city':'Reno', 'state':'NV', 'zip':'89511'},
        'A86':{'city':'Industry', 'state':'CA', 'zip':'91748'},
        'A85':{'city':'Portland', 'state':'OR', 'zip':'97201-2464'},
        'A84':{'city':'Colorado Springs', 'state':'CO', 'zip':'80920'},
        'A83':{'city':'Westlake', 'state':'OH', 'zip':'44145'},
        'A82':{'city':'Oregon City', 'state':'OR', 'zip':'97045'},
        'A81':{'city':'Wilmington', 'state':'DE', 'zip':'19804-1190'},
        'A80':{'city':'Lindon', 'state':'UT', 'zip':'84042'},
        'A8':{'city':'Tinley Park', 'state':'IL', 'zip':'60487'},
        'A77':{'city':'St. Louis Park', 'state':'MN', 'zip':'55426'},
        'A76':{'city':'Golden Valley', 'state':'MN', 'zip':'55426'},
        'A75':{'city':'Brooklyn Park', 'state':'MN', 'zip':'55445'},
        'A74':{'city':'Minnetonka', 'state':'MN', 'zip':'55305'},
        'A73':{'city':'Brooklyn Park', 'state':'MN', 'zip':'55428'},
        'A72':{'city':'Modesto', 'state':'CA', 'zip':'95356'},
        'A71':{'city':'Columbia', 'state':'SC', 'zip':'29203'},
        'A7':{'city':'York', 'state':'PA', 'zip':'17404'},
        'A69':{'city':'MONTCLAIR', 'state':'CA', 'zip':'91763'},
        'A68':{'city':'Medford', 'state':'OR', 'zip':'97509'},
        'A67':{'city':'Anaheim', 'state':'CA', 'zip':'92806'},
        'A66':{'city':'Longview', 'state':'WA', 'zip':'98632'},
        'A64':{'city':'Grove Heights', 'state':'MN', 'zip':'55077'},
        'A63':{'city':'Sacramento', 'state':'CA', 'zip':'95821'},
        'A62':{'city':'Peoria', 'state':'AZ', 'zip':'85382'},
        'A61':{'city':'Peoria', 'state':'IL', 'zip':'85382'},
        'A60':{'city':'Sodus', 'state':'NY', 'zip':'14551'},
        'A59':{'city':'Lancaster', 'state':'WI', 'zip':'53813'},
        'A57':{'city':'Florida City', 'state':'FL', 'zip':'33034'},
        'A56':{'city':'Bridgeport', 'state':'CT', 'zip':'6606'},
        'A55':{'city':'Van Nuys', 'state':'CA', 'zip':'91401'},
        'A54':{'city':'Mesa', 'state':'AZ', 'zip':'85204'},
        'A52':{'city':'Mission Viejo', 'state':'CA', 'zip':'92692'},
        'A50':{'city':'Lewiston', 'state':'ME', 'zip':'4240'},
        'A5':{'city':'Pensacola', 'state':'FL', 'zip':'32505'},
        'A49':{'city':'Laconia', 'state':'NH', 'zip':'3246'},
        'A48':{'city':'Irvine', 'state':'CA', 'zip':'92618'},
        'A46':{'city':'Scottsdale', 'state':'AZ', 'zip':'85260'},
        'A45':{'city':'St. James', 'state':'MO', 'zip':'65559'},
        'A44':{'city':'Houston', 'state':'TX', 'zip':'77904'},
        'A43':{'city':'Woodland', 'state':'CA', 'zip':'95695'},
        'A42':{'city':'Glendale', 'state':'WI', 'zip':'53209'},
        'A41':{'city':'Fairmont', 'state':'MN', 'zip':'56031'},
        'A40':{'city':'Hardin', 'state':'MT', 'zip':'59034'},
        'A4':{'city':'Anchorage', 'state':'AK', 'zip':'99515'},
        'A39':{'city':'Las Vegas', 'state':'NV', 'zip':'89118'},
        'A38':{'city':'Highland Park', 'state':'IL', 'zip':'60035'},
        'A37':{'city':'Alhambra', 'state':'CA', 'zip':'91801'},
        'A36':{'city':'Alhambra', 'state':'CA', 'zip':'91801'},
        'A35':{'city':'Green Cove Springs', 'state':'FL', 'zip':'32043'},
        'A34':{'city':'Henderson', 'state':'NV', 'zip':'89014'},
        'A33':{'city':'Henderson', 'state':'NV', 'zip':'89011'}}
            
        for key in t:
            d = Dealership.get_by_key_name(str(key))
            d.Location_City = t[key]['city']
            d.Location_Zip = t[key]['zip']
            d.Location_State = t[key]['state']
            d.save()        
            

        
application = webapp.WSGIApplication(
                                     [
                                         ('/', MainPage),
                                         ('/delete', Delete),
                                         ('/insertbig', InsertDataBig),
                                         ('/store/([^/]+)?', StorePage),
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