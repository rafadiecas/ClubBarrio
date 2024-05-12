
$(document).ready(function () {
    // Para añadir al carrito
    $(document).on('click', '.btn-add', function (e) {
        e.preventDefault();
        console.log("Botón añadir clicado");
        var productTallaId = $(this).data('product-talla-id');  // Cambia 'product-id' a 'product-talla-id'
        console.log("ProductTalla ID: " + productTallaId);
        $.ajax({
            url: '/ClubBarrioApp/tienda/carrito/anyadir/' + productTallaId + '/',  // Usa productTallaId en lugar de productId
            type: 'POST',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            },
            success: function (response) {
                // ...
                // Actualiza el valor del campo de entrada
                $('#form' + productTallaId).val(response.productQuantities[productTallaId]);  // Usa productTallaId en lugar de productId
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('Error:', errorThrown);
            }
        });
    });

    // Para restar del carrito
$(document).on('click', '.btn-subtract', function (e) {
    e.preventDefault();
    var productTallaId = $(this).data('product-talla-id');
    var productElement = $('#product' + productTallaId);
    var formElement = $('#form' + productTallaId);
    $.ajax({
        url: '/ClubBarrioApp/tienda/carrito/restar/' + productTallaId + '/',
        type: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        success: function (response) {
            var formElement = $('#form' + productTallaId);
            formElement.val(response.productQuantities[productTallaId]);

            if (formElement.val() === "") {
                $('#product' + productTallaId).remove();
                $('#hr' + productTallaId).remove();
            }

            $('.mb-0.text-muted').attr('id', 'totalItemsText');
            $('.text-uppercase').attr('id', 'totalItemsUpper');
            $('#totalItemsText').text(response.totalItems + " productos");
            $('#totalItemsUpper').text(response.totalItems + " Productos");
            $('.total').text('€ ' + response.totalPrice);

            formElement.val(response.productQuantities[productTallaId]);
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log('Error:', errorThrown);
        }
    });
});

// Para eliminar del carrito
$(document).on('click', '.btn-delete', function (e) {
    e.preventDefault();
    var productTallaId = $(this).data('product-talla-id');
    $.ajax({
        url: '/ClubBarrioApp/tienda/carrito/eliminar/' + productTallaId + '/',
        type: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        success: function (response) {
            $('#product' + productTallaId).remove();
            $('#hr' + productTallaId).remove();

            $('.mb-0.text-muted').attr('id', 'totalItemsText');
            $('.text-uppercase').attr('id', 'totalItemsUpper');
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