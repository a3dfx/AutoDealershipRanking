$(document).ready(function() {
	G.addControl("StarDisplay", Control.sub({
		tag: 'span',
		inherited: {
			content:
				{
					html: 'span',
					ref: 'stars',
					css: { 'padding-bottom': 2 },
					content:
						[
							{
								html: 'img',
								ref: 'star1',
								attr: {
									align: 'absmiddle'
								},
								css: {
									'padding': 1,
									'padding-left': 0
								}
							},
							{
								html: 'img',
								ref: 'star2',
								attr: {
									align: 'absmiddle'
								},
								css: {
									'padding': 1
								}
							},
							{
								html: 'img',
								ref: 'star3',
								attr: {
									align: 'absmiddle'
								},
								css: {
									'padding': 1
								}
							},
							{
								html: 'img',
								ref: 'star4',
								attr: {
									align: 'absmiddle'
								},
								css: {
									'padding': 1
								}
							},
							{
								html: 'img',
								ref: 'star5',
								attr: {
									align: 'absmiddle'
								},
								css: {
									'padding': 1
								}
							},
							{
								html: 'div',
								ref: 'date'
							}					
						]						
				}
		},
		fullStarPath: Control.property(),
		quarterStarPath: Control.property(),
		halfStarPath: Control.property(),
		threeQuartersStarPath: Control.property(),
		emptyStarPath: Control.property(),
		rating: Control.property(),
		date: Control.chain('$date', 'content'),
		initialize: function() {
			var self = this;
			$starList = [self.$star1(), self.$star2(), self.$star3(), self.$star4(), self.$star5()]
			this.inDocument(function() {
				if (!self.rating()) {
					self.$stars().empty().append(
						'Not Found'
					).css({
						'font-style': 'italic',
						'color': 'gray'
					});
				} else {
					var i = self.rating();
					while (i >= 1) {
						$starList[0].attr({
							src: self.fullStarPath()
						});			
						$starList.shift()
						i -= 1;
					}
					if (i) {
						var lastStarPath;
						if (i < .5) {
							lastStarPath = self.quarterStarPath();
						} else if (i >= .5 && i <= .75) {
							lastStarPath = self.halfStarPath();
						} else {
							lastStarPath = self.threeQuartersStarPath();
						}
						$starList[0].attr({
							src: lastStarPath
						});	
						$starList.shift()
					}
					while ($starList.length) {
						$starList[0].attr({
							src: self.emptyStarPath()
						});	
						$starList.shift()					
					}	
				}			
			});
		}
	}))	
})