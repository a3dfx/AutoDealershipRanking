$(document).ready(function() {
	G.addControl("LocationEntry", Control.sub({
		tag: 'tr',
		ref: 'locationEntry',
		inherited: {
			content: 
				[
					{
						html: 'td',
						ref: 'locationName'
					},
					{
						html: 'td',
						ref: 'address',
						content: 
							{
								html: 'a',
								ref: 'dealerPageLink'
							}
					},
					{
						html: 'td',
						ref: 'city'
					},
					{
						html: 'td',
						ref: 'state'
					},
					{
						html: 'td',
						ref: 'zip'
					},
					{
						html: 'td'
					},					
					{
						html: 'td',
						content: 
							[
								{
									html: 'a',
									ref: 'delete',
									content: 'Delete',
									css: {
										'cursor': 'pointer'
									}
								},
								{
									html: 'div',
									ref: 'price'
								}
							]
					}				
				]
		},
		locationName: Control.chain('$locationName', 'content'),
		address: Control.chain('$address', 'content'),
		city: Control.chain('$city', 'content'),
		state: Control.chain('$state', 'content'),
		zip: Control.chain('$zip', 'content'),
		price: Control.chain('$price', 'content'),
		initialize: function() {
			var self = this;
			this.inDocument(function() {
				self.$delete().click(function () {
					self.remove();
				})
			});
		}
	}))	
})