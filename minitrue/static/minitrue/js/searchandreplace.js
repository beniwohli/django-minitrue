(function( $ ){
	$.fn.SearchAndReplace = function(options){
		var globalcounter = $('#globalcounter');
		function decr_counter(amount, counter){
			/*
			 * Decrements the 'Results' counter at the bottom of the page by
			 * 'amount'.
			 */
			counter.text(parseInt(counter.text()) - amount);
		}
		
		function remove_element(ele){
			ele.find('span.match').removeClass('match').addClass('match-replaced').text(options['replacement']);
			ele.fadeOut(500, function(){ele.remove();});
		}
		
		// Logging!
		if (typeof console == "undefined" || typeof console.log == "undefined"){
			function log(){};
		} else {
			function log(text){
				console.log(text);
			}
		}
		$("button.replace-link").click(function(event){
			/*
			 * Single match replacement
			 */
			event.preventDefault();
			ele = $(this);
			ele.attr('disabled', 'disabled');
			var tr = ele.parentsUntil('tr').parent();
				tr.css('opacity', '0.5');
			var bits = ele.val().split('::');
			var app = bits[0];
			var model = bits[1];
			var counter = tr.parentsUntil('fieldset').parent().find('span.counter');
			var data = {
				'app': app,
				'model': model,
				'pk': bits[2],
				'field': bits[3],
				'term': bits[4],
				'replacement': bits[5],
				'case_sensitive': bits[6],
				'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
			};
			$.ajax({
				'url': options['replace-url'],
				'data': data,
				'type': 'POST',
				'success': function(){
					remove_element(tr);
					decr_counter(1, globalcounter);
					decr_counter(1, counter);
				},
				'error': function(xhr, status, error){
					alert("An error occured");
					log(xhr.responseText);
					ele.removeAttr('disabled');
				}
			});
		});
		$("button.replace-all-link").click(function(event){
			/*
			 * Replace all matches in a model
			 */
			event.preventDefault();
			ele = $(this);
			ele.attr('disabled', 'disabled');
			var bits = ele.val().split('::');
			var trs = ele.parentsUntil('table').parent().find('td').parent();
			var amount = trs.length;
			var fieldset = trs.parentsUntil('fieldset').parent();
				fieldset.css('opacity', '0.5');
			var data = {
				'app': bits[0],
				'model': bits[1],
				'term': bits[2],
				'replacement': bits[3],
				'case_sensitive': bits[4],
				'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
			};
			$.ajax({
				'url': options['replace-all-url'],
				'data': data,
				'type': 'POST',
				'success': function(){
					remove_element(fieldset);
					decr_counter(amount, globalcounter);
				},
				'error': function(xhr, status, error){
					alert("An error occured");
					log(xhr.responseText);
					ele.removeAttr('disabled');
				}
			});
		});
		
		/*
		 * Show/Hide hash signalling for better URLs and better behavior on page reload
		 */
		var lock = false; // prevent initial loading to destroy hashes
		$('fieldset.collapse a.collapse-toggle').click(function(){
			if (lock){
				return;
			}
			var fieldset = $(this).parent().parent();
			var id = fieldset.attr('id');
			var nohash = window.location.hash.substr(1);
			if (nohash){
				var hasharray = nohash.split('&');
			} else {
				var hasharray = [];
			}
			if ($.inArray(id, hasharray) != -1){
				hasharray.splice(hasharray.indexOf(id), 1);
			} else {
				hasharray.push(id);
			}
			if (hasharray.length){
				window.location.hash = hasharray.join('&');
			} else {
				window.location.hash = "";
			}
		});
		$.each(window.location.hash.substr(1).split('&'), function(i, val){
			if (val){
				lock = true;
				// Must be a click and not changing the class to prevent toggle-bug
				$('#' + val).find('a.collapse-toggle').click();
				lock = false;
			}
		});
	}
})(django.jQuery);
