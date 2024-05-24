// Function to confirm the deletion of a record
function confirmarEliminarUsuario(event) {
    // Show a confirmation dialog to the user
    var confirmacion = confirm('¿Seguro que desea eliminar?');
    // If the user does not confirm, prevent the default action (which is the deletion)
    if (!confirmacion) {
        event.preventDefault();
    }
}

// When the document is ready
$(document).ready(function(){

    // Set the language of Moment.js to Spanish
    moment.locale('es');

    // Get the titles of the columns
    var columnTitles = $("#tabla thead th").toArray().map(function (header) {
        return $(header).text().trim();
    });

    // Check if the 'Fecha' and 'Hora' columns exist
    var fechaIndex = columnTitles.indexOf('Fecha') !== -1 ? columnTitles.indexOf('Fecha') : columnTitles.indexOf('Fecha de nacimiento')
    var horaIndex = columnTitles.indexOf('Hora');

    // Initialize the DataTable with the specified options
    let tabla = $("#tabla").DataTable({
        "dom": 'lrtip',
        "lengthMenu": [[10, 25, -1], [10, 25, "All"]],
        "language": {
            "lengthMenu": "Mostrar _MENU_ registros por página",
            "zeroRecords": "No se encontraron registros",
            "info": "Mostrando la página _PAGE_ de _PAGES_",
            "infoEmpty": "No hay registros disponibles",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        },
        "columnDefs": [
            {
                "targets": horaIndex, // Apply the format to the 'Hora' column
                "render": function (data, type, row) {
                    if (type === 'display' && horaIndex !== -1) {
                        data = data.replace('noon', '12:00 PM');
                        return moment(data, 'h:mm a').format('HH:mm'); // 24-hour format
                    }
                    return data;
                }
            }
        ]
    });

    // Add an input to search in the table
    $("#inputBuscar").on("keyup", function() {
        tabla.search($(this).val()).draw();
    });
});

// Limit the number of characters in the inputs
$(document).ready(function() {
    $('input').attr('maxlength', '40');
});