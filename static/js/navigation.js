$(function(){
    $('#logout').click(function() {
        if(confirm('Are you sure you want to log out ?')){
            return true;
        }

        alert('You have been logged out')

        return false;
    });
});





