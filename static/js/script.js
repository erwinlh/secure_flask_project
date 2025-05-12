// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    const showDivButtons = document.querySelectorAll('.show-div-btn');
    const contentAreas = document.querySelectorAll('.content-area');
    const welcomeDiv = document.getElementById('div_bienvenida'); // El div de bienvenida

    // Función para ocultar todos los divs de contenido
    function hideAllContentAreas() {
        contentAreas.forEach(div => {
            div.classList.add('d-none');
        });
    }

    // Mostrar el div de bienvenida al cargar la página si existe
    if (welcomeDiv) {
        hideAllContentAreas(); // Ocultar todos primero para asegurar
        welcomeDiv.classList.remove('d-none');
    }


    showDivButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Evitar la acción por defecto del enlace (navegar a #)

            const targetId = this.dataset.target; // Obtener el ID del div objetivo del atributo data-target
            const targetDiv = document.getElementById(targetId);

            if (targetDiv) {
                hideAllContentAreas(); // Ocultar todos los divs
                targetDiv.classList.remove('d-none'); // Mostrar el div objetivo
            }
        });
    });

    // Opcional: Ocultar mensajes flash después de un tiempo
    const flashes = document.querySelectorAll('.flashes li');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s ease-out';
            setTimeout(() => flash.remove(), 500); // Eliminar después de la transición
        }, 5000); // 5 segundos
    });
});