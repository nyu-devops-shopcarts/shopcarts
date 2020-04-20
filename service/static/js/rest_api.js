$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res._id);
        $("#customer_id").val(res.customer_id);
        //$("#items").val(res.items);
        //$("#pet_category").val(res.category);
        //if (res.available == true) {
        //    $("#pet_available").val("true");
        //} else {
        //    $("#pet_available").val("false");
        //}
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_id").val("");
        $("#customer_id").val("");
        //$("#items").val("");
        //$("#pet_available").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        var customer_id = $("#customer_id").val();
        //var items = $("#items").val();
        //var available = $("#pet_available").val() == "true";

        var data = {
            //"id": shopcart_id,
            "customer_id": customer_id,
            //"items": items
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
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        var pet_id = $("#pet_id").val();
        var name = $("#pet_name").val();
        var category = $("#pet_category").val();
        var available = $("#pet_available").val() == "true";

        var data = {
            "name": name,
            "category": category,
            "available": available
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/pets/" + pet_id,
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
    // Retrieve a Pet
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
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        var pet_id = $("#pet_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/pets/" + pet_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Pet has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        //var shopcart_id = $("#shopcart_id").val();
        var customer_id = $("#customer_id").val();
        //var items = $("#items").val();

        var queryString = ""

        if (customer_id) {
            queryString += 'customer_id=' + customer_id
        }
        //if (customer_id) {
        //    if (queryString.length > 0) {
        //        queryString += '&customer_id=' + customer_id
        //    } else {
        //        queryString += 'customer_id=' + customer_id
        //    }
        //}
        //if (available) {
        //    if (queryString.length > 0) {
        //        queryString += '&available=' + available
        //    } else {
        //        queryString += 'available=' + available
        //    }
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
            header += '<th style="width:40%">Items</th>'
            //header += '<th style="width:10%">Available</th></tr>'
            $("#search_results").append(header);
            var firstShopcart = "";
            for(var i = 0; i < res.length; i++) {
                var shopcart = res[i];
                var row = "<tr><td>"+shopcart._id+"</td><td>"+shopcart.customer_id+"</td><td>"+shopcart.items+"</td><td>";
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