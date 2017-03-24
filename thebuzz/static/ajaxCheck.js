//lets put some ajax in here

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
//send GET
var incoming = document.getElementById("incoming");
var data;
 
var checkGithub = function(){
$.ajax({
    url: '/createGithubPosts',
    type: 'get', 
    success: function(data) {
        //alert(data);
	if(data === null){ //either no data or youve hit github's api limit - in that case, can't check for an hour
		alert("wait an hour"); //remove this after testing!
		return;
	}

	//console.log(incoming.children().find("incomingButton").length);
	//if incoming has no children
	if($("incoming").find("#incomingButton").length===0){ //checks if it has a button as a child
		createButton();
	}

    }//,
    //failure: function(data) { 
     //   alert('error');
   // }
}); 
};

//interval of checking...3 minutes
var interval = 1000 * 60 * 3;  
setInterval(checkGithub, interval);


function showPosts(){
//displays the posts once the button was clicked
	//delete the button
	$("#incomingButton").remove();	
	var i;	
	for(i=0;i<data.length();i++){
	incoming.appendChild(data[i]);
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
