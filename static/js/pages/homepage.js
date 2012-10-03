$(document).ready(function() {
	G.addControl("Home", Control.sub({
		ref: 'htmlContainer',
		pageData: Control.property(),
		filterChosen: Control.property(),
		createUrl: function(params) {
			var url = '?';
			var goodParams = {};
			for (var key in params) {
				if (params[key] && params[key] != 'All States' && params[key] != 'All Brands') {
					url += key + '=' + encodeURIComponent(params[key]) + '&';
				}
			}
			return url.slice(0, -1);
		},		
		initialize: function() {
			/*
			$.post('https://www.blackmagicsfdcservices.appspot.com/service_call', 
				{'pwd': 'lior1213wfITr8Ik6Mp3P8wgBtPXF11le', 'uid': 'lior.gotesman@reputation.com.dev', 
				'form_fields': JSON.stringify({

	            'service_name': 'ContentInsert',
	
	            'work_order_id': "d366ab70-d07d-4e9a-a728-db8db2a4b411",
	
	            'membership_id': '558493',
	
	            'fulfillment_notes': 'there are notes',
	
	            'master_profile': 'master profile goeshere',
	            'writer_id': '12341234',
	
	            'expedite': "False",
	
	            'contentCreationResults': [
	
	                {
	
	                    "id": "6c0a4d15-3866-4883-9469-73a10961662a",
	
	                    "content": "content is here"
	
	                },
	
	                {
	
	                    "id": "6040c227-7adb-4881-832b-42ddae9f7ac8",
	
	                    "content": "This is my content"
	
	                }
	
	            ]

			})}, function(data) {
				console.log(data)
			});
			*/

			$('#rankResultsTableHole').append(
				$table = $('<table>').attr({
					cellpadding: '0',
					cellspacing: '0'
				}).append(
					$('<tr>').append(
						$('<th>').append(
							'Rank'
						),
						$('<th>').addClass('dealer').append(
							'Dealership'
						),
						$('<th>').append(
							'State'
						),
						$('<th>').append(
							'Number of Reviews'
						),
						$('<th>').append(
							'Score'
						)								
					)				
				)
			);
			var self = this;
			this.inDocument(function() {
				var renderSelectionList = function(listName, listType, allOption, elemHoleId) {
					self.pageData()[listName].unshift(allOption);
					if (self.filterChosen()[listType] != allOption) {
						self.pageData()[listName].unshift(self.filterChosen()[listType]);
					}				
					for (var i=0; i<self.pageData()[listName].length; i++) {
						$('#' + elemHoleId).append(
							$('<option>').text(
								self.pageData()[listName][i]
							)
						);
					}					
				}
				renderSelectionList('brands_list', 'brand', 'All Brands', 'brandSelectElem');	
				renderSelectionList('states_list', 'state', 'All States', 'stateSelectElem');				
				bind = function() {
					$.map($('.selectparent li a'), function(elem) {
						$(elem).click(function() {
							if ($(this).parent().parent().parent().parent().parent().attr('id') == 'brandSelect') {
								self.filterChosen().brand = $(elem).html() != 'All Brands' ? $(elem).html(): null;
							} else {
								self.filterChosen().state = $(elem).html() != 'All States' ? $(elem).html(): null;;
							}
							var url = self.createUrl({
								brand: self.filterChosen().brand,
								state: self.filterChosen().state
							})
							document.location = '/rank' + url;
						});
					});	
				}
				setTimeout(bind, 1000)
				for (var i=0; i<self.pageData().rankResults.length; i++) {
					var data = self.pageData().rankResults[i];
					$table.append(
						G.controls.RankResult.create()
							.rank(data.rank)
							.dealer(data.dealership)
							.state(data.state)
							.reviews(data.numberReviews)
							.score(data.score)	
							.hrefPath(data.hrefPath)
					)					
				}				
			});
		}
	}))	
})