"use strict";


function displayUserResults(results) {
    // Function for showing list of users

    var user_list = $("#result-user-list");

    // remove any existing results
    user_list.empty();

    //to check data against what rendered
    console.log(results);

    for(var i = 0; i < results.length; i++) {

        var btn = $("<button>", {
                    name: 'user-id',
                    value: results[i]['user_id'],
                    on: {
                        click: function() {

                            console.log(this.value);
                            var url = "/new-visit.json";
                            var buttonVal = {
                                'user-id': this.value
                            }
                            console.log(buttonVal);
                            $.post(url, buttonVal, function(res){
                                console.log(res);
                                user_list.empty();
                                user_list.html("<p>User has been added</p>");
                            });
                        }
                    }
        });

        btn.html('Add Visit');

        user_list.append("<li>" + results[i]['fname'] + 
                        " " + results[i]['lname'])
                        .append(btn);
    }
}

function showUserResults(evt) {
    // Function to send form info to server as GET
    evt.preventDefault();
        //prevent from working automatically
    var formInput = $("#user-search").serialize();

    var search_path = "/find-users.json?";

    var url = search_path + formInput;

    console.log(url);

    $.get(url, displayUserResults);
}

$("#user-search").on('submit', showUserResults);

function displayCurrentVisitors(results) {
    //List of current checked-in visitors

    var visitor_list = $("#current-visitors");
    visitor_list.empty();
    console.log(results);

    for (var i = 0; i < results.length; i++) {
        console.log(results[i]['fname'] + results[i]['lname']);
        visitor_list.append("<li>" + results[i]['fname'] + 
                        " " + results[i]['lname']);
    }
}

function getCurrentVisitors(evt) {
    //send query to server for all current checkin in visitors
    evt.preventDefault();

    $.get("/display-visitors", displayCurrentVisitors);

}

$("#display-visits").on('click', getCurrentVisitors);
