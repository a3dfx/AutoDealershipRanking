$(document).ready(function() {
	G.addControl("FindDealershipPage", Control.sub({
		ref: 'htmlContainer',
		pageData: Control.property(),	
		createGetUrl: function(params) {
			var url = '';
			var goodParams = {};
			for (var key in params) {
				if (params[key]) {
					url += key + '=' + encodeURIComponent(params[key]) + '&';
				}
			}
			return '/finddealer?' + url.slice(0, -1);
		},
		renderResults: function(data) {
			data = $.parseJSON(data);
			if (data.zipFilter) {
				$message = $('<div>').addClass('header').append(
					'Dealers in ZIP Code ',
					$('<span>').append(
						'"' + data.zipFilter + '"'
					)
				);
			} else {
				$message = $('<div>').addClass('header').append(
					'Dealers in State ',
					$('<span>').append(
						'"' + data.stateFilter + '"'
					)
				);					
			}			
			if (data.dealerships_list.length) {
				$('#resultsHole').empty().append(
					$message
				);  
				for (var i=0; i<data.dealerships_list.length; i++) {
					d = data.dealerships_list[i]
					$('#resultsHole').append(
						G.controls.DealershipResultRow.create()
							.hrefPath(d.hrefPath)
							.name(d.name)
							.address(d.address)
					)
				} 					
			} else {
				$('#resultsHole').empty().append(
					$message,
					$('<div>').addClass('noResults').append(
						$('<h1>').append(
							'No dealerships could be found matching your criteria.'
						),
						'Please call 1-888-568-7702 to find out how to have your dealership scored or enter a new search criteria'
					)					
				);
			}		
		},
		initialize: function() {
			var self = this;
			this.inDocument(function() {				
    			$("#zipTextFieldHole").append(
	    			$zipTextField = G.controls.TextField.create()
						.id('zipTextField')
						.errorMessage('Enter a valid Zip')
						.required(false)
						.placeHolderText('ZIP')
						.attr({
							name: 'ZIP',
							class: 'field'
						})
				);
				$("#cityTextFieldHole").append(
		    		$cityTextField = G.controls.TextField.create()
						.id('cityTextField')
						.errorMessage('Enter a valid City')
						.required(false)
						.placeHolderText('City')
						.attr({
							name: 'City',
							class: 'field'
						})				
				);
				
				for (var i=0; i<self.pageData().states_list.length; i++) {
					$('#stateSelectElem').append(
						$('<option>').text(
							self.pageData().states_list[i]
						)
					);
				}
    			
				$('#searchButton').css({
					'cursor': 'pointer'
				}).click(function() {
					$stateSelected = $('.enhancedtrigger.enhancedtrigger').html()
	    			if (($cityTextField.getValidInput() && $stateSelected != 'Select State') || $zipTextField.getValidInput()) {
	    				$stateSelected = $stateSelected == 'Select State' ? '' : $stateSelected
	    				var params = {
    						city: $cityTextField.getValidInput(),
    						zip: $zipTextField.getValidInput(),
    						state: $stateSelected
	    				}
	    				$.get(self.createGetUrl(params), function(data) {
	    					self.renderResults(data);
	    				})
	    			} else {
	    				alert('Please submit a valid address')
	    			}
				});
				
			});
		}
	}))	
})