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
			$.post('http://localhost:8087/service_call', {
				'form_fields': JSON.stringify({
				    "results": [
				                {
				                    "subTaskId": "2cb29191-0d4f-44f3-a5b2-d208fd5f04e8",
				                    "content": "QA Test -- Bio2\r\n\r\nEditor -- Bio2",
				                    "status": 2,
				                    "thirdPartyContentId": "11927",
				                    "workerInfo": {
				                        "workerId": "9",
				                        "workerName": "editor1"
				                    }
				                },
				                {
				                    "subTaskId": "05ebdc4f-be4a-4ada-901b-d108f686d2a1",
				                    "content": "QA Test -- Bio1\r\n\r\nEditor -- Bio1",
				                    "status": 2,
				                    "thirdPartyContentId": "11927",
				                    "workerInfo": {
				                        "workerId": "9",
				                        "workerName": "editor1"
				                    }
				                }
				            ],
				            "taskResult": {
				                "taskId": "035f7e70-6ddb-48d4-81c1-ae8090a25d6b",
				                "rdcCorrelationId": "32eedcd1-9da0-4191-98a4-c8c14af106f2",
				                "notes": null
				            },
				            "event": 5
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
						$('<th>').addClass('state').append(
							'State'
						),
						$('<th>').addClass('numReviews').append(
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