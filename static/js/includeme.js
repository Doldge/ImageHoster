
var ImageHandler = function() {
	
	return {
		onChange : function(e, i) {
			var img = null;
			if ( e != null )
				img = $(e.target);
			else if ( i != null )
				img = $(i);
			var src = img.attr('src');
			//var regex = /^(?:http:\/\/)?pics\.rumblelane\.com\/image\/([0-9]+_[0-9])$/ ;
			var regex = /^((?:http:\/\/)?pics\.rumblelane\.com.*)([tsmlfTSMLF])$/ ;
			matches = src.match(regex);
			if ( ! matches || matches.length < 2 ) {
				console.log( matches );
				console.log( matches.length );
				return;
			}
			var winWidth = $( window ).width() ;
			if ( winWidth >= 1080 ) {
				//replace with the largest version of the image
				img.attr('src', src.replace(regex, '$1l') );
			}
			else if ( winWidth > 720 ) {
				img.attr('src', src.replace(regex, '$1m') );
			}
			else if ( winWidth > 320 ) {
				img.attr('src', src.replace(regex, '$1s') );
			}
			else /*if ( winWidth > 100 )*/ {
				img.attr('src', src.replace(regex, '$1t') );
			}
		}
	};
}();

$('img')
.one('load', ImageHandler.onChange )
.each(function() {
	if (this.complete) $(this).load();
});

$( window ).resize(function() {
	$('img').each( function() {
		ImageHandler.onChange( null, $(this) );
	});
});

