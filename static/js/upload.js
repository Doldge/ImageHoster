var Upload = function() {

	var SCALE = 1000;

	//var ASPECT_RATIO_THUMB = 16/10;
	var ASPECT_RATIO_THUMB = 16/10;
	var ASPECT_RATIO_BANNER = 24/10;
	var CURRENT_ASPECT = ASPECT_RATIO_THUMB;

	var CURRENT_SELECTION = null;
	var THUMB_SELECTION = null;
	var BANNER_SELECTION = null;

	var URL;


	var configure_previews = function() {
				
		var prev_height = 320;
		var prev_width = prev_height * CURRENT_ASPECT ;
		
		$('#primary_preview').css('width', prev_width+'px');
		$('#primary_preview').css('height', prev_height+'px');
		$('#secondary_preview').css('width', (prev_width/3)+'px');
		$('#secondary_preview').css('height', (prev_height/3)+'px');
	};


	var switch_config = function( e ) {
		e.preventDefault();
		var btn = $(this);
		var set = $('#set_config');
		if ( CURRENT_ASPECT == ASPECT_RATIO_THUMB ) {
			CURRENT_ASPECT = ASPECT_RATIO_BANNER;
			btn.text('Configure Thumb');
			set.text('Set Banner Configuration');
			$('#ratios').addClass('hidden');
		} else {
			CURRENT_ASPECT = ASPECT_RATIO_THUMB;
			btn.text('Configure Banner');
			set.text('Set Thumb Configuration');
			$('#ratios').removeClass('hidden');
		}

		$('#image').cropper( 'setAspectRatio', CURRENT_ASPECT );
		configure_previews();

		if ( CURRENT_ASPECT == ASPECT_RATIO_THUMB ) {
			if (THUMB_SELECTION != null) {
				var image = $('#image');
				image.cropper('setData', THUMB_SELECTION );
				console.log(image.cropper('getData'));
			}
		} else {
			if (BANNER_SELECTION != null) {
				var image = $('#image');
				image.cropper('setData', BANNER_SELECTION );
				console.log(image.cropper('getData'));
			}
		}
	};


	var set_config = function( e ) {
		e.preventDefault();
		if ( CURRENT_ASPECT == ASPECT_RATIO_BANNER )
			BANNER_SELECTION = CURRENT_SELECTION;
		else
			THUMB_SELECTION = CURRENT_SELECTION;

		console.log('BANNER');
		console.log(BANNER_SELECTION);
		console.log('THUMB');
		console.log(THUMB_SELECTION);
		return false;
	};


	var save_configs = function( e ) {
		var alrt = $('.alert');
		if (! THUMB_SELECTION && ! BANNER_SELECTION )
			alrt.find('p').html('You must have set both a Thumb Configuration, and Banner Configuration. </br><strong>You\'re currently missing Both. Please use the Set ... Button, before using the Configure button to configure the other image.</strong>');
		else if ( ! THUMB_SELECTION )
			alrt.find('p').html('You must have set both a Thumb Configuration, and Banner Configuration. </br><strong>You\'re currently missing a Thumb Configuration.</strong>');
		else if ( ! BANNER_SELECTION ) 
			alrt.find('p').html('You must have set both a Thumb Configuration, and Banner Configuration. </br><strong>You\'re currently missing a Banner Configuration.</strong>');

		if (! THUMB_SELECTION || ! BANNER_SELECTION ) {
			e.preventDefault();
			alrt.removeClass('hidden');
			return false;
		}

		var data = {};
		data['banner_x' ] = BANNER_SELECTION.x;
		data['banner_y' ] = BANNER_SELECTION.y;
		data['banner_width' ] = BANNER_SELECTION.width;
		data['banner_height' ] = BANNER_SELECTION.height;
		data['thumb_x'] = THUMB_SELECTION.x;
		data['thumb_y'] = THUMB_SELECTION.y;
		data['thumb_width'] = THUMB_SELECTION.width;
		data['thumb_height'] = THUMB_SELECTION.height;
		data['banner_aspect'] = ASPECT_RATIO_BANNER;
	       	data['thumb_aspect'] = ASPECT_RATIO_THUMB;	
		data['url'] = URL;
		console.log(data);

		var resp = Static.ajax( 'POST', '/saveconfiguration/', data, true );
		var result = false;
		resp.success( function( data ) {
			console.log(data);
			if ( data.status == 'OK' ) {
				result = true;
			} else {
				result = false;
				/* We should display some kind of message here */
			}
		});

		return true;
	};


	var form_submit = function( e ) {
		console.log('UPLOADING!!');
		e.preventDefault();
		var form = $('#upload_1'); //should be a form element. need to check though.
		var url =  form.prop('action');
		var type = form.prop('method');

		var data = new FormData(form[0]);

		var resp = Static.ajax( type, url, data, true, 'Uploading, Please wait..', true );
		resp.success( function( data ) {
			console.log( data );
			if ( data.status == 'OK' )
			{
				configure_previews();

				$('#controls').removeClass("hidden");

				var image = $('#image');
				image.prop('src', data.results.url );
				URL = data.results.url;
				var xScale = data.results.x/SCALE;
				var yScale = data.results.y/SCALE;

				$('#preview_container').removeClass('hidden');
				$('#image_container').removeClass('hidden');

				image.cropper({
					'aspectRatio' 	: CURRENT_ASPECT,
					'data'		: {
						'x' : data.results.x,
						'y' : data.results.y,
						'width' : data.results.x/xScale,
						'height' : data.results.y/yScale
					},
					'preview' : ".img-preview",
					'done' : function( data ) {
						CURRENT_SELECTION = data;
					}
				});


			}
		});

		return false;
	};


	var set_ratio = function() {
		console.log('Setting RATIO');
		var xRatio = $('input[name="xRatio"]');
		var yRatio = $('input[name="yRatio"]');
		xRatio = xRatio.val();
		yRatio = yRatio.val();
		console.log(xRatio);
		console.log(yRatio);
		if ( xRatio && yRatio && xRatio != '' && yRatio != '' ) {
			CURRENT_ASPECT = ASPECT_RATIO_THUMB = parseFloat( parseFloat(xRatio) / parseFloat(yRatio) );
			$('#image').cropper( 'setAspectRatio', CURRENT_ASPECT );
			configure_previews();
		}
	};

	return {
		init: function() {
			console.log('INITIALIZING!');
			$('#upload_1').on('submit', form_submit );

			$('#set_config').on('click', set_config );
			$('#switch').on('click', switch_config );
			$('#save').on('click', save_configs );
			$('button[name="set_ratio"]').on('click', set_ratio );
		},
	}

}();
