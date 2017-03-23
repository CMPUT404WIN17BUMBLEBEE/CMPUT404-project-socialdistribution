//lets put some ajax in here
/*
http://stackoverflow.com/a/20307569
Answered by Yuvi on Stack Overflow: http://stackoverflow.com/users/2387772/yuvi
*/

//var test = {{ user_username }}; 

alert(githubname);

$.ajax({
    url: 'https://api.github.com/users/' + githubname + '/events',
    type: 'get', 
    success: function(data) {
        alert(data);
    },
    failure: function(data) { 
        alert('error');
    }
}); 

