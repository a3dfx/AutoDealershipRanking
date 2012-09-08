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
							document.location = '/' + url;
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