$(document).ready(function() {
	G.addControl("RankResult", Control.sub({
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
						ref: 'state'
					},
					{
						html: 'td',
						ref: 'reviews'
					},
					{
						html: 'td',
						ref: 'score'
					}				
				]
		},
		rank: Control.property(),
		dealer: Control.property(),
		state: Control.property(),
		reviews: Control.property(),
		score: Control.property(),
		hrefPath: Control.property(),
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
				self.$state().content(self.state());
				self.$reviews().content(self.reviews());
				self.$score().content(self.score());
				self.$dealerPageLink().attr({ href: self.hrefPath() }).content(self.dealer());			
			});
		}
	}))	
})