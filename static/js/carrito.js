



$(document).ready(function () {


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
                $('h5:contains("€")').attr('id', 'totalPrice');

                // Actualiza la interfaz del carrito aquí
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('#totalPrice').text("€ " + response.totalPrice);
                // Actualiza el valor del campo de entrada
                $('#form' + productId).val(response.productQuantities[productId]);

                // Verifica si la cantidad del producto es 5 o más
                if (response.productQuantities[productId] >= 5) {
                    $('.btn-add[data-product-id="' + productId + '"]').prop('disabled', true);
                }
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
                $('h5:contains("€")').attr('id', 'totalPrice');

                // Actualiza la interfaz del carrito aquí
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('#totalPrice').text("€ " + response.totalPrice);

                // Actualiza el valor del campo de entrada
                formElement.val(response.productQuantities[productId]); // Reutiliza la variable en lugar del selector

                // Verifica si la cantidad del producto es menos que 5
                if (response.productQuantities[productId] < 5) {
                    $('.btn-add[data-product-id="' + productId + '"]').prop('disabled', false);
                }
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
                $('h5:contains("€")').attr('id', 'totalPrice');

                // Actualiza la interfaz del carrito aquí
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('#totalPrice').text("€ " + response.totalPrice);
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('Error:', errorThrown);
            }
        });
    });
    $('.input-limit').each(function () {
    var productId = $(this).data('product-id');
    var currentQuantity = parseInt($(this).val());
    console.log("Initial check - Product ID:", productId, "Quantity:", currentQuantity);

    if (currentQuantity > 5) {
        currentQuantity = 5;
        $(this).val(currentQuantity);
        console.log("Quantity set to 5 for Product ID:", productId);
    }

    if (currentQuantity >= 5) {
        var button = $('.btn-add[data-product-id="' + productId + '"]');
        console.log("Button to disable:", button);
        button.prop('disabled', true);
    }
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
//LIMITADOR DE INPUTS
