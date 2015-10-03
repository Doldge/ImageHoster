var Index = function() {
	
	var SCROLL_LIMIT = 30;

	var sortImages = function() {
		var gallery_block = $('#gallery');
		var total_width = 0;
		for ( var i = 0; i < PHOTOS.ALL().length; i ++ )
		{
			total_width = total_width + 1;
		}
	};

	return {
		init : function() {
			console.log('we\'re INITIALISING!');
			$(window).on('scroll', function() {
				var st = $(this).scrollTop(); //FIXME background alpha doesn't appear to be working in Mozilla based browsers?
				$('#disclaimer_bg').css( 'background-color', 'rgba(255,255,255,'+(st/SCROLL_LIMIT)+')' );
			});

			// initialize gallery.
      			$('#gallery').justifiedGallery({
				'rowHeight' : 320,
				'lastRow' : 'hide',
				'margins' : 3,
				'sizeRangeSuffixes' : { 
					'lt100' : '_t',
					'lt240' : '_s',
					'lt320' : '_s',
					'lt500' : '_m',
					'lt640' : '_m',
					'lt1024' : '_l',
				},
				'captions' : true
			});
			//initialize our light boxs.
			$('.fancybox').fancybox({
				'padding': 0,
				'openEffect' : 'elastic',
				'type' : 'image',
				'helpers' : { 'title' : { 'type' : 'over' } }
			});
		},
		/*login-window: function(e) {
			e.preventDefault();

		}*/
	}

}();
