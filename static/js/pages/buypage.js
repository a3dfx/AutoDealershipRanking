$(document).ready(function() {
	G.addControl("BuyPage", Control.sub({
		pageData: Control.property(),
		ccNumber: Control.property(),
		planChosen: Control.property(),
		userParams: Control.property(),
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
            // Get entity data
            var entity = entityInfos[0];
            for (var key in entityInfos[0]) {
                var value = $('#' + key).val();
                if(value) {
                    entityInfos[0][key] = value;
                }             
            }  
            
            planMapping = {
            	'Base': {"5" : "11143"},
            	'Gold': {"5" : "11151"},
            	'Platinum': {"5" : "11152"}
            }

            entityInfos[0].plans = planMapping[this.planChosen()];
            
            for (var key in accountInfo) {
                var value = $('#' + key).val();
                if(value) {
                    accountInfo[key] = value;
                }             
            }                  
            
            $.extend(accountInfo, {
                litle_type: document.getElementById('response$type').value,
                username: accountInfo.account_email,
                password: G.randomPassword()
            });
            
            accountInfo.exp_month = $('#expMonthSelect .enhancedtrigger.enhancedtrigger').html();
            accountInfo.exp_year = $('#expYearSelect .enhancedtrigger.enhancedtrigger').html();
        },
		sendRequestToOptimus: function() {
			var self = this;
			this.configureAPI();
            var apiSecret = "sdklw9ASas9Ajd9jd/cjk9As";
            var url;
            var urlData;
            var dataEncoded;
            
            url = 'http://appservices.reputationdefender.com/AccountManagement/createAccount' +
            	"?api_key=ReputationSF" +
            	"&api_secret=sdklw9ASas9Ajd9jd/cjk9As" +
            	'&accountInfo=' + encodeURIComponent(JSON.stringify(accountInfo)) +
            	'&entityInfos=' + encodeURIComponent(JSON.stringify(entityInfos)) +
            	'&callback=?';
            /*
            url = 'http://appservices.reputationdefender.com/AccountManagement/createAccount';
            data = 'accountInfo=' + JSON.stringify(accountInfo) + 
                'entityInfos=' + JSON.stringify(entityInfos); 
            dataEncoded = '?accountInfo=' + encodeURIComponent(JSON.stringify(accountInfo)) + 
                '&entityInfos=' + encodeURIComponent(JSON.stringify(entityInfos)); 

            var oUrl = this.hashUrl(url, data, dataEncoded, apiSecret);
			*/
            
            console.log(url, accountInfo, entityInfos)
            
            $.getJSON(url, function(response) {
            	console.log(response)
            	if (response.message == "Not allowed") {
            		$('#loadingGif').hide();
                    alert("Payment did not go through");
                    $("#accountNumberField").val(self.ccNumber());
                } else if (response.result.status == 1) {
                	self.userParams().optimusUserId = response.result.userId;
                	console.log(self.userParams())
        			$.get(self.createGetUrl(self.userParams()), function(data) {
        				$('#loadingGif').hide();
        				alert("Successful and Saved");
        				document.location = '/';
        			});	
                } else {
                	$('#loadingGif').hide();
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
	            alert(responseCodes[1])
	            $("#accountNumberField").val(self.ccNumber());
	        }   
	        function onErrorAfterLitle (response) {
	            setLitleResponseFields(response);
	            $("#accountNumberField").val(self.ccNumber());
	            $('#loadingGif').hide();
	            alert(responseCodes[response.response])
	            return false;
	        }  			
			
            setLitleResponseFields({"response":"", "message":""});
            
            var tokenUrl = "https://reputation.securepaypage.litle.com"
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
             "url" : "https://reputation.securepaypage.litle.com"
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
		initialize: function() {
			var self = this;
			this.inDocument(function() {				
    			$("#emailTextFieldHole").append(
	    			$emailTextField = G.controls.TextField.create()
						.id('account_email')
						.validateEmail(true)
						.required(false)
						.placeHolderText('Email Address')
						.attr({
							name: 'Email',
							class: 'field'
						})
				);
    			$("#dealershipNameTextFieldHole").append(
    	    		$dealershipName = G.controls.TextField.create()
						.id('business_name')
						.required(false)
						.placeHolderText('Dealership Name')
						.attr({
							name: 'DealershipName',
							class: 'field'
						})    			
    			);
    			$("#personName").append(
    					$personName = G.controls.TextField.create()
						.id('account_first_name')
						.required(false)
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
						.required(false)
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
						.required(false)
						.placeHolderText('Card Number')
						.css({ 'width': 300 })
						.attr({
							name: 'ccNum',
							class: 'field'
						})
				);
    			
    			$("#cardName").append(
    	    			$cardName = G.controls.TextField.create()
    						.id('first_name')
    						.required(false)
    						.css({ 'width': 300 })
    						.placeHolderText('Name on card')
    						.attr({
    							name: 'cardName',
    							class: 'field'
    						})
    				);
    			
    			$("#address").append(
    	    			$address = G.controls.TextField.create()
    						.id('address1')
    						.required(false)
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
    						.required(false)
    						.placeHolderText('City')
    						.attr({
    							name: 'city',
    							class: 'field'
    						})
    				);
    			
    			$("#state").append(
    	    			$state = G.controls.TextField.create()
    						.id('address_state')
    						.required(false)
    						.placeHolderText('State/Province')
    						.attr({
    							name: 'state',
    							class: 'field'
    						})
    				);
    			
    			$("#zip").append(
    	    			$zip = G.controls.TextField.create()
    						.id('address_zip')
    						.required(false)
    						.placeHolderText('ZIP/Postal Code')
    						.attr({
    							name: 'zip',
    							class: 'field'
    						})
    				);
				$('#submitButton').css({
					'cursor': 'pointer'
				}).click(function() {
					$('#loadingGif').show();
					$expMonth = $('#expMonthSelect .enhancedtrigger.enhancedtrigger').html();
					$expYear = $('#expYearSelect .enhancedtrigger.enhancedtrigger').html();
					$packageSelect = $('#packageSelect .enhancedtrigger.enhancedtrigger').html();
					self.planChosen($packageSelect);
					var inps = [
					    $city.getValidInput(),
					    $zip.getValidInput(),
					    $emailTextField.getValidInput(),
					    $dealershipName.getValidInput(),
					    $cardName.getValidInput(),
					    $ccNum.getValidInput(),
					    $state.getValidInput(),
					    $personName.getValidInput(),
					    $phoneNumber.getValidInput()
					];
					if (self.inputsValid(inps)) {
						self.userParams({
    						email: $emailTextField.getValidInput(),
    						dealershipName: $dealershipName.getValidInput(),
    						personName: $personName.getValidInput(),
    						phoneNumber: $phoneNumber.getValidInput(),
    						packageSelected: $packageSelect,
    						optimusUserId: ''
        				});
						self.ccNumber($ccNum.getValidInput());
						self.processPayment();
					} else {
						$('#loadingGif').hide();
						alert("Please enter valid input for each field.")
					}

				});
    			
			});
		}
	}))	
})