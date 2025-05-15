
function showContent(contentId) {
    console.log("Showing:", contentId);
    var contentSections = document.querySelectorAll('.content-section');
    var selectionButtons = document.querySelectorAll('.selectionButton');

    contentSections.forEach(function (section) {
        section.style.display = 'none';
    });

    selectionButtons.forEach(function (button) {
        button.classList.remove('active');
    });

    var selectedContent = document.getElementById(contentId);
    if (selectedContent) {
        selectedContent.style.display = 'block';
    }

    var buttonNumber = contentId.replace('content', '');
    var activeButton = document.getElementById('button' + buttonNumber);
    if (activeButton) {
        activeButton.classList.add('active');
    }

}

// --- Notification Logic (Keep as is) ---
function showNotification(title, message, type = 'success') {
    const notificationDiv = document.getElementById('notification');
    const notificationTitle = document.getElementById('notification-title');
    const notificationMessage = document.getElementById('notification-message');

    if (!notificationDiv || !notificationTitle || !notificationMessage) {
        console.error("Notification elements not found!");
        return;
    }

    notificationTitle.textContent = title;
    notificationMessage.textContent = message;

    notificationDiv.className = `notification ${type}`; // Reset classes then add type
    notificationDiv.classList.add('show');

    setTimeout(() => {
        notificationDiv.classList.remove('show');
    }, 5000); // Increased duration slightly
}
// --- Progress Appending Logic (CORREGIDA) ---
function appendProgress(message, isError = false, isSuccess = false, site) {
    let progressContainer; // Declarar la variable aquí, fuera de los bloques if/else

    if (site === "oracle") { // Usar === para comparación estricta
        progressContainer = document.getElementById('progress-container');
    } else if (site === "gde") { // Usar ===
        progressContainer = document.getElementById('progress-containergde');
    } else {
        // Si 'site' no es ni 'oracle' ni 'gde', o no se proporciona
        console.error("Sitio no válido o no especificado para appendProgress:", site);
        // Podrías asignar a un contenedor por defecto o simplemente retornar para evitar más errores
        // progressContainer = document.getElementById('progress-container'); // Ejemplo: contenedor por defecto
        return; // Es más seguro retornar si el sitio no es válido.
    }

    if (!progressContainer) {
        console.error(`Progress container for site '${site}' (ID: 'progress-container${site === 'gde' ? 'gde' : ''}') not found!`);
        return;
    }

    const line = document.createElement('div');
    line.textContent = message;

    // Aplicar estilos y clases
    if (isError || message.toLowerCase().includes("error")) { // Simplificado el chequeo de error
        line.style.color = 'red';
        line.classList.add('error-message');
    } else if (isSuccess || message.toLowerCase().includes("completado") || message.toLowerCase().includes("finalizado") || message.toLowerCase().includes("actualizado")) { // Añadido "actualizado"
        line.style.color = 'green';
        line.classList.add('success-message');
    } else if (message.toLowerCase().includes("advertencia") || message.toLowerCase().includes("saltando")) {
        line.style.color = 'orange'; // Para advertencias
    } else if (message.startsWith("---")) { // Para los separadores
        line.style.fontWeight = 'bold';
        line.style.marginTop = '5px';
        line.style.color = '#555';
    }
    else {
        line.style.color = 'inherit'; // o 'black'
    }

    progressContainer.appendChild(line);
    progressContainer.scrollTop = progressContainer.scrollHeight; // Auto-scroll
}
document.addEventListener('DOMContentLoaded', () => {
    // Show initial content
    showContent('content1');

    // Get form elements
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file1Input');
    const progressContainer = document.getElementById('progress-container'); // Text area
    const submitButton = form ? form.querySelector('button[type="submit"]') : null;
    // *** NEW: Get progress bar elements ***
    const progressBarContainer = document.getElementById('upload-progress-bar-container');
    const progressBar = document.getElementById('upload-progress-bar');

    // Check if all required elements exist
    if (form && fileInput && progressContainer && submitButton && progressBarContainer && progressBar) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent default form submission

            if (fileInput.files.length === 0) {
                showNotification('Error', 'Por favor, selecciona un archivo.', 'error');
                return;
            }
            // Optional: Check file type
            const fileName = fileInput.files[0].name;
            if (!fileName.toLowerCase().endsWith('.xlsx')) {
                 showNotification('Error', 'Por favor, selecciona un archivo .xlsx.', 'error');
                 return;
            }


            // --- UI Updates: Start Processing ---
            submitButton.disabled = true;
            submitButton.textContent = 'Procesando...';
            progressContainer.innerHTML = 'Iniciando procesamiento...<br>'; // Clear text area
            // Show and reset progress bar
            progressBarContainer.style.display = 'flex'; // Use flex as it's in a d-flex container
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
            progressBar.setAttribute('aria-valuenow', '0');
            progressBar.classList.add('progress-bar-animated'); // Ensure animation is active
            progressBar.classList.remove('bg-success', 'bg-danger'); // Remove completion/error colors

            const formData = new FormData();
            formData.append('file1', fileInput.files[0]);

            try {
                const response = await fetch('/procesar_archivo', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    // ... (error handling as before) ...
                    appendProgress(errorMsg, true,"", "oracle");
                    showNotification('Error', errorMsg, 'error');
                    // Style progress bar on error
                    progressBar.classList.add('bg-danger');
                    progressBar.classList.remove('progress-bar-animated');
                    progressBar.textContent = 'Error';
                    return;
                }

                if (!response.body) {
                    // ... (error handling as before) ...
                    appendProgress("Error: La respuesta del servidor no tiene cuerpo...", true,"", "oracle");
                    showNotification('Error', "Respuesta inválida del servidor.", 'error');
                     // Style progress bar on error
                    progressBar.classList.add('bg-danger');
                    progressBar.classList.remove('progress-bar-animated');
                    progressBar.textContent = 'Error';
                    return;
                }

                // --- Stream Reading Logic ---
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) {
                        console.log("Stream finalizado por el servidor.");
                        // Process remaining buffer
                        if (buffer.trim()) {
                             const lines = buffer.split('\n\n');
                             lines.forEach(line => {
                                if (line.startsWith('data:')) {
                                    const message = line.substring(5).trim();
                                    if (message) {
                                        appendProgress(message,false,"", "oracle"); // Append final text messages
                                        // Potentially update progress bar based on final message
                                        if (message.toLowerCase().includes("completado") || message.toLowerCase().includes("finalizado")) {
                                            progressBar.style.width = '100%';
                                            progressBar.textContent = '100%';
                                            progressBar.setAttribute('aria-valuenow', '100');
                                            progressBar.classList.remove('progress-bar-animated');
                                            progressBar.classList.add('bg-success'); // Green on success
                                            showNotification('Éxito', 'Archivo procesado correctamente.', 'success');
                                        } else if (message.toLowerCase().includes("error")) {
                                            progressBar.classList.add('bg-danger');
                                            progressBar.classList.remove('progress-bar-animated');
                                            progressBar.textContent = 'Error';
                                        }
                                    }
                                }
                             });
                        }
                        // Check if success notification was already shown by final message
                        const lastMessage = progressContainer.lastChild ? progressContainer.lastChild.textContent : '';
                        if (!lastMessage.toLowerCase().includes("completado") && !lastMessage.toLowerCase().includes("finalizado") && !lastMessage.toLowerCase().includes("error")) {
                            // If stream ends without explicit success/error message, maybe show info
                            // showNotification('Info', 'Proceso terminado.', 'info');
                            // Decide final state of progress bar if needed
                        }
                        break;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    let boundary = buffer.indexOf('\n\n');

                    while (boundary !== -1) {
                        const messagePart = buffer.substring(0, boundary + 2);
                        buffer = buffer.substring(boundary + 2);

                        if (messagePart.startsWith('data:')) {
                            const message = messagePart.substring(5, messagePart.length - 2).trim();
                            if (message) {
                                appendProgress(message,false,"", "oracle"); // Append text message to the text area

                                // --- Update Progress Bar based on message content ---
                                const progressMatch = message.match(/Procesando fila (\d+)\/(\d+)/);
                                if (progressMatch) {
                                    const current = parseInt(progressMatch[1], 10);
                                    const total = parseInt(progressMatch[2], 10);
                                    if (total > 0) {
                                        const percentage = Math.min(100, Math.round((current / total) * 100));
                                        progressBar.style.width = percentage + '%';
                                        progressBar.textContent = percentage + '%';
                                        progressBar.setAttribute('aria-valuenow', percentage);
                                    }
                                } else if (message.toLowerCase().includes("completado") || message.toLowerCase().includes("finalizado")) {
                                    // Final success step
                                    progressBar.style.width = '100%';
                                    progressBar.textContent = '100%';
                                    progressBar.setAttribute('aria-valuenow', '100');
                                    progressBar.classList.remove('progress-bar-animated');
                                    progressBar.classList.add('bg-success'); // Optional: Green color on success
                                    // Notification is handled after loop finishes or by final message check
                                } else if (message.toLowerCase().includes("error")) {
                                     progressBar.classList.add('bg-danger');
                                     progressBar.classList.remove('progress-bar-animated');
                                     progressBar.textContent = 'Error';
                                }
                                // --- End Progress Bar Update ---
                            }
                        } else if (messagePart.startsWith('event: end')) {
                            console.log("Evento 'end' recibido.");
                        }
                        boundary = buffer.indexOf('\n\n');
                    }
                } // End while loop
                                showNotification('Éxito', 'Proceso de envío a Defontana completado.', 'success');


            } catch (error) {
                console.error('Error durante el fetch o la lectura del stream:', error);
                const errorText = `Error de conexión o procesamiento: ${error.message}`;
                appendProgress(errorText, true,"", "oracle");
                showNotification('Error', errorText, 'error');
                 // Style progress bar on error
                progressBar.classList.add('bg-danger');
                progressBar.classList.remove('progress-bar-animated');
                progressBar.textContent = 'Error';

            } finally {
                // --- UI Updates: Finish Processing ---
                submitButton.disabled = false;
                submitButton.textContent = 'Procesar';
                fileInput.value = ''; // Clear file input
                console.log("adas")
                showNotification('Éxito', 'Proceso de envío a Defontana completado.', 'success');


                // Hide progress bar after a short delay to show final state (e.g., 100% or Error)
                setTimeout(() => {
                    progressBarContainer.style.display = 'none';
                    // Reset bar for next time
                    progressBar.style.width = '0%';
                    progressBar.textContent = '0%';
                    progressBar.setAttribute('aria-valuenow', '0');
                    progressBar.classList.remove('progress-bar-animated', 'bg-success', 'bg-danger');
                }, 3000); // Hide after 3 seconds
            }
        });
    } else {
        console.error("Faltan elementos del DOM necesarios para la carga y progreso:",
            { form, fileInput, progressContainer, submitButton, progressBarContainer, progressBar });
    }

    // Section 5
    // Get formgde elements
    const formgde = document.getElementById('upload-formgde');
    const fileInputgde = document.getElementById('file-gde');
    const progressContainergde = document.getElementById('progress-containergde'); // Text area
    const submitButtongde = formgde ? formgde.querySelector('button[type="submit"]') : null;
    // *** NEW: Get progress bar elements ***
    const progressBarContainergde = document.getElementById('upload-progress-bar-containergde');
    const progressBargde = document.getElementById('upload-progress-bargde');

    // Check if all required elements exist
    if (formgde && fileInputgde && progressContainergde && submitButtongde && progressBarContainergde && progressBargde) {
        formgde.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent default formgde submission

            if (fileInputgde.files.length === 0) {
                showNotification('Error', 'Por favor, selecciona un archivo.', 'error');
                return;
            }
            // Optional: Check file type
            const fileName = fileInputgde.files[0].name;
            if (!fileName.toLowerCase().endsWith('.xls')) {
                 showNotification('Error', 'Por favor, selecciona un archivo .xlsx.', 'error');
                 return;
            }


            // --- UI Updates: Start Processing ---
            submitButtongde.disabled = true;
            submitButtongde.textContent = 'Procesando...';
            progressContainergde.innerHTML = 'Iniciando procesamiento...<br>'; // Clear text area
            // Show and reset progress bar
            progressBarContainergde.style.display = 'flex'; // Use flex as it's in a d-flex container
            progressBargde.style.width = '0%';
            progressBargde.textContent = '0%';
            progressBargde.setAttribute('aria-valuenow', '0');
            progressBargde.classList.add('progress-bar-animated'); // Ensure animation is active
            progressBargde.classList.remove('bg-success', 'bg-danger'); // Remove completion/error colors

            const formData = new FormData();
            formData.append('file-gde', fileInputgde.files[0]);

            try {
                const response = await fetch('/procesar_archivo_GDE', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    // ... (error handling as before) ...
                    appendProgress(errorMsg, true,"", "gde");
                    showNotification('Error', errorMsg, 'error');
                    // Style progress bar on error
                    progressBargde.classList.add('bg-danger');
                    progressBargde.classList.remove('progress-bar-animated');
                    progressBargde.textContent = 'Error';
                    return;
                }

                if (!response.body) {
                    // ... (error handling as before) ...
                    appendProgress("Error: La respuesta del servidor no tiene cuerpo...", true,"", "gde");
                    showNotification('Error', "Respuesta inválida del servidor.", 'error');
                     // Style progress bar on error
                    progressBargde.classList.add('bg-danger');
                    progressBargde.classList.remove('progress-bar-animated');
                    progressBargde.textContent = 'Error';
                    return;
                }

                // --- Stream Reading Logic ---
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) {
                        console.log("Stream finalizado por el servidor.");
                        // Process remaining buffer
                        if (buffer.trim()) {
                             const lines = buffer.split('\n\n');
                             lines.forEach(line => {
                                if (line.startsWith('data:')) {
                                    const message = line.substring(5).trim();
                                    if (message) {
                                        appendProgress(message,false,"", "gde"); // Append final text messages
                                        // Potentially update progress bar based on final message
                                        if (message.toLowerCase().includes("completado") || message.toLowerCase().includes("finalizado")) {
                                            progressBargde.style.width = '100%';
                                            progressBargde.textContent = '100%';
                                            progressBargde.setAttribute('aria-valuenow', '100');
                                            progressBargde.classList.remove('progress-bar-animated');
                                            progressBargde.classList.add('bg-success'); // Green on success
                                            showNotification('Éxito', 'Archivo procesado correctamente.', 'success');
                                        } else if (message.toLowerCase().includes("error")) {
                                            progressBargde.classList.add('bg-danger');
                                            progressBargde.classList.remove('progress-bar-animated');
                                            progressBargde.textContent = 'Error';
                                        }
                                    }
                                }
                             });
                        }
                        // Check if success notification was already shown by final message
                        const lastMessage = progressContainergde.lastChild ? progressContainergde.lastChild.textContent : '';
                        if (!lastMessage.toLowerCase().includes("completado") && !lastMessage.toLowerCase().includes("finalizado") && !lastMessage.toLowerCase().includes("error")) {
                            // If stream ends without explicit success/error message, maybe show info
                            // showNotification('Info', 'Proceso terminado.', 'info');
                            // Decide final state of progress bar if needed
                        }
                        break;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    let boundary = buffer.indexOf('\n\n');

                    while (boundary !== -1) {
                        const messagePart = buffer.substring(0, boundary + 2);
                        buffer = buffer.substring(boundary + 2);

                        if (messagePart.startsWith('data:')) {
                            const message = messagePart.substring(5, messagePart.length - 2).trim();
                            if (message) {
                                appendProgress(message,false,"", "gde"); // Append text message to the text area

                                // --- Update Progress Bar based on message content ---
                                const progressMatch = message.match(/Procesando fila (\d+)\/(\d+)/);
                                if (progressMatch) {
                                    const current = parseInt(progressMatch[1], 10);
                                    const total = parseInt(progressMatch[2], 10);
                                    if (total > 0) {
                                        const percentage = Math.min(100, Math.round((current / total) * 100));
                                        progressBargde.style.width = percentage + '%';
                                        progressBargde.textContent = percentage + '%';
                                        progressBargde.setAttribute('aria-valuenow', percentage);
                                    }
                                } else if (message.toLowerCase().includes("completado") || message.toLowerCase().includes("finalizado")) {
                                    // Final success step
                                    progressBargde.style.width = '100%';
                                    progressBargde.textContent = '100%';
                                    progressBargde.setAttribute('aria-valuenow', '100');
                                    progressBargde.classList.remove('progress-bar-animated');
                                    progressBargde.classList.add('bg-success'); // Optional: Green color on success
                                    // Notification is handled after loop finishes or by final message check
                                } else if (message.toLowerCase().includes("error")) {
                                     progressBargde.classList.add('bg-danger');
                                     progressBargde.classList.remove('progress-bar-animated');
                                     progressBargde.textContent = 'Error';
                                }
                                // --- End Progress Bar Update ---
                            }
                        } else if (messagePart.startsWith('event: end')) {
                            console.log("Evento 'end' recibido.");
                        }
                        boundary = buffer.indexOf('\n\n');
                    }
                } // End while loop

            } catch (error) {
                console.error('Error durante el fetch o la lectura del stream:', error);
                const errorText = `Error de conexión o procesamiento: ${error.message}`;
                appendProgress(errorText, true,"", "gde");
                showNotification('Error', errorText, 'error');
                 // Style progress bar on error
                progressBargde.classList.add('bg-danger');
                progressBargde.classList.remove('progress-bar-animated');
                progressBargde.textContent = 'Error';

            } finally {
                // --- UI Updates: Finish Processing ---
                submitButtongde.disabled = false;
                submitButtongde.textContent = 'Procesar';
                fileInputgde.value = ''; // Clear file input

                // Hide progress bar after a short delay to show final state (e.g., 100% or Error)
                setTimeout(() => {
                    progressBarContainergde.style.display = 'none';
                    // Reset bar for next time
                    progressBargde.style.width = '0%';
                    progressBargde.textContent = '0%';
                    progressBargde.setAttribute('aria-valuenow', '0');
                    progressBargde.classList.remove('progress-bar-animated', 'bg-success', 'bg-danger');
                }, 3000); // Hide after 3 seconds
            }
        });
    } else {
        console.error("Faltan elementos del DOM necesarios para la carga y progreso:",
            { formgde, fileInputgde, progressContainergde, submitButtongde, progressBarContainergde, progressBargde });
    }


    // --- Export Form Logic (Section 2 - NEW) ---
    const exportForm = document.getElementById('export-form'); // El form de la sección 2
    const fechaDesdeInput = document.getElementById('fechaDesde');
    const fechaHastaInput = document.getElementById('fechaHasta');
    const buscarExportarBtn = document.getElementById('buscarExportarBtn');
    const resultadosExportarDiv = document.getElementById('resultadosExportar'); // Opcional: para mostrar mensajes

    if (exportForm && fechaDesdeInput && fechaHastaInput && buscarExportarBtn) {

        buscarExportarBtn.addEventListener('click', async () => {
            console.log("asd")
            const fechaDesde = fechaDesdeInput.value;
            const fechaHasta = fechaHastaInput.value;
            
            // Validación simple
            if (!fechaDesde || !fechaHasta) {
                showNotification('Error', 'Por favor, selecciona ambas fechas.', 'error');
                return;
            }

            if (new Date(fechaDesde) > new Date(fechaHasta)) {
                showNotification('Error', 'La fecha "Desde" no puede ser posterior a la fecha "Hasta".', 'error');
                return;
            }

            // Mostrar feedback visual (opcional)
            buscarExportarBtn.disabled = true;
            buscarExportarBtn.textContent = 'Generando...';
            if (resultadosExportarDiv) {
                resultadosExportarDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Generando...</span></div> Generando exportación...';
            }

            // Crear FormData para enviar las fechas
            const formData = new FormData();
            formData.append('fechaDesde', fechaDesde);
            formData.append('fechaHasta', fechaHasta);

            try {
                const response = await fetch('/exportar_archivo', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    let filename = 'exportacion.xls'; // Nombre por defecto
                    const disposition = response.headers.get('content-disposition');
                    if (disposition && disposition.indexOf('attachment') !== -1) {
                        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                        const matches = filenameRegex.exec(disposition);
                        if (matches != null && matches[1]) {
                          filename = matches[1].replace(/['"]/g, '');
                        }
                    }

                    showNotification('Éxito', `La descarga de "${filename}" debería comenzar en breve.`, 'success');
                    if (resultadosExportarDiv) {
                         resultadosExportarDiv.innerHTML = `Archivo <strong>${filename}</strong> generado. La descarga debería iniciarse.`;
                    }

                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = filename; // Usa el nombre obtenido o uno por defecto
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    a.remove();

                } else {
                    // Si hay un error, intentar leer el mensaje JSON del servidor
                    let errorMsg = `Error ${response.status}: ${response.statusText}`;
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.message || errorMsg;
                    } catch (e) {
                        // El cuerpo de la respuesta no era JSON o hubo otro error
                        console.error("No se pudo parsear el error JSON:", e);
                    }
                    showNotification('Error', errorMsg, 'error');
                     if (resultadosExportarDiv) {
                         resultadosExportarDiv.innerHTML = `<span style="color: red;">Error: ${errorMsg}</span>`;
                     }
                }

            } catch (error) {
                console.error('Error en la petición fetch para exportar:', error);
                showNotification('Error', `Error de red o conexión al intentar exportar: ${error.message}`, 'error');
                 if (resultadosExportarDiv) {
                     resultadosExportarDiv.innerHTML = `<span style="color: red;">Error de conexión.</span>`;
                 }
            } finally {
                // Restaurar botón
                buscarExportarBtn.disabled = false;
                buscarExportarBtn.textContent = 'Buscar';
            }
        });

    } else {
         console.error("Faltan elementos del DOM necesarios para la exportación (Sección 2).");
    }

   // send api logic section 3
   const enviarfechaDesdeInput = document.getElementById('fechaDesdeEnviar');
   const enviarfechaHastaInput = document.getElementById('fechaHastaEnviar');
   const tipoDteInput = document.getElementById('tipoDteInput'); // Asegúrate que este ID existe en tu HTML

   const enviarBtn = document.getElementById('enviarBtn');
   const resultadosEnviarDiv = document.getElementById('resultadosEnviar'); // Div para estado inicial/final
   // *** NUEVO: Referencia al contenedor de progreso para la sección 3 ***
   const progressContainerEnviar = document.getElementById('progress-container-enviar'); // Necesitas añadir este div en tu HTML

   // Helper function para añadir progreso al contenedor específico de la sección 3
   function appendProgressEnviar(message, isError = false) {
       if (!progressContainerEnviar) return;
       const line = document.createElement('div');
       line.textContent = message;
       // Reutiliza la lógica de estilo (puedes refinarla más si quieres)
       if (isError || message.toLowerCase().includes("error")) {
           line.style.color = 'red';
       } else if (message.toLowerCase().includes("exitosamente") || message.toLowerCase().includes("completado") || message.toLowerCase().includes("finalizado") || message.toLowerCase().includes("actualizado")) {
           line.style.color = 'green';
       } else if (message.toLowerCase().includes("advertencia") || message.toLowerCase().includes("saltando")) {
            line.style.color = 'orange';
       } else if (message.startsWith("---")) { // Para los separadores
            line.style.fontWeight = 'bold';
            line.style.marginTop = '5px';
            line.style.color = '#555';
       }
       else {
           line.style.color = 'inherit'; // o 'black'
       }
       progressContainerEnviar.appendChild(line);
       progressContainerEnviar.scrollTop = progressContainerEnviar.scrollHeight; // Auto-scroll
   }

    // Helper function para procesar el buffer restante (similar a la de /procesar_archivo)
    function processBufferEnviar(bufferContent) {
        const lines = bufferContent.split('\n\n');
        lines.forEach(line => {
           if (line.startsWith('data:')) {
               const message = line.substring(5).trim();
               if (message) {
                   appendProgressEnviar(message);
               }
           }
        });
    }


   // Verifica que todos los elementos necesarios existan
   if (enviarfechaDesdeInput && enviarfechaHastaInput && tipoDteInput && enviarBtn && resultadosEnviarDiv && progressContainerEnviar) {

       enviarBtn.addEventListener('click', async () => {
           const fechaDesde = enviarfechaDesdeInput.value;
           const fechaHasta = enviarfechaHastaInput.value;
           const tipoDte = tipoDteInput.value; // Obtener valor del tipo DTE

           // --- Validación ---
           if (!fechaDesde || !fechaHasta || !tipoDte) { // Validar también tipoDte
               showNotification('Error', 'Por favor, selecciona ambas fechas y el Tipo DTE.', 'error');
               return;
           }
           // Opcional: Validar que tipoDte sea un número si es necesario
           if (isNaN(tipoDte)) {
                showNotification('Error', 'El Tipo DTE debe ser un número.', 'error');
                return;
           }

           if (new Date(fechaDesde) > new Date(fechaHasta)) {
               showNotification('Error', 'La fecha "Desde" no puede ser posterior a la fecha "Hasta".', 'error');
               return;
           }

           // --- UI Update: Start ---
           enviarBtn.disabled = true;
           enviarBtn.textContent = 'Enviando...';
           // Limpiar contenedor de progreso y mostrar estado inicial
           progressContainerEnviar.innerHTML = 'Iniciando proceso de envío a Defontana...';
           if (resultadosEnviarDiv) {
               resultadosEnviarDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Enviando...</span></div> Procesando...';
               resultadosEnviarDiv.style.color = 'inherit';
           }

           // --- Prepare Data ---
           const formData = new FormData();
           formData.append('fechaDesde', fechaDesde);
           formData.append('fechaHasta', fechaHasta);
           formData.append('tipoDte', tipoDte); // Enviar tipoDte

           // --- Fetch Request con Stream Handling ---
           try {
               const response = await fetch('/subir_defontana', {
                   method: 'POST',
                   body: formData
               });

               // --- INICIO: Lógica de Stream para /subir_defontana ---
               if (!response.ok) {
                   // Intenta obtener un mensaje de error si el servidor lo envió (ej. error 400 inicial)
                   let errorMsg = `Error ${response.status}: ${response.statusText}`;
                    try {
                        const errorText = await response.text();
                        // Intenta parsear como JSON, si no, usa el texto
                        try {
                            const errorData = JSON.parse(errorText);
                            errorMsg = errorData.message || errorData.error || errorMsg;
                        } catch(jsonError) {
                            // Si el error viene como texto plano desde el stream de error inicial
                            if (errorText.startsWith('data:')) {
                                errorMsg = errorText.substring(5).trim();
                            } else if (errorText) {
                                errorMsg = errorText;
                            }
                        }
                    } catch(readError) {
                        // No se pudo leer el cuerpo del error
                    }
                   showNotification('Error', `Error inicial: ${errorMsg}`, 'error');
                   if (resultadosEnviarDiv) resultadosEnviarDiv.innerHTML = `<span style="color: red;">Error: ${errorMsg}</span>`;
                   appendProgressEnviar(`Error inicial: ${errorMsg}`, true); // Añadir al log de progreso
                   return; // Salir temprano
               }

               if (!response.body) {
                   const errorMsg = "Error: La respuesta del servidor no tiene cuerpo (stream).";
                   showNotification('Error', errorMsg, 'error');
                    if (resultadosEnviarDiv) resultadosEnviarDiv.innerHTML = `<span style="color: red;">${errorMsg}</span>`;
                    appendProgressEnviar(errorMsg, true);
                   return;
               }

               // --- Lectura del Stream ---
               const reader = response.body.getReader();
               const decoder = new TextDecoder();
               let buffer = '';
               let finalMessage = ''; // Para guardar el último mensaje o resumen

               while (true) {
                   const { value, done } = await reader.read();
                   if (done) {
                       console.log("Stream de /subir_defontana finalizado.");
                       // Procesar buffer restante si lo hay
                       if (buffer.trim()) {
                            processBufferEnviar(buffer); // Usa la función helper para procesar
                       }

                       // --- UI Update: Stream End ---
                       // Determinar estado final basado en el último mensaje significativo
                       let hasErrors = finalMessage.toLowerCase().includes("error") || progressContainerEnviar.innerHTML.toLowerCase().includes("error");
                       let hasSuccess = finalMessage.toLowerCase().includes("finalizado") || finalMessage.toLowerCase().includes("completado");

                       if (hasErrors) {
                            showNotification('Error', 'El proceso finalizó con errores.', 'error');
                            if (resultadosEnviarDiv) resultadosEnviarDiv.innerHTML = `<span style="color: red;">Proceso finalizado con errores. Ver detalles.</span>`;
                       } else if (hasSuccess) {
                            showNotification('Éxito', 'Proceso de envío a Defontana completado.', 'success');
                            if (resultadosEnviarDiv) resultadosEnviarDiv.innerHTML = `<span style="color: green;">Proceso completado exitosamente.</span>`;
                       } else {
                            // Si no hay mensaje claro de éxito o error, pero terminó.
                            showNotification('Info', 'Proceso terminado.', 'info');
                            if (resultadosEnviarDiv) resultadosEnviarDiv.innerHTML = `<span>Proceso terminado.</span>`;
                       }
                       break; // Salir del bucle while
                   }

                   // Decodificar y procesar chunk
                   buffer += decoder.decode(value, { stream: true });
                   let boundary = buffer.indexOf('\n\n');

                   while (boundary !== -1) {
                       const messagePart = buffer.substring(0, boundary + 2);
                       buffer = buffer.substring(boundary + 2);

                       if (messagePart.startsWith('data:')) {
                           const message = messagePart.substring(5, messagePart.length - 2).trim();
                           if (message) {
                               appendProgressEnviar(message); // Usa la función helper para mostrar
                               finalMessage = message; // Actualiza el último mensaje recibido
                           }
                       } else if (messagePart.startsWith('event: end')) {
                           console.log("Evento 'end' recibido de /subir_defontana.");
                           // El bucle terminará en la siguiente iteración porque done será true
                       }
                       // Ignorar otros tipos de eventos o líneas vacías
                       boundary = buffer.indexOf('\n\n');
                   }
               } // Fin while(true)

           } catch (error) {
               // --- Handle Network/Fetch Errors ---
               console.error('Error en la petición fetch para /subir_defontana:', error);
               const networkErrorMsg = `Error de red o conexión: ${error.message}`;
               showNotification('Error', networkErrorMsg, 'error');
               if (resultadosEnviarDiv) {
                   resultadosEnviarDiv.innerHTML = `<span style="color: red;">${networkErrorMsg}</span>`;
               }
                appendProgressEnviar(networkErrorMsg, true); // Añadir al log de progreso

           } finally {
               // --- UI Update: Always Run ---
               enviarBtn.disabled = false; // Re-enable the button
               enviarBtn.textContent = 'Enviar'; // Reset button text
               // Opcional: Limpiar el spinner si aún está visible después de un tiempo
                setTimeout(() => {
                   if (resultadosEnviarDiv && resultadosEnviarDiv.innerHTML.includes('spinner-border')) {
                       if (!progressContainerEnviar.innerHTML.toLowerCase().includes("error")) {
                            resultadosEnviarDiv.innerHTML = 'Listo.';
                       } else {
                            resultadosEnviarDiv.innerHTML = '<span style="color: red;">Finalizado con errores.</span>';
                       }
                   }
                }, 5000); // Limpia después de 5 segundos si no se actualizó antes
           }
       }); // Fin addEventListener

   } else {
       // Log si faltan elementos principales para esta sección
       console.error("Faltan elementos del DOM necesarios para la sección de envío a Defontana (Sección 3):",
           { enviarfechaDesdeInput, enviarfechaHastaInput, tipoDteInput, enviarBtn, resultadosEnviarDiv, progressContainerEnviar });
        // Opcional: Mostrar un mensaje al usuario en la propia sección
        if(document.getElementById('content3')) {
            document.getElementById('content3').innerHTML = '<p style="color: red;">Error: No se pudieron cargar los controles para esta sección.</p>';
        }
   }
});