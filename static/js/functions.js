var Static = function() {

	return {
		ajax : function( type, url, data, block, blockmessage, multipart, successfunc) {
			var request;
			if (type == null) type = 'GET';
			if ( ! data ) data = {};

			if (!multipart)
			{
				request = $.ajax({
					'type'		: type,
					'url'		: url,
					'data'		: data,
					'async'		: true,
					'beforeSend' 	: function() {
						if (block) {
							if (blockmessage)
								$.blockUI({ 'message' : blockmessage });
							else
								$.blockUI({ 'message' : 'Loading..' })
						}
					},
					'complete'	: function() {
						if (block) $.unblockUI();
					}
				});
			} else {
				request = $.ajax({
					'type'		: type,
					'url'		: url,
					'data'		: data,
					'async'		: true,
					'beforeSend' 	: function() {
						if (block) {
							if (blockmessage)
								$.blockUI({ 'message' : blockmessage });
							else
								$.blockUI({ 'message' : 'Loading..' })
						}
					},
					'complete'	: function() {
						if (block) $.unblockUI();
					},
					'processData' 	: false,
					'contentType'	: false
				});
			}
			return request;
		}
	}
}();
