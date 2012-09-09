$(document).ready(function() {
    G.addControl("ReviewRow", Control.sub({
        inherited: {
            content:
                {
                    html: 'div',
                    ref: 'row',
                    content:
                        [
                             {
                                 html: 'div',
                                 ref: 'col1',
                                 content:
                                     [
                                         {
                                             html: 'img',
                                             attr: {
                                                 src: "/static/images/avatar.jpeg"
                                             }
                                         },
                                         {
                                             html: 'a',
                                             ref: 'name',
                                             attr: {
                                                 href: "#"
                                             }
                                         },
                                         {
                                             html: 'h4',
                                             ref: 'location'
                                         }
                                     ]
                             },
                             {
                                 html: 'div',
                                 ref: 'col2',
                                 content:
                                     [
                                         {
                                             html: 'div',
                                             ref: 'reviewsStarSection'
                                         },
                                         {
                                             html: 'p',
                                             ref: 'review',
                                             attr: {
                                                 href: "#"
                                             },
                                             css: {
                                                 'padding-top': 3
                                             }
                                         }
                                     ]
                             }
                        ]
                    }
        },
        review: Control.property(),
        reviewerName: Control.chain('$name', 'content'),
        reviewerLocation: Control.chain('$location', 'content'),
        rating: Control.property(),
        initialize: function() {
            var self = this;
            this.inDocument(function() {
                self.$review().content(self.review().slice(0, 140) + '<a href="/products">...More</a>');
                self.$reviewsStarSection().content(
                    G.controls.StarDisplay.create()
                        .rating(self.rating())
                        .quarterStarPath('/static/images/star_quarter.png')
                        .halfStarPath('/static/images/star_half.png')
                        .threeQuartersStarPath('/static/images/star_threequarters.png')
                        .fullStarPath('/static/images/star_full.png')
                        .emptyStarPath('/static/images/star_empty.png')
                )
            });
        }
    }))
})
