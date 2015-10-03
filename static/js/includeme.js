
var ImageHandler = function() {
	
	return {
		onChange : function(i) {
			var img = null;
			if ( i != null )
				img = i;
			else
				img = $(this);
			console.log(img);
			var src = img.attr('src');
			var regex = /^(?:http:\/\/)?pics\.rumblelane\.com.*([tsmlfTSMLF])$/ ;
			matches = src.match(regex);
			if ( ! matches )
				return;
			var winWidth = $( window ).width() ;
			if ( winWidth >= 1080 ) {
				//replace with the largest version of the image
				img.attr('src', src.replace(regex, 'l') );
			}
			else if ( winWidth > 720 ) {
				img.attr('src', src.replace(regex, 'm') );
			}
			else if ( winWidth > 320 ) {
				img.attr('src', src.replace(regex, 's') );
			}
			else /*if ( winWidth > 100 )*/ {
				img.attr('src', src.replace(regex, 't') );
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
		ImageHandler.onChange( $(this) );
	});
});

