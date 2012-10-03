$(document).ready(function() {
	G.addControl("SubmitButton", Control.sub({
		inherited: {
			css: {
				"font-family": "museo-sans-300",
				"outline": "medium none",
				'width': '170px'
			},			
			content: 
				{
					html: "button",
					ref: "button",
					content: "Submit",
					attr: {
						'class': "button green"
					},
					css: {
						'cursor': 'pointer'
					}
				}
		},
		initialize: function() {
			var self = this;
			this.$button().hover(
				function() {
					self.$button().css({
						"text-shadow": "0 1px 3px #A3A19E"
					})
				},
				function() {
					self.$button().css({
						"text-shadow": "none"
					})
				}				
			)
		},
		content: Control.property(function(text) {
	    	if (text == undefined) {
	    		return text
	    	} else {
	    		this.$button().content(text)
	    		return this
	    	}				
		}),
		disable: function() {
			this.$button().attr({
				disabled: "disabled"
			})
		},
		enable: function() {
			this.$button().removeAttr('disabled');
		},
		css: Control.property(function(cssProperties) {
			this.$button().css(cssProperties);
		})
	}))
});