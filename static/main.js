function confirmarEliminarUsuario(event) {
    var confirmacion = confirm('¿Seguro que desea eliminar?');
     if (!confirmacion) {
    event.preventDefault();
    }
}

$(document).ready(function(){
    // Define el idioma de Moment.js a español
    moment.locale('es');

    // Obtiene los títulos de las columnas
    var columnTitles = $("#tabla thead th").toArray().map(function (header) {
        return $(header).text().trim();
    });

    // Verifica si las columnas 'Fecha' y 'Hora' existen
    var fechaIndex = columnTitles.indexOf('Fecha') !== -1 ? columnTitles.indexOf('Fecha') : columnTitles.indexOf('Fecha de nacimiento')
    var horaIndex = columnTitles.indexOf('Hora');

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
                "targets": horaIndex, // Aplica el formato a la columna 'Hora'
                "render": function (data, type, row) {
                    if (type === 'display' && horaIndex !== -1) {
                        data = data.replace('noon', '12:00 PM');
                        return moment(data, 'h:mm a').format('HH:mm'); // Formato de 24 horas
                    }
                    return data;
                }
            }
        ]
    });

    $("#inputBuscar").on("keyup", function() {
        tabla.search($(this).val()).draw();
    });
});

$(document).ready(function() {
    $('input').attr('maxlength', '40');
});