
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
    statusCode: {
	200: function(data) {
	console.log(data);
	console.log("success!");
        receivedData = receivedData.concat(data);
	console.log(receivedData);
	/*if(( !$.isArray(receivedData) || !receivedData.length )){ //no new github posts returned http://stackoverflow.com/a/16350718 Answered by Arun P Johny on Stack Overflow http://stackoverflow.com/users/114251/arun-p-johny
		console.log("no new github posts");
		setTimeout(function(){checkGithub()}, interval);
		return;
	}*/
	console.log($("#incomingButton").length);
	if($("#incomingButton").length===0){ //checks if it has a button as a child
		createButton();
	}
	setTimeout(function(){checkGithub()}, interval);
    },
	204: function(data) {
	console.log("nothing to see here");
	setTimeout(function(){checkGithub()}, interval);
	},

	500: function(data) {
	setTimeout(function(){checkGithub()}, interval);
	}

	}
}); 
}

$(document).ready(
function(){
//set onclick listeners for post buttons already displayed
$(".deleteButton").each(function(){
this.addEventListener("click", deletePost); 
 });

//set onclick listeners for comment buttons already displayed
$(".commentButton").each(function(){
this.addEventListener("click", commentPost); 
 });


//interval of checking...5 minutes
interval = 1000 * 60 * 5;
incoming = document.getElementById("incoming");
receivedData = [];
checkGithub();
//setTimeout(checkGithub, interval);
});

function createPost(postInfo){
//creates a post to be appended to the page
var container = document.createElement("div");
container.id = "post-blocks";
var bar = document.createElement("div");
bar.id = "post-title-bar";
container.appendChild(bar);

var author = document.createElement("div");
author.id = "author";
author.innerHTML = "<a href = '/author/" + postInfo["associated_author"] + "/profile'>" + postInfo["displayName"] + "</a>";
var postTitle = document.createElement("div");
postTitle.id = "post-title";
postTitle.innerHTML = "<a id = 'postlink' href = \"/posts/" + postInfo["id"] +"\">" + postInfo["title"] +"</a>"
var postDate = document.createElement("div");
postDate.id = "post-date";
postDate.innerHTML = postInfo["published"];
bar.appendChild(author);
bar.appendChild(postTitle);
bar.appendChild(postDate);

var postContents = document.createElement("div");
postContents.innerHTML = postInfo["content"];
container.appendChild(postContents);
var postDelete = document.createElement("div");
postDelete.id = "delet-div";
var commentbtn = document.createElement("button");
commentbtn.className = "commentButton"
commentbtn.addEventListener("click", commentPost);
commentbtn.innerHTML = "Comment";
postDelete.append(commentbtn);

if(postInfo["currentId"] === postInfo["associated_author"]){
//we only want to have the option to delete our own posts

	var delbtn = document.createElement("button");
	delbtn.className = "deleteButton";
	delbtn.addEventListener("click", deletePost);
	delbtn.innerHTML = "Delete";
	postDelete.append(delbtn);
	
}

container.appendChild(postDelete);
return container;


}


function showPosts(){
//displays the new posts once the button was clicked
	//delete the button
	$("#incomingButton").remove();
	if($("#no-posts").length!==0){ 
		$("#no-posts").remove(); //remove the part about there being no posts
	}	
	var i, newpost;	
	for(i=0;i<receivedData.length;i++){
	newpost = createPost(receivedData[i]);
	//incoming.appendChild(newpost);
	$(newpost).insertAfter(incoming);
	}
	receivedData = [];
	
	
}

function createButton(){
//create the new posts button
var btn = document.createElement("button");
btn.id = "incomingButton";
var text = document.createTextNode("New Posts");
btn.appendChild(text);
incoming.appendChild(btn);
btn.onclick = showPosts;

}


function deletePost(element){
//uses ajax to delete a post
var bigparent = $(this).closest("#post-blocks");
var pID = $(bigparent).find("#postlink")[0].getAttribute("href");
console.log(pID);

if(confirm("Are you sure you want to delete this post?")){


$.ajax({
    url: pID,// + "/info",
    type: 'delete', 
    dataType: 'json',
    statusCode: {
	204: function(data) { //success!
	console.log("deleted!");
	$(bigparent).fadeOut();
	//$(bigparent).empty();
	//bigparent.remove();

	},

	500: function(data) {
	console.log("Deleting a post -- something went wrong");
	},

	404: function(data) {
	alert("Post not found");
	},

	}
  }); 
}

}


function commentPost(){
//retrieves the full post (considering long posts are shortened)
//shows the comments on the post and readies the post for a new comment
console.log("comment!");
var bigparent = $(this).closest("#post-blocks");
var pID = $(bigparent).find("#postlink")[0].getAttribute("href");

$.ajax({
    url: pID,
    type: 'get', 
    dataType: 'json',
    statusCode: {
	200: function(data) { //success!
	console.log(data);
	},

	500: function(data) {
	console.log("Fetching comments -- something went wrong");
	},

	404: function(data) {
	alert("Post not found");
	},

	}
  }); 



}



//post a comment:
//get request for the comments on this post
//generate them, then send a POST request with the new comment in it
