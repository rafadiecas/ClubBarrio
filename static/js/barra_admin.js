// Define a function to confirm user deletion
function confirmarEliminarUsuario(event) {
    // Show a confirmation dialog to the user
    var confirmacion = confirm('¿Seguro que desea eliminar?');
    // If the user does not confirm, prevent the default action (which is the deletion)
    if (!confirmacion) {
        event.preventDefault();
    }
}

// When the document is ready
$(document).ready(function () {
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
        "columnDefs": []
    });

    // When the user types in the search input
    $("#inputBuscar").on("keyup", function () {
        // Search the table for the input value and redraw the table
        tabla.search($(this).val()).draw();
    });
});
