// Title: dmovie.js
// Movie application dynamic version with pure javascript and AJAX

// Variable: votes
// 	array of votes. votes[movieid] = "vote given by user"
votes = []

// Variable: watches
// 	list of watched movieids
watches = []

// Variable: movielist
// 	list of movie object in an array
movielist = []

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


// Function: getfields(mnode)
// parse values of a XMLNode and fill in rv object, return rv
//
// Parameters:
//	mnode - thhe XMLNode object to parse
// 
// Returns:
//	a javascript object containing the values
function getfields(mnode) 
{
	var obj = {};
	obj['id'] = mnode.attributes.id.value;
	// start from first elementchild, traverse siblings
	for ( var c = mnode.firstElementChild; c != null ; 
					c = c.nextElementSibling) {
		// element tagname / textContent are inserted in obj
		obj[c.tagName] = c.textContent;
	}
	return obj
}

// Function: testerror(xmldoc)
//	Test for error in XMLDoc by XMLHttpRequest.
//	Do authentication on need
//
// Returns:
//	"auth" if auth error, "err" if there is an error, "success" otherwise
function testerror(xmldoc)
{
	var result = xmldoc.getElementsByTagName("result")[0].textContent;
	if (result == 'Fail') {
		var reason = xmldoc.getElementsByTagName("reason")[0].textContent;
		if (reason == 'Authentication') {
			return "auth";
		} else {
			alert(reason);
			return "err";
		}
	}		
	return "success";
}

// Function: setuser()
// 	Sets the username part on top right
//
// Parameters:
//	username - name of the user to set
function setuser(username) 
{
	var udiv = document.getElementById('username');
	udiv.innerHTML = username + '&nbsp; <a href="/logout">Logout</a>';
}

// Function: authenticate()
// 	Initiate login by displaying authenticate block/form
//
// Parameters:
//	callback - Function to call after successfull authentication
function authenticate(callback) 
{
	var loginbutton = document.getElementById('loginbutton');
	loginbutton.onclick = function() { loginpost(callback);};
	//loginform = document.getElementById('loginform');
	//loginform.onsubmit = function() { loginpost(callback);};
	// make it visible
	var lbl = document.getElementById('loginblock');
	lbl.style.display='block';
}

// Function: loginpost()
// post action of the login form, do server login
//
// Parameters:
//	callback - Function to call after successfull authentication
function loginpost(callback) 
{
	var http = new XMLHttpRequest();
	var form = document.getElementById('loginform')

	function logincb() {
		var x,err;
		
		if(http.readyState == 4 && http.status == 200) {
			var xmlDoc=http.responseXML;
			err = testerror(xmlDoc);
			if (err == "auth") { // reauthenticate 
				authenticate(callback);
				return;
			} else if (err = "success") {
				// success, run callback
				callback();
				setuser(form.username.value);
			}
		} else if (http.readyState == 4) {
			// just to see output, debugging purpose
			alert(http.responseText);
		}
	}

	var lbl; // container of the login block, hide it during post
	lbl = document.getElementById('loginblock');
	lbl.style.display='none';
	http.open("POST","/logp",true);
	http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	http.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	http.onreadystatechange = logincb; 
	// set query string from login form username/password
	http.send('username=' + form.username.value + 
		  '&password=' + form.password.value);
	return false;
}


// Function: loadmovielist()
// refresh of the movie model in <movielist> from server
function loadmovielist() 
{
	var http = new XMLHttpRequest();
	http.open("GET","/list",true);
	http.onreadystatechange = function() {
		if(http.readyState == 4 && http.status == 200) {
			var x, err, rc;
			var xmlDoc=http.responseXML;
			err = testerror(xmlDoc);
			if ( err == "auth")  {
				authenticate(function() {
					loadvotes();
					loadmovielist();
					loadwatchlist();
				});
				return;
			} else if (err == "err") {
				return;
			}
			// else, it is success
			x=xmlDoc.getElementsByTagName("movielist");
			if (x.length == 0)
				return;

			// full load of movie model
			rc = 0;
			movielist = []
			// for each movie tagged value
			// start from first child of movies tag and
			// traverse all siblings
			for (var m = x[0].firstElementChild; m != null; 
					m = m.nextElementSibling) {
				// get fields of movie tag
				movie = getfields(m);
				movielist[movie.id] = movie;
			}
		}
		// now update the movie list table from the model
		updatemovielistview();
	};
	http.send(null);
}

// Function: updatemovierow(movie, row)
// 	Update the row on the movie table from the movie object
// 	in the model
// 
// Parameters:
//	movie - movie object
//	row -  tr element in the html table
function updatemovierow(movie, row)
{
	var id = movie.id;

	function yourvote(no) {
		var ret = "";
		var els = [1,2,3,4,5];
		for (i in els) {
			if ( no == els[i]) {
			ret = ret + "<span class=\"staron\" onclick=\"vote(" +
				id + ',' +  els[i] + ")\">*</span>";
			} else {
			ret = ret + "<span class=\"star\" onclick=\"vote(" +
				id + ',' + els[i] + ")\">*</span>";
			}
		}
		return ret;
	}

	function yourwatch() {
		var ret = "# watched: " + movielist[id].watches + " &nbsp;";
		ret += ",<a onClick=\"flipwatch(" + id + ");\" class=\"";

		if (watches.indexOf(id) >= 0) {	// movie in watch list
			ret += "watched\">mark not watched</a>";
		} else {
			ret += "notwatched\">mark watched</a>";
		}
		return ret;
	}

	var impre = 'http://www.imdb.com/title/';

	// set row attribute rowid for delete/update/watch/vote ops
	row.setAttribute('id','row' + id);
	row.innerHTML="";
	var cc = 0;
	var cell = row.insertCell(cc);
	// cell containing delete and update icons
	var del = '<a onClick="deletemovie(' + id +');">' +
		'<span class="delbutton">&nbsp;</span></a>'
	var upd = '<a onClick="updatemovie(' + id +');">' +
		'<span class="updatebutton">&nbsp;</span></a>'
	cell.innerHTML =  del + upd;
	cc++;

	// cell containing movie poster/imdb link
	cell = row.insertCell(cc);
	cc++;
	cell.innerHTML = '<a href="' + impre + movie.imdb + 
			 '">' + movie.title + '</a>';

	// 3 cells containing title, director, cast texts
	var tmp = ['director','cast']
	for (var i = 0; i < 2 ; i++) {
			cell = row.insertCell(cc);
			cc++;
			cell.innerHTML = movie[tmp[i]]
	}
	cell = row.insertCell(cc);
	cc++;

	cell.innerHTML = 'Rating:' + ((movie.votes)? movie.votes : '???') + 
			'&nbsp;' + yourvote(votes[id]) + "<br/>" +
			 yourwatch();
	// update the row attribute to set row for later use
	movie.row = row;
}

// Function: updatemovielistview()
// Update the movie list view on the web page
function updatemovielistview() 
{
        tab = document.getElementById("moviestable");                   
	// remove all rows from table
	try {
		while (true) {
			tab.deleteRow(1);
		}
	} catch (e) {
		//nothing
	}
	// update all rows
	for (id in movielist) {
		row = tab.insertRow(1);
		updatemovierow(movielist[id], row);
	}
}

// Function: loadvotes()
// 	load the list <votes> from the server
function loadvotes() 
{
	httpv = new XMLHttpRequest();
	httpv.open("GET","/votes",true);
	httpv.onreadystatechange = function () {
		var x, l;

		if(httpv.readyState == 4 && httpv.status == 200) {
			xmlDoc=httpv.responseXML;
			if (testerror(xmlDoc) != "success") {
				return;
			}

			// else, it is success
			// parse XML elements
			x=xmlDoc.getElementsByTagName("votelist");
			if (x.length == 0)
				votes = [];
		
			l = [];

			for (m = x[0].firstElementChild; m != null; 
					m = m.nextElementSibling) {
				var id = m.getElementsByTagName('movieid')[0].textContent;
				var vote = m.getElementsByTagName('vote')[0].textContent;
				l[id] = vote;
			}
			votes =  l;
		}
	}
	;
	httpv.send(null);
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

// Function: updatemovie(did)
// popup editblock/editform for update of an item
//
// Parameters: 
//	did - Document id
function updatemovie(did) 
{
	var eb = document.getElementById('editblock');
	var ef = document.getElementById('editform');
	// each row contains an id= row + db_id 
 	// get the updated row from table
	var movie = movielist[did];

	// fill in the form from table cells
	ef.title.value = movie.title;
	ef.director.value = movie.director;
	ef.cast.value = movie.cast;
	ef.imdb.value = movie.imdb;
	ef.id.value = did;
	// set action to be Update
	ef.actionbutton.textContent = "Update";
	// make it visible
	eb.style.display = 'block';
}

// Function: movieformvalid(form)
// form validation here
//
// Parameters:
//	form - form element in html
function movieformvalid(form)
{
	// make validation here
	return true;
}


// Function: insupdatemoviepost()
//  called when editform is submitted (Add/Update clicked)
//  post form data to insert or update of service.py
function insupdatemoviesub() 
{
	var ef = document.getElementById('editform');

	if (! movieformvalid(ef) )
		return;

	var eb = document.getElementById('editblock');
	eb.style.display = 'none';

	movie = {} ;
	for (i=0; i<ef.elements.length ; i++) {
		el = ef.elements[i];
		if (el.type != 'submit' && el.type != 'button')  {
			movie[ el.name ] = el.value;
		}
	}
	is_add = (ef.actionbutton.textContent == 'Add') 
	insupdatemoviepost(movie, is_add);
}
	

// Function: insupdatemoviepost(movie, is_add)
//  post a movie object on server to add or update
//
// Paramaters:
//	movie - movie object from html form
//	is_add - boolean flag true if add request, false if modify
function insupdatemoviepost(movie, is_add)
{
	// setup query from form data
	var qstr = '';
	var http = new XMLHttpRequest();
	var att,err, id; 
	for (att in movie) {
		if (qstr != '' ) qstr = qstr + '&';
		qstr = qstr + att + '=' + movie[att];
	}

	// choose between insert or update based on actionbutton value
	if (is_add) {
		http.open("POST","/addmovie",true);
	} else {
		http.open("POST","/updmovie",true);
	} 
	http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	http.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	// post the query string
	http.onreadystatechange = function () {
		var xmlDoc,x, tab,eb,rv;
		// if successfully retrieved result
		if(http.readyState == 4 && http.status == 200) {
			xmlDoc=http.responseXML;
			err = testerror(xmlDoc);
			if (err == 'auth') {
				authenticate( function() {
					insupdatemoviepost(movie, is_add);
				});
				return;
			} else if (err != "success") {
				return;
			}

			if (is_add) {
				// if insertion successful, inserted
				// record needs to be inserted in HTML as well
				id = xmlDoc.getElementsByTagName("id")[0].textContent;
				tab = document.getElementById('moviestable');
				eb = document.getElementById('editform');
				movie.id = id;
				// new movie these fields empty
				movie.votes = undefined;
				movie.watches = 0;
				// add to model
				movielist[id] = movie;
				// insert new row for rv
				row = tab.insertRow(1);
				updatemovierow(movie,row);
			} else {
				id = movie.id;
				row = movielist[id].row;
				// use old values in model
				movie.votes = movielist[id].votes;
				movie.watches = movielist[id].watches;
				// update model
				movielist[id] = movie;
				updatemovierow(movie,row);
			} 
		} else if (http.readyState == 4) {
			alert('Failed: ' + http.responseText);
		}
	};
	http.send(qstr);
}

// Function: deletemovie(id, confirmed)
//  delete request from user
//
// Parameters:
//	id - movie id
//	confirmed - boolean flag. if true request posted on server
function deletemovie(id, confirmed) 
{
	var dbl;
	dbl = document.getElementById('deleteblock');
	if (! confirmed) {
		// popup deleteblock and  return
		document.getElementById('delmoviename').innerHTML=
			'<b>'+movielist[id].title + '</b>';
		var ansbutton = document.getElementById('delyesanswer');
		ansbutton.onclick = function () {
			deletemovie(id, true);
		}
		dbl.style.display='block';
		return;
	}
	// otherwise display button is posted with "YES"
	dbl.style.display='none';
	var http = new XMLHttpRequest();
	http.open("GET","/delete/"+id,true);
	http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	// call delresult callback with current id
	http.onreadystatechange = function () {
		var xmlDoc, err, tab,row;
		// if response received completely and it is successful
		if(http.readyState == 4 && http.status == 200) {
			xmlDoc=http.responseXML;
			err = testerror(xmlDoc);
			if (err == 'auth') {
				authenticate(function () {
						deletemovie(id);
					});
			} else if ( err == 'success') {
				// if xml tag result contains success
				// meaning row deleted from server database
				// update model and table
				
				tab = document.getElementById('moviestable');
				row = movielist[id].row;
				// delete the row from table 
				tab.deleteRow(row.rowIndex);
				// delete from model
				movielist[id] = undefined;
			} else {
				alert('Failed: ' + http.responseText);
			}
		} 
	}
	http.send(null)
}

// Function: updatemoviemodel(id)
//	Update movie information from server
//
// Parameters:
//	id - movie id
function updatemoviemodel(id) 
{
	var httpv = new XMLHttpRequest();
	httpv.open("GET","/get/" + id,true);
	httpv.onreadystatechange = function () {
		var xmlDoc, err, tab;
		// if successfully retrieved
		if(httpv.readyState == 4 && httpv.status == 200) {
			xmlDoc=httpv.responseXML;
			err = testerror(xmlDoc);
			if (err == 'auth') {
				authenticate(function () {
					updatemoviemodel(id);
				});
			} else if (err == 'success') {
				var movie, m;
				m = xmlDoc.getElementsByTagName('movie');
				if (m && m.length > 0)
					m = m[0];
				else
					return; // some error

				movie = getfields(m);
				row = movielist[movie.id].row;
				movielist[movie.id] = movie;
				updatemovierow(movie, row);
			} else {
				alert('Failed: ' + httpv.responseText);
			}

		}
	}
	httpv.send(null);
}

// Function: vote(id, v)
//  change vote for a movie
//
// Parameter:
//	id - movie id
//	v - new vote
function vote(id, v) 
{
	var http = new XMLHttpRequest();
	http.open("GET","/vote/" + id + "/" + v,true);
	http.onreadystatechange = function () {
		if(http.readyState == 4 && http.status == 200) {
			var xmlDoc=httpv.responseXML;
			err = testerror(xmlDoc);
			if (err == 'auth') {
				authenticate(function () {
					vote(id,v);
				});
			} else if (err == 'success') {
				votes[id] = v;
				updatemoviemodel(id);
			}
		}
	}
	http.send(null);
}

// Function: flipwatch(id)
//  change watch state for a movie
//
// Parameter:
//	id - movie id
function flipwatch(id) 
{
	var http = new XMLHttpRequest();
	http.open("GET","/watch/" + id ,true);
	http.onreadystatechange = function () {
		if(http.readyState == 4 && http.status == 200) {
			var xmlDoc=httpv.responseXML;
			var err = testerror(xmlDoc);
			if (err == 'auth') {
				authenticate(function () {
					flipwatch(id);
				});
			} else if (err == 'success') {
				var i = watches.indexOf(id.toString());
				if (i<0) {
					watches.push(id.toString());
					movielist[id].watches ++;
				} else {
					watches.splice(i);
					movielist[id].watches --;
				}
				var movie = movielist[id];
				var row = movie.row;
				updatemovierow(movie,row);
			}
		}
	}
	http.send(null);
}


// Function: loadwatchlist()
// load the list of movies watched by current user
function loadwatchlist() 
{
	var http = new XMLHttpRequest();
	http.open("GET","/watches",true);
	http.onreadystatechange = function () {
		var xmlDoc, err, l, m;

		if(http.readyState == 4 && http.status == 200) {
			xmlDoc=http.responseXML;
			err = testerror(xmlDoc);
			if (err == 'auth') {
				authenticate(loadwatchlist);
			} else if (err == 'success') {
				// else, it is success
				x=xmlDoc.getElementsByTagName("watchlist");
				if (x.length == 0)
					watches = [];
			
				l = [];

				for (m = x[0].firstElementChild; m != null; 
						m = m.nextElementSibling) {
					l.push(m.id);
				}
				watches =  l;
			} else {
				alert(http.responseText);
			}
		}
	}
	http.send(null);
}


loadwatchlist();
loadvotes();
loadmovielist();
