$(document).ready(function() {
	G.addControl("StorePage", Control.sub({
		ref: 'htmlContainer',
		pageData: Control.property(),
		initialize: function() {
			var self = this;
			$rankResultsTableBrand = $("#topStoresByBrandTableHole");
			$rankResultsTableState = $("#topStoresByStateTableHole");
			$personReviewsTable = $('#personReviewsTableHole');
			$addressDiv = $("#address_hole");
			this.inDocument(function() {
				pageData = self.pageData()
				$("#reviewCountHole").append(pageData.reviewCount);
				$("#reviewSitesCountHole").append(pageData.reviewSiteCount);
				$("#dealershipNameHole").append(pageData.dealershipName);
				$("#dealershipBrandNameHole").append(pageData.dealershipBrand);
				$("#dealershipStateHole").append(pageData.dealershipState);
				$("#listingsLink").attr({ href: '/publicranking/' + pageData.location_code });
				$("#backToListingsButton").attr({ href: '/publicranking/' + pageData.location_code });
				$("#averageRatingStarDisplayHole").append(
					G.controls.StarDisplay.create()
						.rating(pageData.averageStarRating)
						.quarterStarPath('/static/images/star_large_quarter.png')
						.halfStarPath('/static/images/star_large_half.png')
						.threeQuartersStarPath('/static/images/star_large_threequarters.png')
						.fullStarPath('/static/images/star_large_full.png')
						.emptyStarPath('/static/images/star_large_empty.png')
				)	
				for (var i=0; i<3; i++) {
					$personReviewsTable.append(
						G.controls.ReviewRow.create()
							.review(pageData.reviews[i].review)
							.reviewDate(pageData.reviews[i].reviewDate)
							.reviewerName(pageData.reviews[i].reviewerName)
							.reviewerLocation(pageData.reviews[i].reviewerLocation)
							.rating(pageData.reviews[i].rating)					
					);					
				}
				$addressDiv.append(
					$('<div>').append(
						pageData.address.street
					),
					$('<div>').append(
						pageData.address.region
					)
				);
				var top_dealerships_by_brand = pageData.top_dealerships_by_brand;
				for (var i=0; i<top_dealerships_by_brand.length; i++) {
					var data = top_dealerships_by_brand[i];
					$rankResultsTableBrand.append(
						G.controls.RankResult2.create()
							.rank(data.rank)
							.dealer($('<a>').append(data.dealership))
							.score(data.score)	
							.highlight(data.highlight)
							.locationCode(data.locationCode)
					)					
				}	
				var top_dealerships_by_state = pageData.top_dealerships_by_state;
				for (var i=0; i<top_dealerships_by_state.length; i++) {
					var data = top_dealerships_by_state[i];
					$rankResultsTableState.append(
						G.controls.RankResult2.create()
							.rank(data.rank)
							.dealer($('<a>').append(data.dealership))
							.score(data.score)
							.highlight(data.highlight)
							.locationCode(data.locationCode)
					)					
				}				
			});			
			
		}
	}))	
})