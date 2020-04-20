$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res._id);
        $("#customer_id").val(res.customer_id);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_id").val("");
        $("#customer_id").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart WORKS
    // ****************************************

    $("#create-btn").click(function () {

        var customer_id = $("#customer_id").val();

        var data = {
            "customer_id": customer_id
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {

        var shopcart_id = $("#shopcart_id").val();
        var customer_id = $("#customer_id").val();

        var data = {
            "customer_id": customer_id
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/shopcarts/" + shopcart_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        var shopcart_id = $("#shopcart_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts/" + shopcart_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        var shopcart_id = $("#shopcart_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/shopcarts/" + shopcart_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#customr_id").val("");
        clear_form_data()
    });

    // ****************************************
    // List All Shopcarts
    // ****************************************

    $("#list-btn").click(function () {

        var customer_id = $("#customer_id").val();

        var queryString = ""

        if (customer_id) {
            queryString += 'customer_id=' + customer_id
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Shopcart_ID</th>'
            header += '<th style="width:40%">Customer_ID</th>'
            $("#search_results").append(header);
            var firstShopcart = "";
            for(var i = 0; i < res.length; i++) {
                var shopcart = res[i];
                var row = "<tr><td>"+shopcart.id+"</td><td>"+shopcart.customer_id+"</td><td>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstShopcart = shopcart;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstShopcart != "") {
                update_form_data(firstShopcart)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})