$(document).ready(function() {
	G.addControl("BuyPage", Control.sub({
		pageData: Control.property(),
		ccNumber: Control.property(),
		planChosen: Control.property(),
		userParams: Control.property(),
		saleTotal: Control.property(),
		planId: Control.property(),
		userId: Control.property(),
		entityAdded: Control.property(),
		entityInfos: Control.property(),
		addEntityInfo: function() {
			var self = this;
			var data = self.entityAdded();
            var entityInfo = {
                "is_primary": data.is_primary,
                "plans":data.plans,
                "entity_type": "business",
                "creation_profile_public": false,
                "business_name":data.name,
                "address1":data.address,
                "address2":null,
                "address_city":data.city,
                "address_zip":data.zip,
                "address_state":data.state,
                "address_country": 'USA'
            };
            self.entityInfos().push(entityInfo);
		},
		removeEntityInfo: function(entityName) {
			var self = this;
			var newEntityInfos = [];
            for (var i=0; i<self.entityInfos().length; i++) {
            	var entity = self.entityInfos()[i];
            	if (entity.business_name != entityName) {
            		entity.is_primary = false;
            		newEntityInfos.push(entity);
            	}
            }
            if (newEntityInfos.length) {
            	newEntityInfos[0].is_primary = true;
            }
            self.entityInfos(newEntityInfos);
		},		
		createGetUrl: function(params) {
			var url = '';
			var goodParams = {};
			for (var key in params) {
				if (params[key]) {
					url += key + '=' + encodeURIComponent(params[key]) + '&';
				}
			}
			return '/createAccount?' + url.slice(0, -1);
		},
		hashUrl: function(url, data, dataEncoded, apiSecret) {
	        var date = new Date; // Generic JS date object
	        var unixtime_ms = date.getTime(); // Returns milliseconds since the epoch
	        var unixtime = parseInt(unixtime_ms / 1000);
	        var hmac = Crypto.HMAC(
	            Crypto.SHA256, 
	            unixtime + data, 
	            apiSecret
	        );
	        return url +
	            dataEncoded +
	            "&api_sig=" + hmac + 
	            "&api_key=ReputationSF" + 
	            "&api_timestamp=" + unixtime +
	            "&callback=?"
		},
        configureAPI: function() {
            
            for (var key in accountInfo) {
                var value = $('#' + key).val();
                if(value) {
                    accountInfo[key] = value;
                }             
            }                  
            
            $.extend(accountInfo, {
                litle_type: document.getElementById('response$type').value,
                username: accountInfo.account_email,
                password: G.randomPassword(),
                exp_month: $('#monthYear').val(),
                exp_year: $('#expYear').val()
            });

        },
		sendRequestToOptimus: function() {
			var self = this;
			this.configureAPI();
            var apiSecret = "rdi9GRCV/a9W5y1eAwSM0Asd";
            var url;
            var urlData;
            var dataEncoded;         
            
            url = 'http://qaservices.reputationdefender.com/AccountManagement/createAccount' +
            	"?api_key=ReputationSF" +
            	"&api_secret=rdi9GRCV/a9W5y1eAwSM0Asd" +
            	'&accountInfo=' + encodeURIComponent(JSON.stringify(accountInfo)) +
            	'&entityInfos=' + encodeURIComponent(JSON.stringify(self.entityInfos())) +
            	'&callback=?';
            /*
            url = 'http://appservices.reputationdefender.com/AccountManagement/createAccount';
            data = 'accountInfo=' + JSON.stringify(accountInfo) + 
                'entityInfos=' + JSON.stringify(entityInfos); 
            dataEncoded = '?accountInfo=' + encodeURIComponent(JSON.stringify(accountInfo)) + 
                '&entityInfos=' + encodeURIComponent(JSON.stringify(entityInfos)); 

            var oUrl = this.hashUrl(url, data, dataEncoded, apiSecret);
			*/
            
            console.log(url, accountInfo, self.entityInfos())
            
            $.getJSON(url, function(response) {
            	console.log(response)
            	if (response.message == "Not allowed") {
            		$('#loadingGif').hide();
            		$submitButton.enable();
                    alert("Payment did not go through");
                    $("#accountNumberField").val(self.ccNumber());
                } else if (response.result.status == 1) {
                	self.userParams().optimusUserId = response.result.userId;
                	console.log(self.userParams())
        			$.get(self.createGetUrl(self.userParams()), function(data) {
        				$('#loadingGif').hide();
        				$submitButton.enable();
        				document.location = '/confirmation';
        			});	
                } else {
                	$('#loadingGif').hide();
                	$submitButton.enable();
                	alert(statusCodes[response.result.status]);
                	$("#accountNumberField").val(self.ccNumber());
                }
            });			
		},
		processPayment: function() {
			var self = this;
	        function setLitleResponseFields (response) {
	            document.getElementById('response$code').value = response.response;
	            document.getElementById('response$message').value = response.message;
	            document.getElementById('response$responseTime').value = response.responseTime;
	            document.getElementById('response$litleTxnId').value = response.litleTxnId;
	            document.getElementById('response$type').value = response.type;
	        }
	        function submitAfterLitle (response) {
	            setLitleResponseFields(response);
	            accountInfo['litle_paypageRegistrationId'] = response.paypageRegistrationId;                      
	            self.sendRequestToOptimus();
	        }
	        function timeoutOnLitle () { 
	        	$('#loadingGif').hide();
	        	$submitButton.enable();
	            alert(responseCodes[1])
	            $("#accountNumberField").val(self.ccNumber());
	        }   
	        function onErrorAfterLitle (response) {
	            setLitleResponseFields(response);
	            $("#accountNumberField").val(self.ccNumber());
	            $('#loadingGif').hide();
	            $submitButton.enable();
	            alert(responseCodes[response.response])
	            return false;
	        }  			
			
            setLitleResponseFields({"response":"", "message":""});
            
            var tokenUrl = "https://cert01.securepaypage.litle.com"
            var tokenUser = "REPDEFTKN"
            var tokenPayPageId = "vqDVQEjr87ERQZp9"
            var tokenKey = "700000008870"
            var tokenMerchantId = "055400"
            var tokenReportGroup = "repdeftoken"
        
            var litleFormFields = {
                "accountNum" : document.getElementById('accountNumberField'), 
                "paypageRegistrationId":document.getElementById('response$paypageRegistrationId'),
                "bin" :document.getElementById('response$bin')
            };
            var litleRequest = {
             "paypageId" : document.getElementById("request$paypageId").value,
             "reportGroup" : document.getElementById("request$reportGroup").value,
             "orderId" : document.getElementById("request$orderId").value,
             "id" : document.getElementById("request$merchantTxnId").value,
             "url" : "https://cert01.securepaypage.litle.com"
            }

            if (typeof sendToLitle == 'function') {
            	sendToLitle(litleRequest, litleFormFields, submitAfterLitle, onErrorAfterLitle, timeoutOnLitle, 3000);      
            } else {
                alert("Litle API not working");
            }			
		},
	    inputsValid: function(inpList) {
	    	var allInpsValid = true;
	    	for (var i=0; i<inpList.length; i++) {
	    		if (!inpList[i]) {
	    			allInpsValid = false;
	    		}
	    	}
	    	return allInpsValid;
	    },	
	    planSelected: function(plan) {
	    	var self = this;
	    	if (plan == 'gold') {
	    		$('#goldSelect').css({
	    			'border': '3px solid #2E7BB1'
	    		});
	    		$('#baseSelect').css('border', '');
	    		$('#platinumSelect').css('border', '');
	    	} else if (plan == 'base') {
	    		$('#baseSelect').css({
	    			'border': '3px solid #2E7BB1'
	    		});	
	    		$('#goldSelect').css('border', '');
	    		$('#platinumSelect').css('border', '');	    		
	    	} else if (plan == 'platinum') {
	    		$('#platinumSelect').css({
	    			'border': '3px solid #2E7BB1'
	    		});	
	    		$('#baseSelect').css('border', '');
	    		$('#goldSelect').css('border', '');	    		
	    	}
            planMapping = {
            	'base': {'price': 49, 'plan': {"7" : "13861"}},
            	'gold': {'price': 249, 'plan': {"7" : "13862"}},
            	'platinum': {'price': 749, 'plan': {"7" : "13863"}}
            }		
            self.saleTotal(planMapping[plan].price)
            self.planId(planMapping[plan].plan);
            var totalPrice = $('#totalPrice').html(self.saleTotal());
            totalPrice.formatCurrency();                       
	    },
	    onSubmit: function() {
	    	var self = this;
			$('#loadingGif').show();
			$expMonth = $('#expMonthSelect').html();
			$expYear = $('#expYearSelect').html();
			//$packageSelect = $('#packageSelect').html();
			//self.planChosen($packageSelect);
            var entityData = {
            	is_primary: true,
            	plans:      self.planId(),
            	name:       $dealershipName.getValidInput()
            }
            self.entityAdded(entityData);
            self.addEntityInfo(entityData); 			
			var inps = [
			    $city.getValidInput(),
			    $zip.getValidInput(),
			    $emailTextField.getValidInput(),
			    $dealershipName.getValidInput(),
			    //$cardName.getValidInput(),
			    $ccNum.getValidInput(),
			    $state.getValidInput(),
			    $address.getValidInput(),
			    $personName.getValidInput(),
			    $phoneNumber.getValidInput()
			];
			if (self.inputsValid(inps)) {
				//if (self.entityInfos().length) {
					self.userParams({
						email: $emailTextField.getValidInput(),
						personName: $personName.getValidInput(),
						phoneNumber: $phoneNumber.getValidInput(),
						optimusUserId: ''
					});
					self.ccNumber($ccNum.getValidInput());
					self.processPayment();
				//} else {
				//	$('#loadingGif').hide();
				//	$submitButton.enable();
					//alert("Must add a location before submitting form.")					
				//}
			} else {
				$('#loadingGif').hide();
				$submitButton.enable();
				//alert("Please enter valid input for each field.")
			}	    	
	    },
	    addLocation: function() {
	    	var self = this;
	    	var packageSelected = $("#packageSelecter").val()
            planMapping = {
            	'Base': {'price': 49, 'plan': {"7" : "13861"}},
            	'Gold': {'price': 249, 'plan': {"7" : "13862"}},
            	'Platinum': {'price': 749, 'plan': {"7" : "13863"}}
            }			            
            if (!self.saleTotal()) {
            	self.saleTotal(planMapping[packageSelected].price) 
            } else {
            	self.saleTotal(self.saleTotal() + planMapping[packageSelected].price)
            }
            var entityData = {
            	is_primary: !self.entityInfos().length,
            	plans:      planMapping[packageSelected].plan,
            	name:       $locName.getValidInput(),
            	address:    $locAddress.getValidInput(),
            	city:       $locCity.getValidInput(),
            	state:      $locState.getValidInput(),
            	zip:        $locZip.getValidInput()
            }
            self.entityAdded(entityData);
            self.addEntityInfo(entityData);
            var totalPrice = $('#totalPrice').html(self.saleTotal());
            totalPrice.formatCurrency();
            var price = planMapping[packageSelected].price;
			$('#locationEntryTable').append(
				$locationEntry = G.controls.LocationEntry.create()
					.locationName($locName.getValidInput())
					.address($locAddress.getValidInput())
					.city($locCity.getValidInput())
					.state($locState.getValidInput())
					.zip($locZip.getValidInput())
					.price('$' + price)
			);	 
			$locationEntry.$delete().click(function() {
				self.removeEntityInfo(entityData.name);
				self.saleTotal(self.saleTotal() - price)
	            var totalPrice = $('#totalPrice').html(self.saleTotal());
	            totalPrice.formatCurrency();	    				
			})
			$locName.content('');
			$locAddress.content('');
			$locCity.content('');
			$locState.content('');
			$locZip.content('');	    	
	    },
		initialize: function() {
			var self = this;
			this.inDocument(function() {
				self.entityInfos([]);
    			$("#emailTextFieldHole").append(
	    			$emailTextField = G.controls.TextField.create()
						.id('account_email')
						.validateEmail(true)
						.required(true)
						.bgColorOnFocus('#EDF6FD')
						.placeHolderText('Email Address')
						.attr({
							name: 'Email',
							class: 'field'
						})
				);
    			$("#dealershipName").append(
    	    		$dealershipName = G.controls.TextField.create()
						.id('business_name')
						.required(true)
						.bgColorOnFocus('#EDF6FD')
						.placeHolderText('Dealership Name')
						.attr({
							id: 'dealershipName',
							name: 'DealershipName',
							class: 'field'
						})    			
    			);
    			$("#personName").append(
    					$personName = G.controls.TextField.create()
						.id('account_first_name')
						.required(true)
						.bgColorOnFocus('#EDF6FD')
						.placeHolderText('Your Name')
						.attr({
							id: 'name',
							name: 'Name',
							class: 'field'
						})
				);
    			
    			$("#phoneNumber").append(
    					$phoneNumber = G.controls.TextField.create()
						.id('phone')
						.bgColorOnFocus('#EDF6FD')
						.required(true)
						.placeHolderText('Phone Number')
						.attr({
							id: 'phone',
							name: 'Phone',
							class: 'field'
						})
				);    			
    			
    			$("#ccNum").append(
	    			$ccNum = G.controls.TextField.create()
						.id('accountNumberField')
						.required(true)
						.bgColorOnFocus('#EDF6FD')
						.placeHolderText('Card Number')
						.css({ 'width': 300 })
						.attr({
							name: 'ccNum',
							class: 'field'
						})
				);
    			
    			/*
    			$("#cardName").append(
    	    			$cardName = G.controls.TextField.create()
    						.id('first_name')
    						.required(true)
    						.bgColorOnFocus('#EDF6FD')
    						.css({ 'width': 300 })
    						.placeHolderText('Name on card')
    						.attr({
    							name: 'cardName',
    							class: 'field'
    						})
    				);
    			*/
    			$("#address").append(
    	    			$address = G.controls.TextField.create()
    						.id('address1')
    						.required(true)
    						.bgColorOnFocus('#EDF6FD')
    						.css({ 'width': 300 })
    						.placeHolderText('Address')
    						.attr({
    							name: 'address',
    							class: 'field'
    						})
    				);    			
    			
    			$("#city").append(
    	    			$city = G.controls.TextField.create()
    						.id('address_city')
    						.required(true)
    						.bgColorOnFocus('#EDF6FD')
    						.placeHolderText('City')
    						.attr({
    							name: 'city',
    							class: 'field'
    						})
    				);
    			
    			$("#state").append(
    	    			$state = G.controls.TextField.create()
    						.id('address_state')
    						.required(true)
    						.bgColorOnFocus('#EDF6FD')
    						.placeHolderText('State/Province')
    						.attr({
    							name: 'state',
    							class: 'field'
    						})
    				);
    			
    			$("#zip").append(
    	    			$zip = G.controls.TextField.create()
    						.id('address_zip')
    						.required(true)
    						.bgColorOnFocus('#EDF6FD')
    						.placeHolderText('ZIP/Postal Code')
    						.attr({
    							name: 'zip',
    							class: 'field'
    						})
    				);
    			
    			$("#locName").append(
	    			$locName = G.controls.TextField.create()
						.id('location_name')
						.required(true)
						.attr({
							name: 'location_name',
							class: 'field'
						})
    			);
    			
    			$("#locAddress").append(
	    			$locAddress = G.controls.TextField.create()
						.id('location_address')
						.required(true)
						.attr({
							name: 'location_address',
							class: 'field'
						})
        			);
    			$("#locCity").append(
	    			$locCity = G.controls.TextField.create()
						.id('location_city')
						.required(true)
						.attr({
							name: 'location_city',
							class: 'field'
						})
        			);
    			$("#locState").append(
	    			$locState = G.controls.TextField.create()
						.id('location_state')
						.required(true)
						.attr({
							name: 'location_state',
							class: 'field'
						})
        			);
    			$("#locZip").append(
	    			$locZip = G.controls.TextField.create()
						.id('location_zip')
						.required(true)
						.attr({
							name: 'location_zip',
							class: 'field'
						})
    			);    
    			
    			$('#baseSelect').click(function() {
    				self.planSelected('base');
    			});
    			$('#goldSelect').click(function() {
    				self.planSelected('gold');
    			});
    			$('#platinumSelect').click(function() {
    				self.planSelected('platinum');
    			});
    			self.planSelected('gold');
    			$('#addLocationButton').click(function() {
					var inps = [
					    $locName.getValidInput(),
					    $locAddress.getValidInput(),
					    $locCity.getValidInput(),
					    $locState.getValidInput(),
					    $locZip.getValidInput()
					]; 
					;
					if (self.inputsValid(inps)) {	
						self.addLocation();
					} else {
						//alert('Must fill all fields to add a location');
					}
    			})
    			$('#submitButton').append(
    				$submitButton = G.controls.SubmitButton
    					.create('Complete Purchase')
    					.click(function() {
    						$submitButton.disable();
	    					self.onSubmit();
	    				})
    			)
    			
			});
		}
	}))	
})