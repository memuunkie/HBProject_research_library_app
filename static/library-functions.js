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
                            var formValues = {
                                'user-id': this.value
                            }
                            console.log(formValues);
                            $.post(url, formValues, function(res){
                                console.log(res);
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

// $("#result-user-list").on('click', 'button', function() {
//     console.log("Testing, testing, 123" + $('button').attr('user-id'));
// } );


//  ("<button user-id=" + results[i]['user_id']
//                         + " class=\"btn btn-primary\"type=\
//                         \"submit\" >Add Visit</button>")