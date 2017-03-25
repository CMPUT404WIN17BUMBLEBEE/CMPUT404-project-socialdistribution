
//global variables
var incoming;
var receivedData;
var interval; 

//code for getting the csrf cookie from https://docs.djangoproject.com/en/1.10/ref/csrf/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
//code also from https://docs.djangoproject.com/en/1.10/ref/csrf/ to set the header for the token
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/*
http://stackoverflow.com/a/20307569
Answered by Yuvi on Stack Overflow: http://stackoverflow.com/users/2387772/yuvi
*/
//send GET request to recieve github posts in response
var checkGithub = function(){
$.ajax({
    url: '/createGithubPosts',
    type: 'get', 
    dataType: 'json',
    success: function(data) {
	console.log(data);
	console.log("success!");
        receivedData = data;
	if(( !$.isArray(data) || !data.length )){ //no new github posts returned http://stackoverflow.com/a/16350718 Answered by Arun P Johny on Stack Overflow http://stackoverflow.com/users/114251/arun-p-johny
		console.log("no new github posts");
		setTimeout(function(){checkGithub()}, interval);
		return;
	}

	if($("incoming").find("#incomingButton").length===0){ //checks if it has a button as a child
		createButton();
	}
	setTimeout(function(){checkGithub()}, interval);
    },
    failure: function(data) { 
	console.log("failure!");
	setTimeout(function(){checkGithub()}, interval);
        return;
    }
}); 
}

$(document).ready(
function(){
//interval of checking...3 minutes
interval = 1000 * 60 * 1;
incoming = document.getElementById("incoming");
setTimeout(checkGithub, interval);
});



function showPosts(){
//displays the new posts once the button was clicked
	//delete the button
	$("#incomingButton").remove();	
	var i;	
	for(i=0;i<receivedData.length;i++){
	//console.log(receivedData[i]);
	//incoming.appendChild(receivedData[i]);
	}

	
	
}

function createButton(){
//create the new posts button
alert("button!");
var btn = document.createElement("button");
btn.id = "incomingButton";
var text = document.createTextNode("New Posts");
btn.appendChild(text);
incoming.appendChild(btn);
btn.onclick = showPosts;

}


//next POST to the posts page, update the page with the info in the response

//http://www.tangowithdjango.com/book/chapters/ajax.html
//delete a post:
//send a delete request

//post a comment:
//get request for the comments on this post
//generate them, then send a POST request with the new comment in it
