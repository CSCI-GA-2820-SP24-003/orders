$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the order form with data from the response
    function update_order_form_data(res) {
        $("#order_id").val(res.id);
        $("#customer_id").val(res.customer_id);
        $("#order_date").val(res.order_date);
        $("#status").val(res.status);
        $("#shipping_address").val(res.shipping_address);
        $("#total_amount").val(res.total_amount);
        $("#payment_method").val(res.payment_method);
        $("#shipping_cost").val(res.shipping_cost);
        $("#expected_date").val(res.expected_date);
        $("#order_notes").val(res.order_notes);
    }

    /// Clears all order form fields
    function clear_order_form_data() {
        $("#customer_id").val("");
        $("#order_date").val("");
        $("#status").val("");
        $("#shipping_address").val("");
        $("#total_amount").val("");
        $("#payment_method").val("");
        $("#shipping_cost").val("");
        $("#expected_date").val("");
        $("#order_notes").val("");
    }

    // Updates the order form with data from the response
    function update_item_form_data(res) {
        $("#item_id").val(res.id);
        $("#item_order_id").val(res.order_id);
        $("#product_id").val(res.product_id);
        $("#name").val(res.name);
        $("#quantity").val(res.quantity);
        $("#unit_price").val(res.unit_price);
        $("#total_price").val(res.total_price);
        $("#description").val(res.description);
    }

    /// Clears all order form fields
    function clear_item_form_data() {
        $("#item_order_id").val("");
        $("#product_id").val("");
        $("#name").val("");
        $("#quantity").val("");
        $("#unit_price").val("");
        $("#total_price").val("");
        $("#description").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let order_date = $("#order_date").val();
        let status = $("#status").val();
        let shipping_address = $("#shipping_address").val();
        let total_amount = $("#total_amount").val();
        let payment_method = $("#payment_method").val();
        let shipping_cost = $("#shipping_cost").val();
        let expected_date = $("#expected_date").val();
        let order_notes = $("#order_notes").val();
        let items = []

        let data = {
            "customer_id": customer_id,
            "order_date": order_date,
            "status": status,
            "shipping_address": shipping_address,
            "total_amount": total_amount, 
            "payment_method": payment_method,
            "shipping_cost": shipping_cost,
            "expected_date": expected_date,
            "order_notes": order_notes,
            "items": items
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_order_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {

        let order_id = $("#order_id").val();
        let customer_id = $("#customer_id").val();
        let order_date = $("#order_date").val();
        let status = $("#status").val();
        let shipping_address = $("#shipping_address").val();
        let total_amount = $("#total_amount").val();
        let payment_method = $("#payment_method").val();
        let shipping_cost = $("#shipping_cost").val();
        let expected_date = $("#expected_date").val();
        let order_notes = $("#order_notes").val();
        let items = []

        let data = {
            "customer_id": customer_id,
            "order_date": order_date,
            "status": status,
            "shipping_address": shipping_address,
            "total_amount": total_amount, 
            "payment_method": payment_method,
            "shipping_cost": shipping_cost,
            "expected_date": expected_date,
            "order_notes": order_notes,
            "items":items
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/orders/${order_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_order_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_order_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_order_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_order_form_data()
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Cancel an Order
    // ****************************************
    $("#cancel-btn").click(function () {

        let order_id = $("#order_id").val(); 

        if (!order_id) {
            flash_message("Please enter an Order ID");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/orders/${order_id}/cancel`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            flash_message("Order cancellation successful");
            clear_order_form_data(); // Optionally clear form or update status
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    
    // ****************************************
    // Clear the Order form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_order_form_data()
    });

    // ****************************************
    // Search for an Order
    // ****************************************

    $("#search-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let order_date = $("#order_date").val();
        let status = $("#status").val();
        let total_amount = $("#total_amount").val();

        let queryString = ""

        if (customer_id) {
            queryString += 'customer-id=' + customer_id
        }
        if (order_date) {
            if (queryString.length > 0) {
                queryString += '&order-start=' + order_date
            } else {
                queryString += 'order-start=' + order_date
            }
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }
        if (total_amount) {
            if (queryString.length > 0) {
                queryString += '&total-min=' + total_amount
            } else {
                queryString += 'total-min=' + total_amount
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_order_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Customer_id</th>'
            table += '<th class="col-md-2">Order_Date</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Shipping_Address</th>'
            table += '<th class="col-md-2">Total_Amount</th>'
            table += '<th class="col-md-2">Payment_Method</th>'
            table += '<th class="col-md-2">Shipping_Cost</th>'
            table += '<th class="col-md-2">Expected_Date</th>'
            table += '<th class="col-md-2">Order_Notes</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                table +=  `<tr id="row_${i}"><td>${order.id}</td><td>${order.customer_id}</td><td>${order.order_date}</td><td>${order.status}</td><td>${order.shipping_address}</td><td>${order.total_amount}</td><td>${order.payment_method}</td><td>${order.shipping_cost}</td><td>${order.expected_date}</td><td>${order.order_notes}</td></tr>`;
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_order_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_order_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Create an Item
    // ****************************************

    $("#create-item-btn").click(function () {

        let order_id = $("#item_order_id").val();
        let product_id = $("#product_id").val();
        let name = $("#name").val();
        let quantity = $("#quantity").val();
        let unit_price = $("#unit_price").val();
        let total_price = $("#total_price").val();
        let description = $("#description").val();

        let data = {
            "order_id": order_id,
            "product_id": product_id,
            "name": name,
            "quantity": quantity,
            "unit_price": unit_price, 
            "total_price": total_price,
            "description": description,
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/orders/" + order_id + "/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Item
    // ****************************************

    $("#update-item-btn").click(function () {

        let item_id = $("#item_id").val();
        let order_id = $("#item_order_id").val();
        let product_id = $("#product_id").val();
        let name = $("#name").val();
        let quantity = $("#quantity").val();
        let unit_price = $("#unit_price").val();
        let total_price = $("#total_price").val();
        let description = $("#description").val();

        let data = {
            "order_id": order_id,
            "product_id": product_id,
            "name": name,
            "quantity": quantity,
            "unit_price": unit_price, 
            "total_price": total_price,
            "description": description,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/orders/${order_id}/items/${item_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Item
    // ****************************************

    $("#retrieve-item-btn").click(function () {

        let item_id = $("#item_id").val();
        let order_id = $("#item_order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_item_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#delete-item-btn").click(function () {

        let item_id = $("#item_id").val();
        let order_id = $("#item_order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_item_form_data()
            flash_message("Item has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the Item form
    // ****************************************

    $("#clear-item-btn").click(function () {
        $("#item_id").val("");
        $("#flash_message").empty();
        clear_item_form_data()
    });

    // ****************************************
    // Search for an Item
    // ****************************************

    $("#search-item-btn").click(function () {

        let order_id = $("#item_order_id").val()
        let product_id = $("#product_id").val();
        let name = $("#name").val();

        let queryString = ""

        if (product_id) {
            queryString += 'product_id=' + product_id
        }
        if (name) {
            if (queryString.length > 0) {
                queryString += '&name=' + name
            } else {
                queryString += 'name=' + name
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}/items?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_item_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Order ID</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Unit Price</th>'
            table += '<th class="col-md-2">Total Price</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for(let i = 0; i < res.length; i++) {
                let item = res[i];
                table +=  `<tr id="row_${i}"><td>${item.id}</td><td>${item.order_id}</td><td>${item.product_id}</td><td>${item.name}</td><td>${item.quantity}</td><td>${item.unit_price}</td><td>${item.total_price}</td><td>${item.description}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_item_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_item_form_data(firstItem)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})