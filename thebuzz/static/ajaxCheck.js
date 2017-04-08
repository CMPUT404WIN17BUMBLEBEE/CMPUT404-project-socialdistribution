
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
	//console.log(data);
	//console.log("success!");
        receivedData = receivedData.concat(data);
	//console.log(receivedData);
	
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
postTitle.innerHTML = postInfo["title"]; 
var postDate = document.createElement("div");
postDate.id = "post-date";
postDate.innerHTML = postInfo["published"];
bar.appendChild(author);
bar.appendChild(postTitle);
bar.appendChild(postDate);

var postContents = document.createElement("div");
postContents.className = "pContents";
postContents.innerHTML = postInfo["content"];
container.appendChild(postContents);
var postDelete = document.createElement("div");
postDelete.id = "delet-div";

var hiddenVal = document.createElement("div");
hiddenVal.className = "hidden";
hiddenVal.textContent = postInfo["id"];
postDelete.append(hiddenVal);

var commentbtn = document.createElement("button");
commentbtn.className = "commentButton"
commentbtn.addEventListener("click", commentPost);
commentbtn.innerHTML = "Comments";
postDelete.append(commentbtn);
console.log(postInfo["currentId"]);
console.log(postInfo["associated_author"]);

if(postInfo["currentId"] === postInfo["associated_author"]){
//we only want to have the option to delete our own posts

	var editbtn = document.createElement("button");
	editbtn.className = "editButton";
	editbtn.addEventListener("click", function(){
	location.href = postInfo["id"] + "/edit_post"; //TODO: make sure this works if i get to obtaining incoming regular posts
	});
	editbtn.innerHTML = "Edit";
	postDelete.append(editbtn);
	var delbtn = document.createElement("button");
	delbtn.className = "deleteButton";
	delbtn.addEventListener("click", deletePost);
	delbtn.innerHTML = "Delete";
	postDelete.append(delbtn);
	
}
if(postInfo["categories"]!==null){
var i,tmp;
	for(i=0;i<postInfo["categories"].length;i++){
	tmp = document.createElement("span");
	tmp.id = "category_values";
	tmp.textContent = "#" + postInfo["categories"][i]
	postDelete.append(tmp);
	}
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
var pID = $(bigparent).find(".hidden")[0].textContent;


if(confirm("Are you sure you want to delete this post?")){


$.ajax({
    url: pID + "/action",
    type: 'delete', 
    dataType: 'json',
    statusCode: {
	204: function(data) { //success!
	$(bigparent).fadeOut();

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

var bigparent = $(this).closest("#post-blocks");
var pID = $(bigparent).find(".hidden")[0].textContent;


$.ajax({
    url: pID + "/action",
    type: 'get', 
    dataType: 'json',
    statusCode: {
	200: function(data) { //success!
	replacePost(bigparent,data);

	},

	500: function(data) {
	console.log("Fetching Post +  Comments -- something went wrong");
	},

	404: function(data) {
	alert("Post not found");
	},

	}
  }); 



}

function replacePost(pBlock, data){
//replaces the post with the full post, including the comments
//TODO: update this once jill gets images working properly

var contents = $(pBlock).find(".pContents");
contents = data["content"]; //show full content if post is too long to show it all
var hideButton = $(pBlock).find(".commentButton");

hideButton[0].textContent = "Hide";
hideButton[0].removeEventListener("click", commentPost);
hideButton[0].addEventListener("click", hideCommentSection); 

var cmtSection;
var holder = document.createElement("div");
holder.id = "detail_content";
pBlock.append(holder);
var commentLabel = document.createElement("div");
commentLabel.id = "comment-label";
commentLabel.textContent = "Comments";	
holder.append(commentLabel);

if(data["comments"].length>0){
	var i;
	var cmtBar,cAuthor,cDate,cComment;
	

	for(i=data["comments"].length - 1;i>=0;i--){
		
		cmtSection = document.createElement("div");
		cmtSection.className = "comment-sections";
		cmtBar = document.createElement("div");
		cmtBar.id = "comment-title-bar";	
		cAuthor = document.createElement("div");
		cAuthor.id = "comment_author";
		cAuthor.innerHTML = "<a class = 'authlink' href= 'http://127.0.0.1:8000/author/" + data["comments"][i]["author"]["id"] + "/profile'>" + data["comments"][i]["author"]["displayName"] + "</a>";
		cDate = document.createElement("div");
		cDate.id = "comment_date";
		cDate.textContent = data["comments"][i]["published"]
		cComment = document.createElement("div");
		cComment.id = data["comments"][i]["id"];
		cComment.textContent = data["comments"][i]["comment"];

		if(data["comments"][i]["author"]["id"]===data["currentId"]){ //if the user posted it, show a delete button
			var delbtn = document.createElement("button");
			delbtn.className = "deleteCommentButton";
			delbtn.addEventListener("click", function(){
			deleteComment(this);
			});
			delbtn.innerHTML = "Delete";
			cComment.append(delbtn);
			}


		cmtBar.append(cAuthor);
		cmtBar.append(cDate);
				
		cmtSection.append(cmtBar);		
		cmtSection.append(cComment);
		
		holder.append(cmtSection);
		//$(cmtSection).insertAfter(pBlock);		
		}
	

}

//stuff that allows them to leave a comment

var pID = $(pBlock).find(".hidden")[0].textContent;

var tbox = document.createElement("textarea");
tbox.setAttribute("rows",2);
tbox.setAttribute("cols",20);
tbox.className = "tbox";
tbox.setAttribute("name","commentText");

var cmtBtn = document.createElement("button");
cmtBtn.setAttribute("type","submit");
cmtBtn.textContent = "Comment";
cmtBtn.id = "cmtBtn";
cmtBtn.addEventListener("click",sendCommentToPost);


//form.append(tbox);
//form.append(cmtBtn);

//holder.append(form);
holder.append(tbox);
holder.append(cmtBtn);

}


function sendCommentToPost(){
//use a post request to send the comment

var bigparent = $(this).closest("#post-blocks");
var pID = $(bigparent).find(".hidden")[0].textContent;
var text = $(bigparent).find(".tbox")[0].value;

if(text.trim() === "") return;

//var comment = {"comment": text};


$.ajax({
    url: pID + "/add_comment.html",//"/action",
    type: 'post', 
    contentType: 'application/json',
    data: text,
    statusCode: {
	201: function(data) { //success!
	appendComment(bigparent,data);
	

	},

	500: function(data) {
	console.log("Posting a comment -- something went wrong");
	},

	404: function(data) {
	alert("Post not found");
	},

	403: function(data) {
	alert("Unauthorized");
	},

	}
  }); 

}

function hideCommentSection(){
var parent = $(this).closest("#post-blocks");
var csection = $(parent).find("#detail_content");
$(csection).fadeOut(function(){
$(this).remove();
});

this.textContent = "Comment";
this.removeEventListener("click", hideCommentSection);
this.addEventListener("click", commentPost); 

}

function deleteComment(element){
//delete your own comment!

var celement = $(element).parent()[0];
var cID = celement.id;

$.ajax({
    url:  cID + "/delete_comment/",
    type: 'delete', 
        dataType: 'json',
    statusCode: {
	204: function(data) { //success!
	commentDisappear(celement);
	},

	500: function(data) {
	console.log("Posting a comment -- something went wrong");
	},

	404: function(data) {
	alert("Not found");
	},

	}
  }); 

}


function commentDisappear(element){
//removes the deleted comment
var cs = $(element).parent();
cs.fadeOut();

}

function appendComment(pBlock,data){
//puts the comment into the html of the page

var cs = $(pBlock).find("#detail_content");

cmtSection = document.createElement("div");
		cmtSection.className = "comment-sections";
		cmtBar = document.createElement("div");
		cmtBar.id = "comment-title-bar";	
		cAuthor = document.createElement("div");
		cAuthor.id = "comment_author";
		cAuthor.innerHTML = "<a class = 'authlink' href = 'http://127.0.0.1:8000/author/" + data["author"]["id"] + "/profile'>" + data["author"]["displayName"] + "</a>";
		cDate = document.createElement("div");
		cDate.id = "comment_date";
		cDate.textContent = data["published"]
		cComment = document.createElement("div");
		cComment.id = data["id"];
		cComment.textContent = data["comment"];

		
		if(data["author"]["id"]===data["currentId"]){ //if the user posted it, show a delete button
			var delbtn = document.createElement("button");
			delbtn.className = "deleteCommentButton";
			delbtn.addEventListener("click", function(){
			deleteComment(this);
			});
			delbtn.innerHTML = "Delete";
			cComment.append(delbtn);
			}

		cmtBar.append(cAuthor);
		cmtBar.append(cDate);
		cmtSection.append(cmtBar);		
		cmtSection.append(cComment);

		var tbox = $(pBlock).find(".tbox")[0];
		tbox.value = "";
		$(cmtSection).insertBefore(tbox);

}

//post a comment:
//get request for the comments on this post
//generate them, then send a POST request with the new comment in it
