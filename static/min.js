function solicitarEstado(ticket, boton) {
    var url = '/solicitar_estado/' + ticket;

    fetch(url)
        .then(response => response.json())
        .then(result => {
            var estadoSpan = document.getElementById('estado-' + ticket);
            if (result.codRespuesta === '0') {
                estadoSpan.textContent = 'Guía OK!';
                estadoSpan.style.color = 'green';
            } else if (result.codRespuesta === '98') {
                estadoSpan.textContent = 'SUNAT procesando!';
                estadoSpan.style.color = 'orange';
            } else {
                estadoSpan.textContent = 'Error: Revise la creación del XML!';
                estadoSpan.style.color = 'red';
            }
        })
        .catch(error => console.log('Error: ', error));
}
