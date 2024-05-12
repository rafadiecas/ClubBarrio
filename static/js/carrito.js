$(document).ready(function () {
    // Para añadir al carrito
    $(document).on('click', '.btn-add', function (e) {
        e.preventDefault();
        console.log("Botón añadir clicado");
        var productId = $(this).data('product-id');
        console.log("Product ID: " + productId);
        $.ajax({
            url: '/ClubBarrioApp/tienda/carrito/anyadir/' + productId + '/',
            type: 'POST',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            },
            success: function (response) {
                console.log("Response: ", response);
                // Asigna IDs a los elementos
                $('.mb-0.text-muted').attr('id', 'totalItemsText');
                $('.text-uppercase').attr('id', 'totalItemsUpper');
                // $('h5:contains("€")').attr('id', 'totalPrice');

                // Actualiza la interfaz del carrito aquí
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('.total').text("€ " + response.totalPrice);
                // Actualiza el valor del campo de entrada
                $('#form' + productId).val(response.productQuantities[productId]);
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('Error:', errorThrown);
            }
        });
    });

    // Para restar del carrito
    $(document).on('click', '.btn-subtract', function (e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        var productElement = $('#product' + productId); // Almacena el resultado del selector en una variable
        var formElement = $('#form' + productId); // Almacena el resultado del selector en una variable
        $.ajax({
            url: '/ClubBarrioApp/tienda/carrito/restar/' + productId + '/',
            type: 'POST',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            },
            success: function (response) {
                // Si la cantidad del producto es 0, elimina el elemento HTML correspondiente al producto
                var formElement = $('#form' + productId);
                formElement.val(response.productQuantities[productId]);

                // Si el valor del input es "", elimina el elemento HTML correspondiente al producto
                if (formElement.val() === "") {
                    $('#product' + productId).remove();
                    $('#hr' + productId).remove();
                }

                // Asigna IDs a los elementos
                $('.mb-0.text-muted').attr('id', 'totalItemsText');
                $('.text-uppercase').attr('id', 'totalItemsUpper');
                // $('h5:contains("€")').attr('id', 'totalPrice');

                // Actualiza la interfaz del carrito aquí
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('.total').text('€ ' + response.totalPrice);

                // Actualiza el valor del campo de entrada
                formElement.val(response.productQuantities[productId]); // Reutiliza la variable en lugar del selector
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('Error:', errorThrown);
            }
        });
    });

    // Para eliminar del carrito
    $(document).on('click', '.btn-delete', function (e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        $.ajax({
            url: '/ClubBarrioApp/tienda/carrito/eliminar/' + productId + '/',
            type: 'POST',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            },
            success: function (response) {
                // Elimina el elemento HTML correspondiente al producto
                $('#product' + productId).remove();
                $('#hr' + productId).remove();

                // Asigna IDs a los elementos
                $('.mb-0.text-muted').attr('id', 'totalItemsText');
                $('.text-uppercase').attr('id', 'totalItemsUpper');
                // $('h5:contains("€")').attr('id', 'totalPrice');

                // Actualiza la interfaz del carrito aquí
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('.total').text("€ " + response.totalPrice);
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('Error:', errorThrown);
            }
        });
    });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}