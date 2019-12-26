// Adapted from tornado/examples/websocket/static/chat.js
// License of original is:
// Copyright 2009 FriendFeed
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License. You may obtain
// a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.

$(document).ready(function() {
	// startup operations when document is loaded
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#newentryform").on("submit", function() {
		// when newentryform is submitted
        newEntry($(this));
        return false;
    });
    $("#newentryform").on("keypress", function(e) {
		// when newentryform is submitted by "enter" key
        if (e.keyCode == 13) {
            newEntry($(this));
            return false;
        }
    });
    updater.start();
});

function newEntry(form) {
	// create a new entry from form and tell websocket
    var entry = form.formToDict();
	// following two fields are required on server side
	entry.op = 'new';
	entry.user = username;
    updater.socket.send(JSON.stringify(entry));
    form.find("input[type=text]").val(""); // clean form  
    form.find("#idname").select(); // select name  
}

jQuery.fn.formToDict = function() {
	// form has a list of input elements, convert it into an object
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    return json;
};

function incrementPrice(ael) {
	// compose an increment bid operation and send
	var eid = $(ael).parents(".entry").attr("id");
	var op = { id: eid, op: 'increment', user: username};
	// send to server
	updater.socket.send(JSON.stringify(op));
}
function deleteEntry(ael) {
	// compose delete entry request and send
	var eid = $(ael).parents(".entry").attr("id");
	var op = { id: eid, op: 'delete', user: username};
	updater.socket.send(JSON.stringify(op));
}
function sellEntry(ael) {
	// compose a sell request and send
	var eid = $(ael).parents(".entry").attr("id");
	var op = { id: eid, op: 'sell', user: username};
	updater.socket.send(JSON.stringify(op));
}

var updater = {  // web socket object gets updatemodel requests
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/chatsocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
			// when a new message is received, parse and update model
			console.log(JSON.parse(event.data))
            updater.updateModel(JSON.parse(event.data));
        }
    },

    updateModel: function(op) {
		// op: update model command coming from server
		var notifymess;
		var notifybg;
		console.log(op.message);
		if (op.error) {  // notification color based on error or success
			notifymess = op.error;
			notifybg = "#ffa0a0";
		} else {
			notifymess = op.message;
			notifybg = "#a0a0ff";
		}
	
		// show notification message coming from server bottom right
		$("#notification").text(notifymess)
						  .css({position: "absolute", bottom: "5px", 
								right: "5px", padding: "15px", "border-radius": "8px",
								"box-shadow": "4px 4px 2px #808080", 'background-color': notifybg })
					      .fadeIn().delay(3000).slideUp(); // show for 3 seconds and disappear

		if (op.change) {  // if model on HTML changes
			switch (op.change.op) {
			case "add": 		// someone inserted a new entry
				var actions=$('<td class="actions">'); // actions cell
				
				// new row
				var div = $("<tr>",{class:"entry",id:op.change.entry.id}) 
						 .append($("<td>",{class:"ename"}).text(op.change.entry.name))
						 .append($("<td>",{class:"eprice"}).text(op.change.entry.price))
						 .append($("<td>",{class:"eseller"}).text(op.change.entry.user))
						 .append($("<td>",{class:"ebidder"}).text("no bidder yet"));

				// depending on if current user is owner set "delete" or "increment" button
				// owner cannot increment but delete. no "Sell" button on new entries.
				if (op.change.entry.user == username) 
					actions.append($('<button onClick="deleteEntry(this);">Delete</button>'));
				else
					actions.append($('<button onClick="incrementPrice(this);">Increment</button>'));

				div.append(actions); 
				// initial color
				div.css({'background-color':'#b0ffb0'});
				// after 1 second, set it to white
				setTimeout(function () {
					div.css({'background-color': ''})
					}, 1000);

				var found = false;
				var ret = $.each($("#sellitems tr.entry"),function(index,entry) {
					if ($(entry).find(".ename").text() > op.change.entry.name) {
						$(entry).before(div);
						found = true;
						return false;
					}
				});   // sorted insert. find first name > current name and insert before
				if (!found)
					$('#sellitems').append(div);

				break;
			case "del": 
				var tmp = $("#" + op.change.id).fadeOut(1000);
				setTimeout(function () { tmp.remove()}, 1000);
				break;
			case "upd": 
				var row = $("#" + op.change.entry.id)
				// update request
				row.find(".ename").text(op.change.entry.name);
				row.find(".eprice").text(op.change.entry.price);
				if (op.change.entry.bidder ) {  // if there is a bidder
					row.find(".ebidder").text(op.change.entry.bidder);
					if (op.change.entry.user == username && row.find(".actions .selllink").length == 0 ) 
						// if current user is owner      and no Sell button yet
						// add Sell button

						row.find(".actions").append($('<button class="selllink" onClick="sellEntry(this);">Sell</button>'));
				}
				// change color of price cell for 1 seconds
				row.find('.eprice').css({'background-color' : '#ffe0b0'});
				setTimeout(function () { row.find('.eprice').css({'background-color':''})},
						   1000);
				break;
			}
		}
    }
};
