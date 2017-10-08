"use strict";

/**************
    For doing a search of Users and rendering a list with buttons
**************/
function displayUserResults(results) {
    // Function for showing list of users

    var userList = $("#result-user-list");

    // remove any existing results
    userList.empty();

    //to check data against what rendered
    console.log(results);

    for(var i = 0; i < results.length; i++) {

        var btn = $("<button>", {
                    name: 'user-id',
                    value: results[i]['user_id'],
                    on: {
                        click: function() {
                            //check to see if right value sent
                            console.log(this.value);
                            var url = "/new-visit.json";
                            var buttonVal = {
                                'user-id': this.value
                                }
                            //show what is getting sent to server
                            console.log(buttonVal);
                            $.post(url, buttonVal, function(res){
                                //show what got back from server
                                console.log(res);

                                if (res == 'None') {
                                    userList.empty();
                                    userList.html("<p>USER ALREADY CHECKED IN</p>");
                                    } else {
                                    userList.empty();
                                    userList.html("<p>User has been added</p>");
                                    }                                    
                                });
                                            }
                        }
        });

        btn.html('Add Visit');

        userList.append("<li>" + results[i]['fname'] + 
                        " " + results[i]['lname'] + "<br>")
                        .append(btn);
    }
}

function showUserResults(evt) {
    // Function to send form info to server as GET
    evt.preventDefault();
        //prevent from working automatically
    var formInput = $("#user-search").serialize();

    var searchPath = "/find-users.json?";

    var url = searchPath + formInput;
    // check that url path looks right
    console.log(url);

    $.get(url, displayUserResults);
}

$("#user-search").on('submit', showUserResults);

/**************
    For doing a search of Books
**************/

function displayBookResults(results) {
    // Function for showing list of users

    var bookList = $("#result-book-list");

    bookList.empty();

    console.log(results);

    for(var i = 0; i < results.length; i++) {

        var btn = $("<button>", {
                        name: 'book-id',
                        value: results[i]['book_id'],
                        on: {
                            click: function() {
                                console.log(this.value);
                                var url = "/add-book.json";
                                var buttonVal = {
                                    'book-id': this.value,
                                    'visit-id': parseInt($('#visit-id').html()),
                                    }
                                $.post(url, buttonVal, function(res) {
                                        $('#result-book-list').empty();
                                        $('#result-book-list').html("<p>" + res + "</p>");
                                        console.log(res)
                                    });

                                }
                            }
                }

            );

        btn.html("Add Book");

        bookList.append("<li><b>" + results[i]['title'] + 
                        "</b><br>" + results[i]['author'] +
                        "<br>" + results[i]['call_num'] +
                        "<br>").append(btn);
    }
}

function showBookResults(evt) {
    // Function to send form info to server as GET
    evt.preventDefault();
        //prevent from working automatically
    var formInput = $("#book-search").serialize();

    var searchPath = "/find-books.json?";

    var url = searchPath + formInput;
    // check that url path looks right
    console.log(url);

    $.get(url, displayBookResults);
}

$("#book-search").on('submit', showBookResults);

/*************
    Display all the visits in the database
*************/

function displayCurrentVisitors(results) {
    //List of current checked-in visitors

    var visitorList = $("#current-visitors");

    // clear out the past visitor list
    $("#msg-bad").empty();
    visitorList.empty();
    // check data
    console.log(results);

    for (var i = 0; i < results.length; i++) {
        //check that results will render right
        console.log(results[i]['fname'] + " " + results[i]['lname']
                    + " " + results[i]['visit_timein']);

        var btn1 = $("<button>", {
                    id: 'btn1-' + results[i]['user_id'],
                    name: 'user-id',
                    value: results[i]['user_id'],
                    on: {
                        click: function() {
                            //check to see if right value sent
                            console.log(this.value);
                            var url = "/checkout.json";
                            var buttonVal = {
                                'user-id': this.value
                            }
                            //show what is getting sent to server
                            console.log(buttonVal);
                            $.post(url, buttonVal, function(res){
                                //show what got back from server
                                console.log(res);
                                if (res == 'None') {
                                    $("#msg-bad").html("User has outstanding books and cannot be checked out.");

                                } else {

                                    console.log(res);
                                    console.log(res['user_id']);
                                    $("#li-"+ res['user_id']).empty().html("User has been checked out.");
                                    $("#btn1-" + res['user_id']).remove();
                                    $("#btn2-" + res['user_id']).remove();
                                    $("#btn3-" + res['user_id']).remove();
                                    }

                            });
                        }
                    }
            });

        var btn2 = $("<button>", {
                    id: 'btn2-' + results[i]['user_id'],
                    name: 'add-book',
                    value: results[i]['user_id'],
                    on: {
                        click: function() {
                            var url = "/book-search?user-id="+ this.value;
                            $.get(window.location.href = url);
                        }
                    }
            });

        var btn3 = $("<button>", {
                    id: 'btn3-' + results[i]['user_id'],
                    name: 'return-book',
                    value: results[i]['user_id'],
                    on: {
                        click: function() {
                            var url = "/return-book?user-id="+ this.value;
                            $.get(window.location.href = url);
                        }
                    }
        });


        btn1.html('Check Out');
        btn2.html('Add Book');
        btn3.html('Return Books');

        visitorList.append("<li id=\"li-" + results[i]['user_id'] + "\">"
                        + results[i]['fname'] + " " + results[i]['lname'] 
                        + 
                        " in at " + formatDate(results[i]['visit_timein']))
                        .append(btn1).append(btn2).append(btn3);
    }
}

function getCurrentVisitors(evt) {
    //send query to server for all current checkin in visitors
    evt.preventDefault();

    $.get("/display-visitors", displayCurrentVisitors);

}

$("#display-visits").on('click', getCurrentVisitors);

/*************
    For logging in
*************/

function loginResults(results) {

    if (results == 'None') {
        $("#user-login").append("<p>No such user. Please register.</p>");
    } else {
        $('#user-login').empty();
        $("#user-register").remove();
        $("#user-login").html('You are logged in.');
    }

}

function loginUser(evt) {
    //Login in user and set up a session in server
    evt.preventDefault();

    var formInput = $("#log-in").serialize();

    console.log(formInput);

    $.post("/log-in.json", formInput, loginResults);

}

$("#log-in").on("submit", loginUser);


/*************
    Some helper functions to get it out of the way
**************/

function formatDate(date) {
    var newDate = new Date(date);
    var date = newDate.toDateString();
    var hour = newDate.getHours();
    var minutes = newDate.getMinutes();

    var time = function (hr, min) { 
        if (min < 10) {
            min = '0' + min;
        }
        if (hour > 12) {
            hour = hour - 12;
            min += 'PM';
        } else {
            min += 'AM';
        }
        return hour + ':' + min;
    };

    return date + ' ' + time(hour, minutes);

}