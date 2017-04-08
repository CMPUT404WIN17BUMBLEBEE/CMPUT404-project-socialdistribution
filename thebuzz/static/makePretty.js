//highlight the current feed we are on ;)

$(document).ready(
function(){
var url = window.location.href.split("/");
var navBar = $("#nav");
var current;

if( url[3] === "posts" ){
current = $(navBar).find("#news-feed")[0];
$(current).css("background-color", "#fff5cc");
$(current).css("margin-bottom", "-10px");
$("#news-feed a").hover(
function(){
    $(this).css("color","#ffd11a");
},
function(){
    $(this).css("color","black");
});
}

if( url[3] === "author" && url[5] === "profile" ){
current = $(navBar).find("#profile")[0];
$(current).css("background-color", "#fff5cc");
$(current).css("margin-bottom", "-10px");
$("#profile a").hover(
function(){
    $(this).css("color","#ffd11a");
},
function(){
    $(this).css("color","black");
});
}

if( url[3] === "friends" ){
current = $(navBar).find("#friends")[0];
$(current).css("background-color", "#fff5cc");
$(current).css("margin-bottom", "-10px");
$("#friends a").hover(
function(){
    $(this).css("color","#ffd11a");
},
function(){
    $(this).css("color","black");
});
}

if( url[3] === "author" && url[5] === "posts" ){
current = $(navBar).find(".myposts")[0];
$(current).css("background-color", "#fff5cc");
$(current).css("margin-bottom", "-10px");
$(".myposts a").hover(
function(){
    $(this).css("color","#ffd11a");
},
function(){
    $(this).css("color","black");
});

}
});


