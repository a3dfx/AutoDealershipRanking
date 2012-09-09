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
        
        print 'hey'            

        
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
