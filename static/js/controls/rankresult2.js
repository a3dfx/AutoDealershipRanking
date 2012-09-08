$(document).ready(function() {
	G.addControl("RankResult2", Control.sub({
		tag: 'tr',
		ref: 'rankRow',
		inherited: {
			content: 
				[
					{
						html: 'td',
						ref: 'rank'
					},
					{
						html: 'td',
						ref: 'dealer',
						content: 
							{
								html: 'a',
								ref: 'dealerPageLink'
							}
					},
					{
						html: 'td',
						ref: 'score'
					}				
				]
		},		
		rank: Control.property(),
		dealer: Control.property(),
		score: Control.property(),
		locationCode: Control.property(),
		highlight: Control.property(),
		initialize: function() {
			var self = this;
			this.inDocument(function() {
				if (self.highlight()) {
					self.attr({
						class: 'highlight'
					})
				}	
				self.$rank().content(self.rank());
				self.$score().content(self.score());
				self.$dealerPageLink()
					.attr({ href: '/store/' + self.locationCode() })
					.content(self.dealer());			
			});			
		}
	}))	
})