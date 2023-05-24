// Title: jqmovie.js
// Movie application dynamic version with jquery and JSON on server side

// Variable: votes
// 	array of votes. votes[movieid] = "vote given by user"
votes = [];

// Variable: watches
// 	list of watched movieids
watches = [];

// Variable: movielist
// 	list of movie object in an array
movielist = [];

// Variable: selected
// 	selected row query
selected = undefined;

// Function: getCookie(name)
// Parses the cookie header, finds and returns cookie with name
// Used for getting csrftoken from django
//
// Parameters:
//	 name - name of the cookie
//
// Returns:
// 	value of the cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// Function: setuser()
// 	Sets the username part on top right
//
// Parameters:
//	username - name of the user to set
function setuser(username) 
{
	$('#username').html(username + '&nbsp; <a href="/logout">Logout</a>');
}

// Function: authenticate()
// 	Initiate login by displaying authenticate block/form
//
// Parameters:
//	callback - Function to call after successfull authentication
function authenticate(callback) 
{
	$("#loginblock").fadeIn();
	$("#loginbutton").click(function() {
		var u = $("#loginform [name=username]").val();
		var p = $("#loginform [name=password]").val();
		postlogin(u, p, callback);
		$("#loginblock").fadeOut();
		return false;
	});
}

// Function: postlogin(username, password)
// post action of the login form, do server login
//
// Parameters:
//	username - Function to call after successfull authentication
//	password - Function to call after successfull authentication
//	callback - Function to call after successfull authentication
function postlogin(username, password, callback) 
{
	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});
	$.post("/logp", {'username': username,
			 'password': password},
			function (data) {
				if ( data.result == 'Fail') {
					alert(data.reason);
				}
				callback();
				setuser(username);
			});
}


// Function: loadmovielist()
// refresh of the movie model in <movielist> from server
function loadmovielist() 
{
	$.getJSON('/list', function(data) {
		if ( data.result == 'Fail') {
			if (data.reason == 'Authentication') {
				authenticate(function() {
						loadvotes();
						loadwatchlist();
						loadmovielist();
					});
			} else {
				alert(data.reason);
			}
			return;
		}
		for (var i in data.movielist) {
			var v = data.movielist[i];
			movielist[v.id] = v;
		}
		// now update the movie list table from the model
		updatemovielistview();
	});
}

// Function: updatemovierow(movie, row)
// 	Update the row on the movie table from the movie object
// 	in the model
// 
// Parameters:
//	movie - movie object
//	row -  jquery object for tr element in the html table
function updatemovierow(movie, row)
{
	var id = movie.id;
	var cell;

	var yourvote = "<span></span><span></span><span></span><span></span><span></span>";
	var impre = 'http://www.imdb.com/title/';

	// set row attribute rowid for delete/update/watch/vote ops
	row.attr('id','row' + id);

	row.html("");

	// append new cell
	row.append('<td class="imdbcol"></td>');

	cell = row.find("td:last");

	cell.html('<a href="' + impre + movie.imdb + '">IMDB</a>');

	// 3 cells containing title, director, cast texts
	var tmp = ['title','director','cast']
	for (var i = 0; i < 3 ; i++) {
		row.append('<td class="' + tmp[i] + 'col"></td>');
		cell = row.find("td:last");

		cell.html(movie[tmp[i]]);
	}

	row.append('<td class="votecol"></td>');
	cell = row.find("td:last");

	cell.html('Rating:' + ((movie.votes)? movie.votes : '???') + 
			'&nbsp;' + yourvote );
	cell.find('span').each(function(i) {
		$(this).click( function () { vote(id,i+1);return false;})
		       .attr('class',(i+1 == votes[id])? "staron" : "star");
	});

	row.append('<td class="watchcol"></td>');
	cell = row.find("td:last");
	cell.html('Watched: ' + movie.watches + '&nbsp; <a></a>');
	if (watches.indexOf(id)<0) {
		cell.find("a").unbind();
		cell.find("a").click(function() {flipwatch(id); return false;})
			      .text("mark watched")
			      .attr('class',"notwatched");
	} else {
		cell.find("a").unbind();
		cell.find("a").click(function() {flipwatch(id); return false;})
			      .text("mark not watched")
			      .attr('class',"watched");
	}

	// clicking on a row selects the movie
	// , updates variable "selected" and enables/disables buttons
	row.click(function() {
			var id = this.id.slice(3); // remove heading "row"
			if (selected == id) {  // reclick on selected
				selected = undefined;
				this.classList.remove('selectedrow');
				$("#updbutton").attr('disabled',true);
				$("#delbutton").attr('disabled',true);
			} else {
				if (selected)  {
					$("#row"+selected)
					.removeClass('selectedrow');
				}
				this.classList.add('selectedrow');
				selected = id;
				$("#updbutton").attr('disabled',false);
				$("#delbutton").attr('disabled',false);
			}
		})
		      
}

// Function: updatemovielistview()
// Update the movie list view on the web page
function updatemovielistview() 
{
	var row;

	// remove all rows from table
	$("#moviestable tr").remove();

	// update all rows
	for (id in movielist) {
		$("#moviestable").append("<tr></tr>")
		row = $("#moviestable tr:last")
		updatemovierow(movielist[id], row);
	}

	$("table").trigger("update")
}

// Function: loadvotes()
// 	load the list <votes> from the server
function loadvotes() 
{
	$.getJSON('/votes', function (data) {
			if (data.result != "Success") {
				return;
			}
			votes = {}
			for (var i in data.votes) {
				var v = data.votes[i];
				votes[v.movieid] = v.vote;
				$(`#row${v.movieid}`).find('.votecol span').attr('class','star') ;   $(`#row${v.movieid}`).find(`.votecol span:nth-child(${v.vote})`).attr('class','staron') 
			}

	}) ;
}

// Function: insertmovie()
// 	popup editblock/edit form for insertion of a new item
function insertmovie() 
{
	var eb = document.getElementById('editblock');
	var ef = document.getElementById('editform');
	ef.reset();
	ef.id.value='';
	// Add will be the action
	ef.actionbutton.textContent = "Add";
	// make it visible
	eb.style.display = 'block';
}


// Function: postmovie(is_add)
//  post  add or update request on server
//
// Paramaters:
//	is_add - boolean flag true if add request, false if modify
function postmovie(is_add)
{
	var url;
	var id;
	if (is_add) {
		url = '/addmovie';
	} else {
		url = '/updmovie';
	}

	$.ajaxSetup({beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}});
	
	data = $("#editform").serialize() ;
	$.post(url, data , function (data) {
			if (data.result == 'Authentication') {
				authenticate( function() {
					postmovie(is_add);
				});
				return;
			} else if (data.result != "Success") {
				alert(data.reason);
				return;
			}
			var fdata = {};
			var row;
			$("#editform :input").each(function (id,val) {
					fdata[val.name] = val.value;
				});

			if (is_add) {
				id = data.success.id;
				// add movie to model
				movielist[id] = {'id':id,
						'votes':undefined,
						'watches':0};
				// add row to table
				$("#moviestable").append("<tr></tr>")
                		row = $("#moviestable tr:last")
			} else {
				id = $("#editform [name=id]").val();
				// select existing row
				row = $("#row" + id);
			} 
			var fields =  ['title','director','imdb','cast'];
			for (var i in fields) {
				var n = fields[i];
				movielist[id][n] = fdata[n];
			}
			updatemovierow(movielist[id], row);
			$("table").trigger("update");
		});
}

// Function: deletemovie(id)
//  delete movie from server
//
// Parameters:
//	id - movie id
function deletemovie(id, confirmed) 
{
	$.getJSON('/delete/'+id,function (data) {
		if (data.result == 'Fail' ) {
			if (data.reason == 'Authentication') {
				authenticate(function () {
					deletemovie(id);
				});
			} else {
				alert(data.reason);
			}
		} else {
			// remove row from table
			$("#row"+id).remove();
			// delete from model
			movielist[id] = undefined;
			$("table").trigger("update");
		} 
	});
}

// Function: updatemoviemodel(id)
//	Update movie information from server
//
// Parameters:
//	id - movie id
function updatemoviemodel(id) 
{
	$.getJSON('/get/' + id,function (data) {
		if (data.result == 'Fail' ) {
			if (data.reason == 'Authentication') {
				authenticate(function () {
					updatemoviemodel(id);
				});
			} else {
				alert(data.reason);
			}
		} else {
			row = $("#row" + id);
			movielist[data.movie.id] = data.movie;
			updatemovierow(data.movie, row);
		}
	});
}

// Function: vote(id, v)
//  change vote for a movie
//
// Parameter:
//	id - movie id
//	v - new vote
function vote(id, v) 
{
	$.getJSON('/vote/' + id + '/' + v, function (data) {
		if (data.result == 'Fail') {
			if (data.reason == 'Authentication') {
				authenticate(function () {
					vote(id,v);
				});
			} else {
				alert(data.reason);
			} 
		} else {
				votes[id] = v;
				updatemoviemodel(id);
		}
	});
}

// Function: flipwatch(id)
//  change watch state for a movie
//
// Parameter:
//	id - movie id
function flipwatch(id) 
{
	$.getJSON("/watch/" + id, function (data) {
		if (data.result == 'Fail') {
			if (data.reason == 'Authentication') {
				authenticate(function () {
					flipwatch(id);
				});
			} else {
				alert(data.reason);
			} 
		} else {
			var i = watches.indexOf(id);
			if (i<0) {
				watches.push(id);
				movielist[id].watches ++;
			} else {
				watches.splice(i);
				movielist[id].watches --;
			}
			var movie = movielist[id];
			var row = $("#row" + id);
			updatemovierow(movie,row);
		}
	});
}


// Function: loadwatchlist()
// load the list of movies watched by current user
function loadwatchlist() 
{
	$.getJSON('/watches', function (data) {
			if (data.result != 'Success')  
				return;
			
			watches = [];
			for (var i in data.watches) {
				var w = data.watches[i];
				watches.push(w.id);
			}
		});
}

// Function: $(document).ready()
// Code to execute on document load
$(document).ready(function() {
	// for tablesorter widget
	// needs $("table").trigger("update") after table change
	$("table").tablesorter({});

	// Action of edit cancel button
	$("#editform [name=cancelbutton]").click(function() {
		$("#editblock").fadeOut();
		return false;
	});

	// Action of no answer to delete
	$("#delnoanswer").click(function() {
		$("#deleteblock").fadeOut();
		return false;
	});

	// Action of login cancel
	$("#loginform [name=cancelbutton]").click(function() {
		$("#loginblock").fadeOut();
		return false;
	});

	// Action of update button on the top
	$("#updbutton").click(function() {
		if (! selected) 
			return;
		$("#editblock").fadeIn();
		// for all input elements of the form
		$("#editform :input").each(function (i, elem) {
			// get movie[elem.name] from model
			elem.value = movielist[selected][elem.name];
		});
		// cancel previous events
		$("#editform [name=actionbutton]").unbind();
		// bind new event
		$("#editform [name=actionbutton]")
			.text("Update")
			.click(function () {
				$("#editblock").fadeOut();
				postmovie(false);
				return false;});
		return false;
	});

	// Action of new button on the top
	$("#newbutton").click(function() {
		$("#editblock").fadeIn();
		// for all input elements of the form
		$("#editform :input").each(function (i, elem) {
			elem.value = "";
		});
		// cancel previous events
		$("#editform [name=actionbutton]").unbind();
		// bind new event
		$("#editform [name=actionbutton]")
			.text("Add")
			.click(function () {
				$("#editblock").fadeOut();
				postmovie(true); 
				return false;});
		return false;
	});

	// Action of del button on the top
	$("#delbutton").click(function() {
		if (! selected) 
			return;
		$("#deleteblock .moviename").text(movielist[selected].title);
		$("#deleteblock").fadeIn();
		$("#delyesanswer").unbind();   // cancel previous events
		$("#delyesanswer").click(function () {
				$("#deleteblock").fadeOut();
				deletemovie(selected); 
				selected = undefined;
				$("#updbutton").attr('disabled',true);
				$("#delbutton").attr('disabled',true);
				return false;});
		return false;
	});
	loadwatchlist();
	loadvotes();
	loadmovielist();
});

