var EventHandler = function() {

	var events = [];

	this.on = function(event, callback) {
		if(!$.isFunction(callback))
			return;

		if(events[event] == undefined)
			events[event] = [];
			
		events[event].push(callback);
	}

	this.fire = function(event) {
		if(events[event] == undefined)
			return;

		var args = [];
		for(var i = 1; i < arguments.length; i++)
			args.push(arguments[i]);	

		for(var i = 0; i < events[event].length; i++)
			events[event][i].apply(null, args);
	}
}