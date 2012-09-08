$(document).ready(function() {
	G.addControl("DealershipResultRow", Control.sub({
		inherited: {
			content: {
				html: 'div',
				ref: 'row',
				content:
					[
					 	{
					 		html: 'a',
					 		ref: 'button',
					 		content: 'View Ranking'
					 	},
					 	{
					 		html: 'h1',
					 		ref: 'dealershipName',
					 		css: {
					 			'cursor': 'pointer'
					 		}
					 	},
					 	{
					 		html: 'span',
					 		ref: 'addressSection'
					 	}
					 ]
			}
		},
		hrefPath: Control.property(),
		name: Control.property(),
		address: Control.property(),
		initialize: function() {
			var self = this;
			this.inDocument(function() {
				self.$button().attr({ href: self.hrefPath()});
				self.$dealershipName().content(self.name()).click(function() {
					document.location = self.hrefPath();
				});
				self.$addressSection().content(self.address());			
			});
		}
	}))	
})