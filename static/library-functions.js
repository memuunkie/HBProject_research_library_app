"use strict";


function displayUserResults(results) {
    // Function for showing list of users

    var user_list = $("#result-user-list");

    for(var i = 0; i < results.length; i++) {
       user_list.append("<li>" + results[i]['fname'] + " " + results[i]['lname'] + "</li>");
    }
}

function showUserResults(evt) {
    // Function to send form info to server as GET
    evt.preventDefault();
        //prevent from working automatically
    var email = "/find-users.json?email=" + $("#search-email").val();
    var fname = "&fname=" + $("#search-fname").val();
    var lname = "&lname=" + $("#search-lname").val();

    var url = email+fname+lname;

    $.get(url, displayUserResults);
}

$("#user-search").on('submit', showUserResults);