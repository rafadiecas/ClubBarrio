// Espera a que el documento esté listo
$(document).ready(function () {

    // Añade un evento de clic al botón de añadir
    $(document).on('click', '.btn-add', function (e) {
        e.preventDefault(); // Previene la acción por defecto del botón
        var productId = $(this).data('product-id'); // Obtiene el ID del producto del atributo data del botón

        // Realiza una petición AJAX para añadir el producto al carrito
        $.ajax({
            url: '/ClubBarrioApp/tienda/carrito/anyadir/' + productId + '/',
            type: 'POST',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')); // Añade el token CSRF a la petición
            },
            success: function (response) {
                // Actualiza la interfaz del carrito con la respuesta obtenida
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('#totalPrice').text("€ " + response.totalPrice);
                $('#form' + productId).val(response.productQuantities[productId]);

                // Si la cantidad del producto es 5 o más, deshabilita el botón de añadir
                if (response.productQuantities[productId] >= 5) {
                    $('.btn-add[data-product-id="' + productId + '"]').prop('disabled', true);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                // Muestra un mensaje de error en la consola si la petición falla
                console.log('Error:', errorThrown);
            }
        });
    });

    // Añade un evento de clic al botón de restar
    $(document).on('click', '.btn-subtract', function (e) {
        e.preventDefault(); // Previene la acción por defecto del botón
        var productId = $(this).data('product-id'); // Obtiene el ID del producto del atributo data del botón

        // Realiza una petición AJAX para restar el producto del carrito
        $.ajax({
            url: '/ClubBarrioApp/tienda/carrito/restar/' + productId + '/',
            type: 'POST',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')); // Añade el token CSRF a la petición
            },
            success: function (response) {
                // Actualiza la interfaz del carrito con la respuesta obtenida
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('#totalPrice').text("€ " + response.totalPrice);
                $('#form' + productId).val(response.productQuantities[productId]);

                // Si la cantidad del producto es menos que 5, habilita el botón de añadir
                if (response.productQuantities[productId] < 5) {
                    $('.btn-add[data-product-id="' + productId + '"]').prop('disabled', false);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                // Muestra un mensaje de error en la consola si la petición falla
                console.log('Error:', errorThrown);
            }
        });
    });

    // Añade un evento de clic al botón de eliminar
    $(document).on('click', '.btn-delete', function (e) {
        e.preventDefault(); // Previene la acción por defecto del botón
        var productId = $(this).data('product-id'); // Obtiene el ID del producto del atributo data del botón

        // Realiza una petición AJAX para eliminar el producto del carrito
        $.ajax({
            url: '/ClubBarrioApp/tienda/carrito/eliminar/' + productId + '/',
            type: 'POST',
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')); // Añade el token CSRF a la petición
            },
            success: function (response) {
                // Actualiza la interfaz del carrito con la respuesta obtenida
                $('#totalItemsText').text(response.totalItems + " productos");
                $('#totalItemsUpper').text(response.totalItems + " Productos");
                $('#totalPrice').text("€ " + response.totalPrice);
            },
            error: function (xhr, textStatus, errorThrown) {
                // Muestra un mensaje de error en la consola si la petición falla
                console.log('Error:', errorThrown);
            }
        });
    });

    // Limita la cantidad de un producto a 5
    $('.input-limit').each(function () {
        var productId = $(this).data('product-id'); // Obtiene el ID del producto del atributo data del botón
        var currentQuantity = parseInt($(this).val()); // Obtiene la cantidad actual del producto

        // Si la cantidad actual es mayor que 5, la establece a 5
        if (currentQuantity > 5) {
            $(this).val(5);
        }

        // Si la cantidad actual es 5 o más, deshabilita el botón de añadir
        if (currentQuantity >= 5) {
            $('.btn-add[data-product-id="' + productId + '"]').prop('disabled', true);
        }
    });
});

// Función para obtener el valor de una cookie
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
//<script type="text/javascript">
//     let numero = prompt("Introduce tu numero de dni sin letra");
//
//     if(numero.length != 8 || isNaN(numero) || numero < 0 || numero > 99999999){
//         alert("El numero no es correcto");
//     }else{
//
//         lista_letras = ['T', 'R', 'W', 'A', 'G', 'M', 'Y', 'F', 'P', 'D', 'X', 'B', 'N', 'J', 'Z', 'S', 'Q', 'V', 'H', 'L', 'C', 'K', 'E'];
//
//         let letra_dni = lista_letras[numero % 23];
//
//         alert("Tu letra de DNI es: " + letra_dni);
//
//
//     }
// </script>
//<script>
//     let confrimacion = confirm("¿Quieres introducir una cadena de texto?");
//     if (confrimacion == true) {
//         let cadena = prompt("Introduce una cadena de texto");
//         alert('hola');
//     }
//     else {
//         alert("No has introducido una cadena de texto");
//     }
// </script>