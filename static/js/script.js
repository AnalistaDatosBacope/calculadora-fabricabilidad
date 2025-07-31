document.addEventListener('DOMContentLoaded', function() {
    console.log('=== SCRIPT.JS CARGADO ===');
    console.log('Script.js cargado correctamente');
    console.log('Document ready state:', document.readyState);
    console.log('Timestamp:', new Date().toISOString());
    
    // Debug: Verificar que todos los elementos existen
    const sections = ['dashboard', 'carga', 'fabricabilidad', 'demanda', 'equilibrado', 'costo_total', 'costos', 'analisis'];
    const elementos = {};
    
    sections.forEach(section => {
        const sectionElement = document.getElementById('section-' + section);
        const tabElement = document.getElementById('tab-' + section);
        elementos[section] = {
            section: !!sectionElement,
            tab: !!tabElement
        };
    });
    
    console.log('Elementos encontrados:', elementos);
    
    // Verificar elementos específicos de costos históricos
    const costosElements = {
        select: !!document.getElementById('articulo_costos_select'),
        visualizacion: !!document.getElementById('costos-historicos-visualizacion'),
        tbody: !!document.getElementById('costos-historicos-tbody'),
        chart: !!document.getElementById('costosHistoricosChart'),
        alert: !!document.getElementById('costos-historicos-alert')
    };
    console.log('Elementos de costos históricos:', costosElements);
    
    // Obtener elementos del DOM
    const modelNameSelect = document.getElementById('model_name_select');
    const desiredQtyInput = document.getElementById('desired_qty');
    const calculateIndividualBtn = document.getElementById('calculate_individual_btn');
    const individualCalcCard = document.getElementById('individual-calc-card');

    const lotCalcCard = document.getElementById('lot-calc-card');
    const calculateLotBtn = document.getElementById('calculate_lot_btn');

    const modelDemandCard = document.getElementById('model-demand-card');
    const calculateModelDemandBtn = document.getElementById('calculate_model_demand_btn');
    const modelsSelectDemand = document.getElementById('models_select_demand');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    const equalizationCalcCard = document.getElementById('equalization-calc-card'); // Nuevo
    const calculateEqualizationBtn = document.getElementById('calculate_equalization_btn'); // Nuevo
    const modelsSelectEqualization = document.getElementById('models_select_equalization'); // Nuevo
    const startDateEqualizationInput = document.getElementById('start_date_equalization'); // Nuevo
    const endDateEqualizationInput = document.getElementById('end_date_equalization');     // Nuevo

    // Nuevos elementos para el cálculo de costo total de modelo
    const modelFullCostCard = document.getElementById('model-full_cost-card');
    const modelNameFullCostSelect = document.getElementById('model_name_full_cost_select');
    const quantityFullCostInput = document.getElementById('quantity_full_cost');
    const calculateFullCostBtn = document.getElementById('calculate_full_cost_btn');

    // Elementos para los mensajes de estado de carga de archivos
    const bomStatus = document.getElementById('bom_status');
    const stockStatus = document.getElementById('stock_status');
    const lotStatus = document.getElementById('lot_status');
    const costStatus = document.getElementById('cost_status');
    const salesStatus = document.getElementById('sales_status');
    const suppliersStatus = document.getElementById('suppliers_status');

    // DEBUG: Verificar que los elementos se encontraron
    console.log('Elementos encontrados:', {
        modelFullCostCard: !!modelFullCostCard,
        modelNameFullCostSelect: !!modelNameFullCostSelect,
        quantityFullCostInput: !!quantityFullCostInput,
        calculateFullCostBtn: !!calculateFullCostBtn
    });

    // Banderas de estado de carga de archivos
    let bomLoaded = bomStatus ? bomStatus.value === 'True' : false;
    let stockLoaded = stockStatus ? stockStatus.value === 'True' : false;
    let lotLoaded = lotStatus ? lotStatus.value === 'True' : false;
    let costLoaded = costStatus ? costStatus.value === 'True' : false;
    let salesLoaded = salesStatus ? salesStatus.value === 'True' : false;
    let suppliersLoaded = suppliersStatus ? suppliersStatus.value === 'True' : false;


    // Inicializar Select2 en los selectores de modelos
    if (modelNameSelect) {
    $(modelNameSelect).select2({
        theme: "bootstrap-5",
            width: '100%',
            placeholder: "Seleccione un modelo para fabricabilidad individual",
        allowClear: true,
            dropdownParent: $('#individual-calc-card'),
            language: {
                noResults: function() {
                    return "No se encontraron modelos";
                },
                searching: function() {
                    return "Buscando...";
                }
            }
        });
    }

    if (modelsSelectDemand) {
    $(modelsSelectDemand).select2({
        theme: "bootstrap-5",
            width: '100%',
            placeholder: "Seleccione modelos para proyección de demanda",
        allowClear: true,
            multiple: true,
            dropdownParent: $('#model-demand-card'),
            language: {
                noResults: function() {
                    return "No se encontraron modelos";
                },
                searching: function() {
                    return "Buscando...";
                }
            }
        });
    }

    if (modelsSelectEqualization) {
    $(modelsSelectEqualization).select2({
        theme: "bootstrap-5",
            width: '100%',
            placeholder: "Seleccione modelos para equilibrado de stock",
        allowClear: true,
            multiple: true,
            dropdownParent: $('#equalization-calc-card'),
            language: {
                noResults: function() {
                    return "No se encontraron modelos";
                },
                searching: function() {
                    return "Buscando...";
                }
            }
        });
    }

    if (modelNameFullCostSelect) {
    $(modelNameFullCostSelect).select2({
        theme: "bootstrap-5",
            width: '100%',
            placeholder: "Seleccione un modelo para cálculo de costo total",
        allowClear: true,
            dropdownParent: $('#model-full-cost-card'),
            language: {
                noResults: function() {
                    return "No se encontraron modelos";
                },
                searching: function() {
                    return "Buscando...";
                }
            }
        });
    }

    // Inicializar flatpickr para los campos de fecha
    if (startDateInput) {
        flatpickr(startDateInput, { 
            dateFormat: "Y-m-d",
            allowInput: true,
            clickOpens: true,
            placeholder: "Seleccionar fecha de inicio"
        });
    }
    if (endDateInput) {
        flatpickr(endDateInput, { 
            dateFormat: "Y-m-d",
            allowInput: true,
            clickOpens: true,
            placeholder: "Seleccionar fecha de fin"
        });
    }
    if (startDateEqualizationInput) {
        flatpickr(startDateEqualizationInput, { 
            dateFormat: "Y-m-d",
            allowInput: true,
            clickOpens: true,
            placeholder: "Seleccionar fecha de inicio"
        });
    }
    if (endDateEqualizationInput) {
        flatpickr(endDateEqualizationInput, { 
            dateFormat: "Y-m-d",
            allowInput: true,
            clickOpens: true,
            placeholder: "Seleccionar fecha de fin"
        });
    }

    // Función para actualizar el estado de los inputs de archivo
    function updateFileInputStatus() {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', function() {
                const fileName = this.files[0] ? this.files[0].name : 'Seleccionar archivo';
                const label = this.nextElementSibling;
                if (label) {
                    label.innerText = fileName;
                }
            });
        });
    }

    // Función para poblar los selectores de modelos
    async function populateModelSelectors() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            const models = data.models;

            // Limpiar selectores antes de añadir opciones
            $(modelNameSelect).empty().append('<option></option>'); // Añadir opción vacía para placeholder
            $(modelsSelectDemand).empty().append('<option></option>');
            $(modelsSelectEqualization).empty().append('<option></option>');
            $(modelNameFullCostSelect).empty().append('<option></option>');

            models.forEach(model => {
                const option = new Option(model, model, false, false);
                $(modelNameSelect).append(option);
                $(modelsSelectDemand).append(new Option(model, model, false, false));
                $(modelsSelectEqualization).append(new Option(model, model, false, false));
                $(modelNameFullCostSelect).append(new Option(model, model, false, false));
            });

            // Actualizar Select2 para mostrar las nuevas opciones
            $(modelNameSelect).trigger('change');
            $(modelsSelectDemand).trigger('change');
            $(modelsSelectEqualization).trigger('change');
            $(modelNameFullCostSelect).trigger('change');

        } catch (error) {
            console.error('Error al cargar los modelos:', error);
        }
    }

    // Manejadores de eventos para los botones de cálculo
    if (calculateIndividualBtn) {
    calculateIndividualBtn.addEventListener('click', async function() {
        const modelName = modelNameSelect.value;
        const desiredQty = desiredQtyInput.value;

        if (!modelName || !desiredQty) {
            alert('Por favor, seleccione un modelo y una cantidad deseada.');
            return;
        }

        const formData = new FormData();
        formData.append('model_name', modelName);
        formData.append('desired_qty', desiredQty);

        try {
            const response = await fetch('/calculate_individual', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert('Error al calcular la fabricabilidad individual: ' + data.error);
            }
        } catch (error) {
            console.error('Error en la solicitud:', error);
            alert('Ocurrió un error al comunicarse con el servidor.');
        }
    });
    }

    if (calculateLotBtn) {
    calculateLotBtn.addEventListener('click', async function() {
        try {
            const response = await fetch('/calculate_lot', {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert('Error al calcular la fabricabilidad por lote: ' + data.error);
            }
        } catch (error) {
            console.error('Error en la solicitud:', error);
            alert('Ocurrió un error al comunicarse con el servidor.');
        }
    });
    }

    if (calculateModelDemandBtn) {
    calculateModelDemandBtn.addEventListener('click', async function() {
        const selectedModels = $(modelsSelectDemand).val(); // Obtener valores de Select2
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        // DEBUG: Frontend - Proyección de Demanda
        console.log("DEBUG (Frontend - Demanda): selectedModels from Select2:", selectedModels);
        console.log("DEBUG (Frontend - Demanda): selectedModels.length:", selectedModels ? selectedModels.length : 'N/A');
        console.log("DEBUG (Frontend - Demanda): startDate:", startDate);
        console.log("DEBUG (Frontend - Demanda): endDate:", endDate);


        if (!selectedModels || selectedModels.length === 0 || !startDate || !endDate) {
            alert('Por favor, seleccione al menos un modelo y un rango de fechas.');
            return;
        }

        const formData = new FormData();
        // CAMBIO: Usar 'selected_models_demand' como nombre de campo
        formData.append('selected_models_demand', JSON.stringify(selectedModels)); 
        formData.append('start_date', startDate);
        formData.append('end_date', endDate);

        try {
            const response = await fetch('/calculate_model_demand', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            console.log("Respuesta del servidor para proyección de demanda:", data); // DEBUG
            if (data.success) {
                    window.location.href = data.redirect_url + '?t=' + new Date().getTime();
            } else {
                alert('Error al calcular la proyección de demanda: ' + data.error);
            }
        } catch (error) {
            console.error('Error en la solicitud:', error);
            alert('Ocurrió un error al comunicarse con el servidor.');
        }
    });
    }

    // Interceptar el envío del formulario de equilibrado
    const equalizationForm = document.getElementById('equalization_form');
    if (equalizationForm) {
        equalizationForm.addEventListener('submit', async function(e) {
            e.preventDefault(); // Prevenir envío tradicional del formulario
            
            // DEBUG: Verificar si el select existe y tiene opciones
            console.log("DEBUG (Frontend - Equilibrado): modelsSelectEqualization element:", modelsSelectEqualization);
            console.log("DEBUG (Frontend - Equilibrado): Select options count:", $(modelsSelectEqualization).find('option').length);
            console.log("DEBUG (Frontend - Equilibrado): Select is disabled:", modelsSelectEqualization.disabled);
            
            const selectedModels = $(modelsSelectEqualization).val() || []; // Siempre array
            const startDate = startDateEqualizationInput.value;
            const endDate = endDateEqualizationInput.value;

            // DEBUG: Frontend - Equilibrado de Stock
            console.log("DEBUG (Frontend - Equilibrado): selectedModels from Select2:", selectedModels);
            console.log("DEBUG (Frontend - Equilibrado): selectedModels.length:", selectedModels ? selectedModels.length : 'N/A');
            console.log("DEBUG (Frontend - Equilibrado): startDate:", startDate);
            console.log("DEBUG (Frontend - Equilibrado): endDate:", endDate);

            if (!selectedModels.length || !startDate || !endDate) {
                alert('Por favor, seleccione al menos un modelo y un rango de fechas para el equilibrado.');
                console.error("DEBUG (Frontend - Equilibrado): Validation failed. selectedModels:", selectedModels, "startDate:", startDate, "endDate:", endDate);
                return; // This should prevent the fetch call
            }

            const modelsJsonString = JSON.stringify(selectedModels);
            console.log("DEBUG (Frontend - Equilibrado): JSON stringified models:", modelsJsonString);

            const formData = new FormData();
            formData.append('selected_models_equalization', modelsJsonString); 
            formData.append('start_date_equalization', startDate);
            formData.append('end_date_equalization', endDate);

            try {
                const response = await fetch('/calculate_stock_equalization', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                console.log("Respuesta del servidor para equilibrado:", data); // DEBUG
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert('Error al calcular el equilibrado de stock: ' + data.error);
                }
            } catch (error) {
                console.error('Error en la solicitud:', error);
                alert('Ocurrió un error al comunicarse con el servidor.');
            }
        });
    }

    // El event listener del botón ya no es necesario porque interceptamos el formulario
    // if (calculateEqualizationBtn) { ... } - REMOVIDO

    // Interceptar el submit del formulario de costo total de fabricación
    console.log('=== DEBUG: Buscando formulario de costo total ==='); // DEBUG
    const modelFullCostForm = document.getElementById('model_full_cost_form');
    console.log('Buscando formulario model_full_cost_form:', !!modelFullCostForm); // DEBUG
    
    // Verificar todos los formularios en la página
    const allForms = document.querySelectorAll('form');
    console.log('Total de formularios encontrados:', allForms.length);
    allForms.forEach((form, index) => {
        console.log(`Formulario ${index}:`, {
            id: form.id,
            action: form.action,
            method: form.method
        });
    });
    
    if (modelFullCostForm) {
        console.log('Formulario encontrado, agregando event listener'); // DEBUG
        modelFullCostForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Formulario de costo total interceptado'); // DEBUG
            
            // Asegurar que el select esté habilitado antes de calcular
            modelNameFullCostSelect.disabled = false;
            $(modelNameFullCostSelect).prop('disabled', false).trigger('change.select2');
        const modelName = modelNameFullCostSelect.value;
        const quantity = quantityFullCostInput.value;

            console.log('Modelo seleccionado:', modelName); // DEBUG
            console.log('Cantidad:', quantity); // DEBUG

        if (!modelName || !quantity) {
            alert('Por favor, seleccione un modelo y una cantidad para el cálculo de costo total.');
            return;
        }

        const formData = new FormData();
            formData.append('model_name_full_cost', modelName);
            formData.append('quantity_full_cost', quantity);

        try {
                console.log('Enviando solicitud a /calculate_model_full_cost'); // DEBUG
            const response = await fetch('/calculate_model_full_cost', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
                console.log('Respuesta del servidor:', data); // DEBUG
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert('Error al calcular el costo total de fabricación: ' + data.error);
            }
        } catch (error) {
            console.error('Error en la solicitud:', error);
            alert('Ocurrió un error al comunicarse con el servidor.');
        }
    });
        console.log('Event listener agregado exitosamente'); // DEBUG
    } else {
        console.error('No se encontró el formulario model_full_cost_form'); // DEBUG
        // Intentar encontrar el formulario de otra manera
        const allForms = document.querySelectorAll('form');
        console.log('Todos los formularios encontrados:', allForms.length);
        allForms.forEach((form, index) => {
            console.log(`Formulario ${index}:`, form.id, form.action);
        });
        
        // Intentar encontrar el formulario después de un delay
        setTimeout(() => {
            console.log('=== REINTENTANDO BUSCAR FORMULARIO DESPUÉS DE 1 SEGUNDO ==='); // DEBUG
            const retryForm = document.getElementById('model_full_cost_form');
            console.log('Formulario encontrado en retry:', !!retryForm);
            if (retryForm) {
                console.log('Agregando event listener en retry');
                retryForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    console.log('Formulario interceptado en retry');
                    
                    // Asegurar que el select esté habilitado antes de calcular
                    modelNameFullCostSelect.disabled = false;
                    $(modelNameFullCostSelect).prop('disabled', false).trigger('change.select2');
                    const modelName = modelNameFullCostSelect.value;
                    const quantity = quantityFullCostInput.value;

                    console.log('Modelo seleccionado:', modelName); // DEBUG
                    console.log('Cantidad:', quantity); // DEBUG

                    if (!modelName || !quantity) {
                        alert('Por favor, seleccione un modelo y una cantidad para el cálculo de costo total.');
                        return;
                    }

                    const formData = new FormData();
                    formData.append('model_name_full_cost', modelName);
                    formData.append('quantity_full_cost', quantity);

                    try {
                        console.log('Enviando solicitud a /calculate_model_full_cost'); // DEBUG
                        const response = await fetch('/calculate_model_full_cost', {
                            method: 'POST',
                            body: formData
                        });
                        const data = await response.json();
                        console.log('Respuesta del servidor:', data); // DEBUG
                        if (data.success) {
                            window.location.href = data.redirect_url;
                        } else {
                            alert('Error al calcular el costo total de fabricación: ' + data.error);
                        }
                    } catch (error) {
                        console.error('Error en la solicitud:', error);
                        alert('Ocurrió un error al comunicarse con el servidor.');
                    }
                });
            }
        }, 1000);
    }


    // Lógica para la gráfica de ventas históricas
    const historicalSalesChartCtx = document.getElementById('historicalSalesChart');
    const yearFilter = document.getElementById('year_filter');
    const periodFilter = document.getElementById('period_filter');
    const modelFilter = $('#model_filter'); // Usar jQuery para Select2

    // Inicializar Select2 para el filtro de modelos del gráfico
    modelFilter.select2({
        theme: "bootstrap-5",
        width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
        placeholder: "Seleccione modelos para el gráfico",
        allowClear: true,
        multiple: true,
        dropdownParent: $('#sales-chart-card')
    });

    let historicalChart; // Variable para almacenar la instancia del gráfico

    // Asegurarse de que el elemento canvas existe antes de intentar inicializar el gráfico
    if (historicalSalesChartCtx) {
        historicalChart = new Chart(historicalSalesChartCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cantidad Vendida'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Período'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y;
                            }
                        }
                    }
                }
            }
        });
    }

    async function updateSalesChart() {
        const year = yearFilter.value;
        const period = periodFilter.value;
        const selectedModels = modelFilter.val().join(',');
        
        const url = `/api/sales_data?year=${year}&period=${period}&models=${selectedModels}`;
        
        try {
            const response = await fetch(url);
            const chartData = await response.json();
            if (chartData.error) { console.error("Error del servidor:", chartData.error); return; }
            
            historicalChart.data.labels = chartData.labels;
            historicalChart.data.datasets = chartData.datasets;
            historicalChart.update();
        } catch (error) {
            console.error("Error al obtener datos para el gráfico:", error);
        }
    }

    if (yearFilter) yearFilter.addEventListener('change', updateSalesChart);
    if (periodFilter) periodFilter.addEventListener('change', updateSalesChart);
    if (modelFilter) modelFilter.on('change', updateSalesChart);


    // Llamadas iniciales al cargar el DOM
    populateModelSelectors();
    updateFormStates();
    updateFileInputStatus();
    
    // Inicializar costos históricos
    initializeCostosHistoricos();
});

// Mover updateFormStates al scope global
window.updateFormStates = function() {
    console.log("DEBUG: updateFormStates ejecutado");
    // Actualizar banderas de estado de carga de archivos
    const bomStatus = document.getElementById('bom_status');
    const stockStatus = document.getElementById('stock_status');
    const lotStatus = document.getElementById('lot_status');
    const costStatus = document.getElementById('cost_status');
    const salesStatus = document.getElementById('sales_status');
    const suppliersStatus = document.getElementById('suppliers_status');
    
    let bomLoaded = bomStatus ? bomStatus.value === 'True' : false;
    let stockLoaded = stockStatus ? stockStatus.value === 'True' : false;
    let lotLoaded = lotStatus ? lotStatus.value === 'True' : false;
    let costLoaded = costStatus ? costStatus.value === 'True' : false;
    let salesLoaded = salesStatus ? salesStatus.value === 'True' : false;
    let suppliersLoaded = suppliersStatus ? suppliersStatus.value === 'True' : false;

    // Obtener elementos del DOM
    const individualCalcCard = document.getElementById('individual-calc-card');
    const modelNameSelect = document.getElementById('model_name_select');
    const desiredQtyInput = document.getElementById('desired_qty');
    const calculateIndividualBtn = document.getElementById('calculate_individual_btn');
    
    const lotCalcCard = document.getElementById('lot-calc-card');
    const calculateLotBtn = document.getElementById('calculate_lot_btn');
    
    const modelDemandCard = document.getElementById('model-demand-card');
    const calculateModelDemandBtn = document.getElementById('calculate_model_demand_btn');
    const modelsSelectDemand = document.getElementById('models_select_demand');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    const equalizationCalcCard = document.getElementById('equalization-calc-card');
    const calculateEqualizationBtn = document.getElementById('calculate_equalization_btn');
    const modelsSelectEqualization = document.getElementById('models_select_equalization');
    const startDateEqualizationInput = document.getElementById('start_date_equalization');
    const endDateEqualizationInput = document.getElementById('end_date_equalization');
    
    const modelFullCostCard = document.getElementById('model-full_cost-card');
    const modelNameFullCostSelect = document.getElementById('model_name_full_cost_select');
    const quantityFullCostInput = document.getElementById('quantity_full_cost');
    const calculateFullCostBtn = document.getElementById('calculate_full_cost_btn');

    // Lógica para la tarjeta de cálculo individual
    if (individualCalcCard && modelNameSelect && desiredQtyInput && calculateIndividualBtn) {
        if (bomLoaded && stockLoaded && costLoaded) {
            individualCalcCard.classList.remove('disabled');
            modelNameSelect.disabled = false;
            desiredQtyInput.disabled = false;
            calculateIndividualBtn.disabled = false;
        } else {
            individualCalcCard.classList.add('disabled');
            modelNameSelect.disabled = true;
            desiredQtyInput.disabled = true;
            calculateIndividualBtn.disabled = true;
        }
    }

    // Lógica para la tarjeta de cálculo de lote
    if (lotCalcCard && calculateLotBtn) {
        if (bomLoaded && stockLoaded && lotLoaded && costLoaded) {
            lotCalcCard.classList.remove('disabled');
            calculateLotBtn.disabled = false;
        } else {
            lotCalcCard.classList.add('disabled');
            calculateLotBtn.disabled = true;
        }
    }

    // Lógica para la tarjeta de proyección de demanda
    if (modelDemandCard && calculateModelDemandBtn && modelsSelectDemand && startDateInput && endDateInput) {
        if (bomLoaded && stockLoaded && salesLoaded && costLoaded) {
            modelDemandCard.classList.remove('disabled');
            calculateModelDemandBtn.disabled = false;
            modelsSelectDemand.disabled = false;
            startDateInput.disabled = false;
            endDateInput.disabled = false;
        } else {
            modelDemandCard.classList.add('disabled');
            calculateModelDemandBtn.disabled = true;
            modelsSelectDemand.disabled = true;
            startDateInput.disabled = true;
            endDateInput.disabled = true;
        }
    }

    // Lógica para la tarjeta de equilibrado de stock
    if (equalizationCalcCard && calculateEqualizationBtn && modelsSelectEqualization && startDateEqualizationInput && endDateEqualizationInput) {
        if (bomLoaded && stockLoaded && salesLoaded && costLoaded && suppliersLoaded) {
            equalizationCalcCard.classList.remove('disabled');
            calculateEqualizationBtn.disabled = false;
            modelsSelectEqualization.disabled = false;
            startDateEqualizationInput.disabled = false;
            endDateEqualizationInput.disabled = false;
        } else {
            equalizationCalcCard.classList.add('disabled');
            calculateEqualizationBtn.disabled = true;
            modelsSelectEqualization.disabled = true;
            startDateEqualizationInput.disabled = true;
            endDateEqualizationInput.disabled = true;
        }
    }

    // Lógica para la tarjeta de costo total de fabricación de un modelo
    if (modelFullCostCard && modelNameFullCostSelect && quantityFullCostInput && calculateFullCostBtn) {
        if (bomLoaded && costLoaded) {
            modelFullCostCard.classList.remove('disabled');
            modelNameFullCostSelect.disabled = false;
            quantityFullCostInput.disabled = false;
            calculateFullCostBtn.disabled = false;
            // Refrescar Select2 para reflejar el estado habilitado
            if (window.jQuery) {
                $(modelNameFullCostSelect).prop('disabled', false).trigger('change.select2');
            }
        } else {
            modelFullCostCard.classList.add('disabled');
            modelNameFullCostSelect.disabled = true;
            quantityFullCostInput.disabled = true;
            calculateFullCostBtn.disabled = true;
            // Refrescar Select2 para reflejar el estado deshabilitado
            if (window.jQuery) {
                $(modelNameFullCostSelect).prop('disabled', true).trigger('change.select2');
            }
        }
    }
};

// Función para mostrar secciones (mover a global scope)
window.showSection = function(section) {
    console.log('DEBUG: showSection llamado con:', section);
    const sections = ['dashboard', 'carga', 'fabricabilidad', 'demanda', 'equilibrado', 'costo_total', 'costos', 'analisis', 'admin'];
    sections.forEach(s => {
        const sectionElement = document.getElementById('section-' + s);
        // Corregir el nombre del tab para costo_total
        const tabId = s === 'costo_total' ? 'tab-costo-total' : 'tab-' + s;
        const tabElement = document.getElementById(tabId);
        
        if (sectionElement) {
            sectionElement.style.display = (s === section) ? '' : 'none';
            console.log('DEBUG: Sección', s, 'display:', sectionElement.style.display);
        } else {
            console.error('DEBUG: No se encontró elemento para sección:', s);
        }
        
        if (tabElement) {
            tabElement.classList.toggle('active', s === section);
        } else {
            console.error('DEBUG: No se encontró tab para sección:', s, '(buscando:', tabId, ')');
        }
    });
    
    // Inicializar dashboard si es la sección activa
    if (section === 'dashboard') {
        console.log('DEBUG: Inicializando dashboard');
        initializeDashboard();
    }
    
    // Inicializar costos históricos si es la sección activa
    if (section === 'costos') {
        console.log('DEBUG: Inicializando costos históricos');
        initializeCostosHistoricos();
    }
    
    // Inicializar análisis de ventas si es la sección activa
    if (section === 'analisis') {
        console.log('DEBUG: Inicializando análisis de ventas');
        initializeSalesAnalysis();
    }
    
    // Inicializar administración si es la sección activa
    if (section === 'admin') {
        console.log('DEBUG: Inicializando administración');
        loadAdminData();
    }
};

// Lógica para costos históricos
function initializeCostosHistoricos() {
    const articuloCostosSelect = document.getElementById('articulo_costos_select');
    if (articuloCostosSelect) {
        console.log('Inicializando costos históricos');
        cargarArticulosCostos();
        articuloCostosSelect.addEventListener('change', function() {
            cargarHistorialArticulo(this.value);
        });
    }
}

let articulosCostos = [];
let chartCostos = null;

function cargarArticulosCostos() {
    fetch('/api/historico_costos')
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                articulosCostos = data.articulos;
                const select = document.getElementById('articulo_costos_select');
                if (select) {
                    select.innerHTML = '<option value="">Seleccionar artículo...</option>' +
                        articulosCostos.map(a => `<option value="${a}">${a}</option>`).join('');
                }
            } else {
                mostrarAlertaCostos(data.error || 'No hay datos de costos históricos cargados.');
            }
        })
        .catch(() => mostrarAlertaCostos('Error al consultar los artículos.'));
}

function mostrarAlertaCostos(msg) {
    const visual = document.getElementById('costos-historicos-visualizacion');
    const alert = document.getElementById('costos-historicos-alert');
    if (visual) visual.style.display = 'none';
    if (alert) {
        alert.style.display = '';
        alert.textContent = msg;
    }
}

function ocultarAlertaCostos() {
    const alert = document.getElementById('costos-historicos-alert');
    if (alert) alert.style.display = 'none';
}

function cargarHistorialArticulo(articulo) {
    if (!articulo) {
        const visual = document.getElementById('costos-historicos-visualizacion');
        if (visual) visual.style.display = 'none';
        return;
    }
    fetch(`/api/historico_costos?articulo=${encodeURIComponent(articulo)}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                ocultarAlertaCostos();
                mostrarHistorialCostos(data.historial);
            } else {
                mostrarAlertaCostos(data.error || 'No se pudo obtener el historial.');
            }
        })
        .catch(() => mostrarAlertaCostos('Error al consultar el historial.'));
}

function mostrarHistorialCostos(historial) {
    const visual = document.getElementById('costos-historicos-visualizacion');
    const tbody = document.getElementById('costos-historicos-tbody');
    const canvas = document.getElementById('costosHistoricosChart');
    
    if (!visual || !tbody || !canvas) {
        console.error('Elementos de costos históricos no encontrados');
        return;
    }
    
    tbody.innerHTML = '';
    let labels = [], data = [];
    historial.forEach(item => {
        if (item.costo !== null && !isNaN(item.costo)) {
            labels.push(item.anio);
            data.push(item.costo);
            tbody.innerHTML += `<tr><td>${item.anio}</td><td>$ ${item.costo.toFixed(2)}</td></tr>`;
        }
    });
    
    if (labels.length === 0) {
        visual.style.display = 'none';
        mostrarAlertaCostos('No hay datos de costos para este artículo.');
        return;
    }
    
    visual.style.display = '';
    
    // Gráfico
    if (chartCostos) chartCostos.destroy();
    const ctx = canvas.getContext('2d');
    chartCostos = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Costo (USD)',
                data: data,
                borderColor: '#0979b0',
                backgroundColor: 'rgba(12,183,242,0.15)',
                pointBackgroundColor: '#0cb7f2',
                pointRadius: 5,
                fill: true,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            },
            scales: {
                x: { title: { display: true, text: 'Año', color: '#004173', font: { weight: 'bold' } } },
                y: { title: { display: true, text: 'Costo (USD)', color: '#004173', font: { weight: 'bold' } }, beginAtZero: true }
            }
        }
    });
}

// Lógica para análisis de ventas históricas
function initializeSalesAnalysis() {
    console.log('DEBUG: Inicializando análisis de ventas');
    
    // Inicializar Select2 para el filtro de modelos
    const modelFilter = $('#model_filter');
    console.log('DEBUG: Elemento model_filter encontrado:', modelFilter.length > 0);
    
    if (modelFilter.length) {
        console.log('DEBUG: Inicializando Select2 para model_filter');
        modelFilter.select2({
            theme: "bootstrap-5",
            width: '100%',
            placeholder: "Selecciona modelos para filtrar",
            allowClear: true,
            multiple: true,
            language: {
                noResults: function() {
                    return "No se encontraron modelos";
                },
                searching: function() {
                    return "Buscando...";
                }
            }
        });
        console.log('DEBUG: Select2 inicializado para model_filter');
    } else {
        console.error('DEBUG: No se encontró el elemento model_filter');
    }
    
    // Cargar modelos en el filtro
    console.log('DEBUG: Llamando a loadModelsForFilter');
    loadModelsForFilter();
    
    // Inicializar gráficos
    console.log('DEBUG: Inicializando gráficos');
    initializeSalesCharts();
    
    // Agregar event listeners para los filtros
    const yearFilter = document.getElementById('year_filter');
    const periodFilter = document.getElementById('period_filter');
    
    console.log('DEBUG: Elementos de filtro encontrados:', {
        yearFilter: !!yearFilter,
        periodFilter: !!periodFilter,
        modelFilter: modelFilter.length > 0
    });
    
    // Agregar event listeners con logging
    if (yearFilter) {
        console.log('DEBUG: Agregando event listener para year_filter');
        yearFilter.addEventListener('change', function() {
            console.log('DEBUG: Evento change detectado en year_filter, valor:', yearFilter.value);
            updateSalesAnalysis();
        });
    } else {
        console.error('DEBUG: No se encontró year_filter');
    }
    
    if (periodFilter) {
        console.log('DEBUG: Agregando event listener para period_filter');
        periodFilter.addEventListener('change', function() {
            console.log('DEBUG: Evento change detectado en period_filter, valor:', periodFilter.value);
            updateSalesAnalysis();
        });
    } else {
        console.error('DEBUG: No se encontró period_filter');
    }
    
    if (modelFilter.length) {
        console.log('DEBUG: Agregando event listener para model_filter');
        modelFilter.on('change', function() {
            const selectedModels = modelFilter.val();
            console.log('DEBUG: Evento change detectado en model_filter, modelos seleccionados:', selectedModels);
            updateSalesAnalysis();
        });
    } else {
        console.error('DEBUG: No se encontró model_filter');
    }
    
    // Cargar datos iniciales
    console.log('DEBUG: Cargando datos iniciales');
    updateSalesAnalysis();
}

let historicalChart = null;
let distributionChart = null;

function initializeSalesCharts() {
    console.log('DEBUG: Inicializando gráficos de ventas');
    
    // Gráfico principal de ventas históricas
    const historicalCtx = document.getElementById('historicalSalesChart');
    if (historicalCtx) {
        console.log('DEBUG: Canvas historicalSalesChart encontrado');
        
        // Destruir gráfico existente si existe
        if (historicalChart) {
            console.log('DEBUG: Destruyendo gráfico histórico existente');
            try {
                historicalChart.destroy();
            } catch (error) {
                console.warn('DEBUG: Error al destruir gráfico histórico:', error);
            }
            historicalChart = null;
        }
        
        // Verificar que el canvas esté disponible
        if (historicalCtx.getContext) {
            console.log('DEBUG: Creando nuevo gráfico histórico');
            historicalChart = new Chart(historicalCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                color: '#ffffff',
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#ffffff',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Período',
                                color: '#ffffff',
                                font: { weight: 'bold' }
                            },
                            ticks: {
                                color: '#ffffff'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            border: {
                                color: 'rgba(255, 255, 255, 0.3)'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Cantidad Vendida',
                                color: '#ffffff',
                                font: { weight: 'bold' }
                            },
                            beginAtZero: true,
                            ticks: {
                                color: '#ffffff'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            border: {
                                color: 'rgba(255, 255, 255, 0.3)'
                            }
                        }
                    }
                }
            });
            console.log('DEBUG: Gráfico histórico creado exitosamente');
        } else {
            console.error('DEBUG: No se puede obtener contexto del canvas histórico');
        }
    } else {
        console.error('DEBUG: No se encontró el canvas historicalSalesChart');
    }
    
    // Gráfico de distribución por modelo
    const distributionCtx = document.getElementById('modelDistributionChart');
    if (distributionCtx) {
        console.log('DEBUG: Canvas modelDistributionChart encontrado');
        
        // Destruir gráfico existente si existe
        if (distributionChart) {
            console.log('DEBUG: Destruyendo gráfico de distribución existente');
            try {
                distributionChart.destroy();
            } catch (error) {
                console.warn('DEBUG: Error al destruir gráfico de distribución:', error);
            }
            distributionChart = null;
        }
        
        // Verificar que el canvas esté disponible
        if (distributionCtx.getContext) {
            console.log('DEBUG: Creando nuevo gráfico de distribución');
            try {
                distributionChart = new Chart(distributionCtx, {
                    type: 'doughnut',
                    data: {
                        labels: [],
                        datasets: [{
                            data: [],
                            backgroundColor: [
                                '#0979b0', '#0cb7f2', '#7cdaf9', '#004173',
                                '#28a745', '#ffc107', '#dc3545', '#6f42c1'
                            ],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    color: '#ffffff',
                                    padding: 20,
                                    usePointStyle: true
                                }
                            },
                            tooltip: {
                                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                titleColor: '#ffffff',
                                bodyColor: '#ffffff',
                                borderColor: '#ffffff',
                                borderWidth: 1
                            }
                        }
                    }
                });
                console.log('DEBUG: Gráfico de distribución creado exitosamente');
            } catch (error) {
                console.error('DEBUG: Error al crear gráfico de distribución:', error);
            }
        } else {
            console.error('DEBUG: No se puede obtener contexto del canvas de distribución');
        }
    } else {
        console.error('DEBUG: No se encontró el canvas modelDistributionChart');
    }
}

async function loadModelsForFilter() {
    try {
        console.log('DEBUG: Cargando modelos para filtro...');
        const response = await fetch('/api/models');
        console.log('DEBUG: Respuesta del servidor:', response);
        const data = await response.json();
        console.log('DEBUG: Datos recibidos:', data);
        
        if (data.success) {
            console.log('DEBUG: Modelos encontrados:', data.models);
            const modelFilter = $('#model_filter');
            modelFilter.empty();
            data.models.forEach(model => {
                modelFilter.append(new Option(model, model, false, false));
            });
            modelFilter.trigger('change');
            console.log('DEBUG: Filtro de modelos actualizado');
        } else {
            console.error('DEBUG: Error al cargar modelos:', data.error);
        }
    } catch (error) {
        console.error('Error al cargar modelos para filtro:', error);
    }
}

async function updateSalesAnalysis() {
    console.log('DEBUG: ===== INICIO updateSalesAnalysis =====');
    
    const year = document.getElementById('year_filter')?.value || '';
    const period = document.getElementById('period_filter')?.value || 'year';
    const models = $('#model_filter').val() || [];
    
    console.log('DEBUG: updateSalesAnalysis - Parámetros:', {
        year: year,
        period: period,
        models: models,
        modelsLength: models.length
    });
    
    // Verificar que los elementos existen
    const yearFilter = document.getElementById('year_filter');
    const periodFilter = document.getElementById('period_filter');
    const modelFilter = $('#model_filter');
    
    console.log('DEBUG: Elementos encontrados:', {
        yearFilter: !!yearFilter,
        periodFilter: !!periodFilter,
        modelFilter: modelFilter.length > 0,
        yearFilterValue: yearFilter?.value,
        periodFilterValue: periodFilter?.value,
        modelFilterValue: modelFilter.val()
    });
    
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    if (period) params.append('period', period);
    if (models.length > 0) params.append('models', models.join(','));
    
    const url = `/api/sales_analysis?${params.toString()}`;
    console.log('DEBUG: URL de la petición:', url);
    
    try {
        console.log('DEBUG: Enviando petición al servidor...');
        const response = await fetch(url);
        console.log('DEBUG: Respuesta del servidor:', response);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('DEBUG: Datos recibidos:', data);
        
        if (data.success) {
            console.log('DEBUG: Actualizando gráficos y resumen');
            
            // Verificar que todos los datos necesarios estén presentes
            if (data.chart_data) {
                console.log('DEBUG: Actualizando gráfico de ventas');
                updateSalesChart(data.chart_data);
            } else {
                console.error('DEBUG: No se recibieron datos de gráfico');
            }
            
            if (data.summary) {
                console.log('DEBUG: Actualizando resumen estadístico');
                updateSummary(data.summary);
            } else {
                console.error('DEBUG: No se recibieron datos de resumen');
            }
            
            if (data.distribution) {
                console.log('DEBUG: Actualizando gráfico de distribución');
                updateDistributionChart(data.distribution);
            } else {
                console.error('DEBUG: No se recibieron datos de distribución');
            }
            
            if (data.details) {
                console.log('DEBUG: Actualizando tabla de detalles');
                updateDetailsTable(data.details);
            } else {
                console.error('DEBUG: No se recibieron datos de detalles');
            }
            
            console.log('DEBUG: Análisis de ventas actualizado completamente');
        } else {
            console.error('Error en análisis de ventas:', data.error);
            // Mostrar mensaje de error al usuario
            const summaryElement = document.getElementById('sales-summary');
            if (summaryElement) {
                summaryElement.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            }
        }
    } catch (error) {
        console.error('Error al obtener datos de análisis:', error);
        // Mostrar mensaje de error al usuario
        const summaryElement = document.getElementById('sales-summary');
        if (summaryElement) {
            summaryElement.innerHTML = `<div class="alert alert-danger">Error al cargar datos: ${error.message}</div>`;
        }
    }
    
    console.log('DEBUG: ===== FIN updateSalesAnalysis =====');
}

function updateSalesChart(chartData) {
    console.log('DEBUG: updateSalesChart - Datos recibidos:', chartData);
    
    if (!chartData || !chartData.labels || !chartData.datasets) {
        console.error('DEBUG: Datos de gráfico inválidos:', chartData);
        return;
    }
    
    if (historicalChart) {
        try {
            console.log('DEBUG: Actualizando gráfico histórico con', chartData.labels.length, 'etiquetas y', chartData.datasets.length, 'datasets');
            historicalChart.data.labels = chartData.labels;
            historicalChart.data.datasets = chartData.datasets;
            historicalChart.update('none'); // Usar 'none' para evitar animaciones que puedan causar problemas
            console.log('DEBUG: Gráfico de ventas actualizado exitosamente');
        } catch (error) {
            console.error('DEBUG: Error al actualizar gráfico histórico:', error);
        }
    } else {
        console.error('DEBUG: historicalChart no está inicializado');
    }
}

function updateSummary(summary) {
    console.log('DEBUG: updateSummary - Datos recibidos:', summary);
    
    if (!summary) {
        console.error('DEBUG: Datos de resumen inválidos');
        return;
    }
    
    const summaryElement = document.getElementById('sales-summary');
    if (summaryElement) {
        try {
            summaryElement.innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <div class="text-center">
                            <h4 class="text-primary">${summary.total_sales.toLocaleString()}</h4>
                            <small class="text-muted">Total de Ventas</small>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="text-center">
                            <h4 class="text-success">${summary.avg_sales.toLocaleString()}</h4>
                            <small class="text-muted">Promedio por Período</small>
                        </div>
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="col-12">
                        <div class="text-center">
                            <h6 class="text-info">Modelo Más Vendido</h6>
                            <p class="mb-0"><strong>${summary.top_model}</strong></p>
                            <small class="text-muted">${summary.top_sales.toLocaleString()} unidades</small>
                        </div>
                    </div>
                </div>
            `;
            console.log('DEBUG: Resumen estadístico actualizado exitosamente');
        } catch (error) {
            console.error('DEBUG: Error al actualizar resumen:', error);
        }
    } else {
        console.error('DEBUG: Elemento sales-summary no encontrado');
    }
}

function updateDistributionChart(distribution) {
    console.log('DEBUG: updateDistributionChart - Datos recibidos:', distribution);
    console.log('DEBUG: distributionChart variable:', distributionChart);
    console.log('DEBUG: typeof distributionChart:', typeof distributionChart);
    
    if (!distribution || !distribution.labels || !distribution.data) {
        console.error('DEBUG: Datos de distribución inválidos:', distribution);
        return;
    }
    
    // Verificar si el gráfico existe y está disponible
    if (distributionChart && typeof distributionChart.update === 'function') {
        console.log('DEBUG: distributionChart existe y es válido, actualizando...');
        try {
            console.log('DEBUG: Actualizando gráfico de distribución con', distribution.labels.length, 'modelos');
            distributionChart.data.labels = distribution.labels;
            distributionChart.data.datasets[0].data = distribution.data;
            distributionChart.update('none'); // Usar 'none' para evitar animaciones que puedan causar problemas
            console.log('DEBUG: Gráfico de distribución actualizado exitosamente');
        } catch (error) {
            console.error('DEBUG: Error al actualizar gráfico de distribución:', error);
            // Si hay error, intentar recrear el gráfico
            distributionChart = null;
        }
    }
    
    // Si el gráfico no existe o no es válido, crear uno nuevo
    if (!distributionChart || typeof distributionChart.update !== 'function') {
        console.log('DEBUG: Creando nuevo gráfico de distribución...');
        
        // Intentar reinicializar el gráfico
        const distributionCtx = document.getElementById('modelDistributionChart');
        if (distributionCtx) {
            console.log('DEBUG: Canvas modelDistributionChart encontrado, creando nuevo gráfico');
            try {
                distributionChart = new Chart(distributionCtx, {
                    type: 'doughnut',
                    data: {
                        labels: distribution.labels,
                        datasets: [{
                            data: distribution.data,
                            backgroundColor: [
                                '#0979b0', '#0cb7f2', '#7cdaf9', '#004173',
                                '#28a745', '#ffc107', '#dc3545', '#6f42c1'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((context.parsed / total) * 100).toFixed(1);
                                        return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                                    }
                                }
                            }
                        }
                    }
                });
                console.log('DEBUG: Gráfico de distribución creado exitosamente en updateDistributionChart');
                // Actualizar la variable global
                window.distributionChart = distributionChart;
            } catch (error) {
                console.error('DEBUG: Error al crear gráfico de distribución:', error);
                distributionChart = null;
            }
        } else {
            console.error('DEBUG: No se encontró el canvas modelDistributionChart');
        }
    }
}

function updateDetailsTable(details) {
    console.log('DEBUG: updateDetailsTable - Datos recibidos:', details);
    
    if (!Array.isArray(details)) {
        console.error('DEBUG: Datos de detalles inválidos:', details);
        return;
    }
    
    const tbody = document.getElementById('sales-details-tbody');
    if (tbody) {
        try {
            if (details.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No hay datos para mostrar</td></tr>';
                console.log('DEBUG: Tabla de detalles actualizada - sin datos');
            } else {
                console.log('DEBUG: Actualizando tabla con', details.length, 'registros');
                tbody.innerHTML = details.map(detail => `
                    <tr>
                        <td>${detail.period || ''}</td>
                        <td>${detail.model || ''}</td>
                        <td>${(detail.quantity || 0).toLocaleString()}</td>
                        <td>${(detail.percentage || 0).toFixed(2)}%</td>
                    </tr>
                `).join('');
                console.log('DEBUG: Tabla de detalles actualizada exitosamente');
            }
        } catch (error) {
            console.error('DEBUG: Error al actualizar tabla de detalles:', error);
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-danger">Error al cargar datos</td></tr>';
        }
    } else {
        console.error('DEBUG: Elemento sales-details-tbody no encontrado');
    }
}

// Inicializar análisis de ventas cuando se active la sección
window.showSection = function(section) {
    console.log('DEBUG: showSection llamado con:', section);
    const sections = ['dashboard', 'carga', 'fabricabilidad', 'demanda', 'equilibrado', 'costo_total', 'costos', 'analisis', 'admin'];
    sections.forEach(s => {
        const sectionElement = document.getElementById('section-' + s);
        // Corregir el nombre del tab para costo_total
        const tabId = s === 'costo_total' ? 'tab-costo-total' : 'tab-' + s;
        const tabElement = document.getElementById(tabId);
        
        if (sectionElement) {
            sectionElement.style.display = (s === section) ? '' : 'none';
            console.log('DEBUG: Sección', s, 'display:', sectionElement.style.display);
        } else {
            console.error('DEBUG: No se encontró elemento para sección:', s);
        }
        
        if (tabElement) {
            tabElement.classList.toggle('active', s === section);
        } else {
            console.error('DEBUG: No se encontró tab para sección:', s, '(buscando:', tabId, ')');
        }
    });
    
    // Inicializar dashboard si es la sección activa
    if (section === 'dashboard') {
        console.log('DEBUG: Inicializando dashboard');
        initializeDashboard();
    }
    
    // Inicializar costos históricos si es la sección activa
    if (section === 'costos') {
        console.log('DEBUG: Inicializando costos históricos');
        initializeCostosHistoricos();
    }
    
    // Inicializar análisis de ventas si es la sección activa
    if (section === 'analisis') {
        console.log('DEBUG: Inicializando análisis de ventas');
        initializeSalesAnalysis();
    }
    
    // Inicializar administración si es la sección activa
    if (section === 'admin') {
        console.log('DEBUG: Inicializando administración');
        loadAdminData();
    }
};

// Función para limpiar caché y forzar recarga completa
function forceReload() {
    console.log('DEBUG: Forzando recarga completa de la página');
    // Limpiar caché del navegador
    if ('caches' in window) {
        caches.keys().then(function(names) {
            for (let name of names) {
                caches.delete(name);
            }
        });
    }
    // Forzar recarga completa
    window.location.reload(true);
}

// Función para verificar si hay errores de JavaScript
function checkForErrors() {
    console.log('DEBUG: Verificando errores de JavaScript');
    
    // Verificar si hay funciones problemáticas
    if (typeof actualizarTextoSeleccionadosEqualizacion !== 'undefined') {
        console.error('DEBUG: Función problemática encontrada: actualizarTextoSeleccionadosEqualizacion');
        console.log('DEBUG: Se recomienda recargar la página para limpiar la caché');
    }
    
    // Verificar elementos del DOM
    const requiredElements = [
        'historicalSalesChart',
        'modelDistributionChart',
        'sales-summary',
        'sales-details-tbody',
        'year_filter',
        'period_filter',
        'model_filter'
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    if (missingElements.length > 0) {
        console.error('DEBUG: Elementos faltantes:', missingElements);
    } else {
        console.log('DEBUG: Todos los elementos requeridos están presentes');
    }
}

// Ejecutar verificación de errores al cargar
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(checkForErrors, 1000); // Esperar 1 segundo para que todo se cargue
});

// Función para probar manualmente updateSalesAnalysis
function testUpdateSalesAnalysis() {
    console.log('DEBUG: ===== PRUEBA MANUAL updateSalesAnalysis =====');
    
    // Verificar estado inicial
    console.log('DEBUG: Estado inicial de gráficos:');
    console.log('  historicalChart:', historicalChart);
    console.log('  distributionChart:', distributionChart);
    
    // Llamar a la función
    updateSalesAnalysis();
    
    // Verificar estado después de la llamada
    setTimeout(() => {
        console.log('DEBUG: Estado después de updateSalesAnalysis:');
        console.log('  historicalChart:', historicalChart);
        console.log('  distributionChart:', distributionChart);
    }, 1000);
}

// Función para verificar el estado de los filtros
function checkFilterStatus() {
    console.log('DEBUG: ===== VERIFICACIÓN DE FILTROS =====');
    
    const yearFilter = document.getElementById('year_filter');
    const periodFilter = document.getElementById('period_filter');
    const modelFilter = $('#model_filter');
    
    console.log('DEBUG: Estado de filtros:', {
        yearFilter: {
            exists: !!yearFilter,
            value: yearFilter?.value,
            options: yearFilter ? Array.from(yearFilter.options).map(opt => opt.value) : []
        },
        periodFilter: {
            exists: !!periodFilter,
            value: periodFilter?.value,
            options: periodFilter ? Array.from(periodFilter.options).map(opt => opt.value) : []
        },
        modelFilter: {
            exists: modelFilter.length > 0,
            value: modelFilter.val(),
            selectedCount: modelFilter.val() ? modelFilter.val().length : 0
        }
    });
    
    // Verificar event listeners
    if (yearFilter) {
        console.log('DEBUG: year_filter event listeners:', yearFilter.onchange ? 'SÍ' : 'NO');
    }
    if (periodFilter) {
        console.log('DEBUG: period_filter event listeners:', periodFilter.onchange ? 'SÍ' : 'NO');
    }
    if (modelFilter.length) {
        console.log('DEBUG: model_filter event listeners:', modelFilter.hasClass('select2-hidden-accessible') ? 'SÍ (Select2)' : 'NO');
    }
}

// Agregar funciones al objeto window para acceso desde consola
window.testUpdateSalesAnalysis = testUpdateSalesAnalysis;
window.checkFilterStatus = checkFilterStatus;

// Función para verificar el estado de los gráficos
function checkChartStatus() {
    console.log('DEBUG: ===== VERIFICACIÓN DE GRÁFICOS =====');
    console.log('DEBUG: Estado de gráficos:');
    console.log('  historicalChart:', historicalChart);
    console.log('  distributionChart:', distributionChart);
    console.log('  typeof historicalChart:', typeof historicalChart);
    console.log('  typeof distributionChart:', typeof distributionChart);
    console.log('  historicalChart.update:', historicalChart ? typeof historicalChart.update : 'N/A');
    console.log('  distributionChart.update:', distributionChart ? typeof distributionChart.update : 'N/A');
    
    // Verificar canvas elements
    const historicalCtx = document.getElementById('historicalSalesChart');
    const distributionCtx = document.getElementById('modelDistributionChart');
    console.log('DEBUG: Canvas elements:');
    console.log('  historicalSalesChart:', historicalCtx);
    console.log('  modelDistributionChart:', distributionCtx);
}

window.checkChartStatus = checkChartStatus;

// ===== DASHBOARD FUNCTIONS =====

// Variables globales para los gráficos del dashboard
let trendChart = null;
let periodDistributionChart = null;

// Función para inicializar el dashboard
function initializeDashboard() {
    console.log('DEBUG: Inicializando dashboard...');
    
    // Inicializar gráficos del dashboard
    initializeDashboardCharts();
    
    // Verificar si hay archivos cargados de múltiples formas
    const hasLoadedFiles = checkForLoadedFiles();
    console.log('DEBUG: Archivos cargados detectados:', hasLoadedFiles);
    
    if (hasLoadedFiles) {
        console.log('DEBUG: Archivos detectados, cargando datos del dashboard...');
        refreshDashboard();
    } else {
        console.log('DEBUG: No hay archivos cargados, mostrando dashboard vacío');
        showDashboardWelcome();
    }
}

// Función para verificar si hay archivos cargados
function checkForLoadedFiles() {
    // Verificar badges de éxito
    const successBadges = document.querySelectorAll('.badge-success');
    if (successBadges.length > 0) {
        console.log('DEBUG: Encontrados badges de éxito:', successBadges.length);
        return true;
    }
    
    // Verificar elementos de estado de archivos
    const fileStatusElements = [
        'bom_status',
        'stock_status', 
        'lot_status',
        'cost_status',
        'sales_status',
        'suppliers_status'
    ];
    
    for (const elementId of fileStatusElements) {
        const element = document.getElementById(elementId);
        if (element && element.value === 'True') {
            console.log('DEBUG: Archivo cargado detectado en:', elementId);
            return true;
        }
    }
    
    // Verificar si hay datos en session (backend)
    console.log('DEBUG: No se detectaron archivos cargados en el frontend');
    return false;
}

// Función para inicializar los gráficos del dashboard
function initializeDashboardCharts() {
    console.log('DEBUG: Inicializando gráficos del dashboard...');
    
    // Gráfico de tendencias
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        try {
            if (trendChart) {
                trendChart.destroy();
            }
            trendChart = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Ventas Mensuales',
                        data: [],
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#ffffff',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#ffffff'
                            },
                            border: {
                                color: 'rgba(255, 255, 255, 0.3)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#ffffff'
                            },
                            border: {
                                color: 'rgba(255, 255, 255, 0.3)'
                            }
                        }
                    }
                }
            });
            console.log('DEBUG: Gráfico de tendencias inicializado');
        } catch (error) {
            console.error('DEBUG: Error al inicializar gráfico de tendencias:', error);
        }
    }
    
    // Gráfico de distribución por período
    const periodCtx = document.getElementById('periodDistributionChart');
    if (periodCtx) {
        try {
            if (periodDistributionChart) {
                periodDistributionChart.destroy();
            }
            periodDistributionChart = new Chart(periodCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#007bff',
                            '#28a745',
                            '#ffc107',
                            '#dc3545',
                            '#6f42c1',
                            '#fd7e14'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#ffffff',
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#ffffff',
                            borderWidth: 1
                        }
                    }
                }
            });
            console.log('DEBUG: Gráfico de distribución por período inicializado');
        } catch (error) {
            console.error('DEBUG: Error al inicializar gráfico de distribución:', error);
        }
    }
}

// Función para actualizar el dashboard
async function refreshDashboard() {
    console.log('DEBUG: Actualizando dashboard...');
    
    // Mostrar estado de carga
    showDashboardLoading();
    
    try {
        // Obtener datos del dashboard desde el backend
        const response = await fetch('/api/dashboard_data');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateDashboardKPIs(data.kpis);
            updateDashboardCharts(data.charts);
            updateDashboardAlerts(data.alerts);
            console.log('DEBUG: Dashboard actualizado exitosamente');
        } else {
            throw new Error(data.error || 'Error al cargar datos del dashboard');
        }
    } catch (error) {
        console.error('DEBUG: Error al actualizar dashboard:', error);
        showDashboardError(error.message);
    }
}

// Función para mostrar estado de carga del dashboard
function showDashboardLoading() {
    const kpiElements = [
        'total-sales-kpi',
        'total-models-kpi',
        'avg-sales-kpi',
        'top-model-kpi'
    ];
    
    kpiElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = '...';
            element.parentElement.classList.add('kpi-loading');
        }
    });
}

// Función para mostrar mensaje de bienvenida
function showDashboardWelcome() {
    const alertsContainer = document.getElementById('dashboard-alerts');
    if (alertsContainer) {
        alertsContainer.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                <strong>Bienvenido al Dashboard:</strong> Los KPIs se actualizarán automáticamente cuando cargues los archivos de datos.
            </div>
        `;
    }
}

// Función para mostrar error en el dashboard
function showDashboardError(message) {
    const alertsContainer = document.getElementById('dashboard-alerts');
    if (alertsContainer) {
        alertsContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
}

// Función para forzar la carga del dashboard (para debugging)
function forceDashboardLoad() {
    console.log('DEBUG: Forzando carga del dashboard...');
    refreshDashboard();
}

// Función para actualizar los KPIs del dashboard
function updateDashboardKPIs(kpis) {
    console.log('DEBUG: Actualizando KPIs:', kpis);
    
    // Remover estado de carga
    const kpiCards = document.querySelectorAll('.kpi-card');
    kpiCards.forEach(card => card.classList.remove('kpi-loading'));
    
    // Actualizar cada KPI
    if (kpis.total_sales !== undefined) {
        const element = document.getElementById('total-sales-kpi');
        if (element) {
            element.textContent = formatNumber(kpis.total_sales);
        }
        
        const changeElement = document.getElementById('sales-change');
        if (changeElement && kpis.sales_change !== undefined) {
            const change = kpis.sales_change;
            const changeText = change >= 0 ? `+${change}%` : `${change}%`;
            const changeClass = change >= 0 ? 'text-success' : 'text-danger';
            changeElement.innerHTML = `<span class="${changeClass}">${changeText}</span>`;
        }
    }
    
    if (kpis.total_models !== undefined) {
        const element = document.getElementById('total-models-kpi');
        if (element) {
            element.textContent = kpis.total_models;
        }
        
        const changeElement = document.getElementById('models-change');
        if (changeElement && kpis.models_change !== undefined) {
            const change = kpis.models_change;
            const changeText = change >= 0 ? `+${change}` : `${change}`;
            const changeClass = change >= 0 ? 'text-success' : 'text-danger';
            changeElement.innerHTML = `<span class="${changeClass}">${changeText}</span>`;
        }
    }
    
    if (kpis.avg_sales !== undefined) {
        const element = document.getElementById('avg-sales-kpi');
        if (element) {
            element.textContent = formatNumber(kpis.avg_sales);
        }
        
        const changeElement = document.getElementById('avg-change');
        if (changeElement && kpis.avg_change !== undefined) {
            const change = kpis.avg_change;
            const changeText = change >= 0 ? `+${change}%` : `${change}%`;
            const changeClass = change >= 0 ? 'text-success' : 'text-danger';
            changeElement.innerHTML = `<span class="${changeClass}">${changeText}</span>`;
        }
    }
    
    if (kpis.top_model !== undefined) {
        const element = document.getElementById('top-model-kpi');
        if (element) {
            element.textContent = kpis.top_model;
        }
        
        const changeElement = document.getElementById('top-change');
        if (changeElement && kpis.top_sales !== undefined) {
            changeElement.innerHTML = `<span class="text-info">${formatNumber(kpis.top_sales)}</span>`;
        }
    }
}

// Función para actualizar los gráficos del dashboard
function updateDashboardCharts(charts) {
    console.log('DEBUG: Actualizando gráficos del dashboard:', charts);
    
    // Actualizar gráfico de tendencias
    if (trendChart && charts.trend) {
        trendChart.data.labels = charts.trend.labels;
        trendChart.data.datasets[0].data = charts.trend.data;
        trendChart.update();
    }
    
    // Actualizar gráfico de distribución por período
    if (periodDistributionChart && charts.period_distribution) {
        periodDistributionChart.data.labels = charts.period_distribution.labels;
        periodDistributionChart.data.datasets[0].data = charts.period_distribution.data;
        periodDistributionChart.update();
    }
}

// Función para actualizar las alertas del dashboard
function updateDashboardAlerts(alerts) {
    console.log('DEBUG: Actualizando alertas del dashboard:', alerts);
    
    const alertsContainer = document.getElementById('dashboard-alerts');
    if (!alertsContainer) return;
    
    if (!alerts || alerts.length === 0) {
        alertsContainer.innerHTML = `
            <div class="alert alert-success">
                <i class="bi bi-check-circle me-2"></i>
                <strong>Todo en orden:</strong> No hay alertas pendientes.
            </div>
        `;
        return;
    }
    
    let alertsHTML = '';
    alerts.forEach(alert => {
        const alertClass = alert.type || 'info';
        const iconClass = getAlertIcon(alert.type);
        
        alertsHTML += `
            <div class="alert alert-${alertClass}">
                <i class="bi ${iconClass} me-2"></i>
                <strong>${alert.title}:</strong> ${alert.message}
            </div>
        `;
    });
    
    alertsContainer.innerHTML = alertsHTML;
}

// Función para obtener el ícono de alerta
function getAlertIcon(type) {
    const icons = {
        'success': 'bi-check-circle',
        'danger': 'bi-exclamation-triangle',
        'warning': 'bi-exclamation-triangle',
        'info': 'bi-info-circle'
    };
    return icons[type] || 'bi-info-circle';
}

// Función para formatear números
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

// Agregar funciones del dashboard al objeto window
window.refreshDashboard = refreshDashboard;
window.initializeDashboard = initializeDashboard;
window.forceDashboardLoad = forceDashboardLoad;

// Inicializar dashboard cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que todo se cargue
    setTimeout(() => {
        initializeDashboard();
    }, 500);
});

// Variables globales para los nuevos gráficos
let seasonalChart = null;
let forecastChart = null;

// Función para cargar análisis de estacionalidad
async function loadSeasonalAnalysis() {
    console.log('DEBUG: Cargando análisis de estacionalidad...');
    
    try {
        // Mostrar estado de carga
        document.getElementById('seasonal-summary').innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2">Analizando patrones estacionales...</p>
            </div>
        `;
        
        const response = await fetch('/api/seasonal_analysis');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateSeasonalAnalysis(data.seasonal_analysis);
            console.log('DEBUG: Análisis de estacionalidad cargado exitosamente');
        } else {
            throw new Error(data.error || 'Error al cargar análisis de estacionalidad');
        }
    } catch (error) {
        console.error('DEBUG: Error al cargar análisis de estacionalidad:', error);
        document.getElementById('seasonal-summary').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Error: ${error.message}
            </div>
        `;
    }
}

// Función para actualizar el análisis de estacionalidad
function updateSeasonalAnalysis(analysis) {
    // Actualizar gráfico de estacionalidad
    updateSeasonalChart(analysis.seasonal_data);
    
    // Actualizar resumen
    updateSeasonalSummary(analysis);
}

// Función para actualizar el gráfico de estacionalidad
function updateSeasonalChart(seasonalData) {
    const ctx = document.getElementById('seasonalChart');
    if (!ctx) return;
    
    // Destruir gráfico existente si existe
    if (seasonalChart) {
        seasonalChart.destroy();
    }
    
    seasonalChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: seasonalData.labels,
            datasets: [{
                label: 'Índice de Estacionalidad (%)',
                data: seasonalData.seasonal_index,
                backgroundColor: seasonalData.seasonal_index.map(value => {
                    if (value > 110) return 'rgba(220, 53, 69, 0.7)'; // Rojo para alta temporada
                    if (value < 90) return 'rgba(40, 167, 69, 0.7)'; // Verde para baja temporada
                    return 'rgba(108, 117, 125, 0.7)'; // Gris para temporada normal
                }),
                borderColor: seasonalData.seasonal_index.map(value => {
                    if (value > 110) return 'rgba(220, 53, 69, 1)';
                    if (value < 90) return 'rgba(40, 167, 69, 1)';
                    return 'rgba(108, 117, 125, 1)';
                }),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return `Índice: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff',
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    border: {
                        color: 'rgba(255, 255, 255, 0.3)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#ffffff'
                    },
                    border: {
                        color: 'rgba(255, 255, 255, 0.3)'
                    }
                }
            }
        }
    });
}

// Función para actualizar el resumen de estacionalidad
function updateSeasonalSummary(analysis) {
    const summaryDiv = document.getElementById('seasonal-summary');
    
    const highSeasonText = analysis.high_season_months.length > 0 
        ? analysis.high_season_months.join(', ') 
        : 'No identificados';
    
    const lowSeasonText = analysis.low_season_months.length > 0 
        ? analysis.low_season_months.join(', ') 
        : 'No identificados';
    
    const trendDirection = analysis.trend_analysis.trend_direction;
    const trendStrength = analysis.trend_analysis.trend_strength;
    
    summaryDiv.innerHTML = `
        <div class="mb-3">
            <h6 class="text-primary">Temporada Alta</h6>
            <p class="mb-2"><i class="bi bi-arrow-up-circle text-danger"></i> ${highSeasonText}</p>
        </div>
        <div class="mb-3">
            <h6 class="text-success">Temporada Baja</h6>
            <p class="mb-2"><i class="bi bi-arrow-down-circle text-success"></i> ${lowSeasonText}</p>
        </div>
        <div class="mb-3">
            <h6 class="text-info">Tendencia General</h6>
            <p class="mb-2">
                <i class="bi bi-${trendDirection === 'creciente' ? 'arrow-up' : 'arrow-down'}-circle text-${trendDirection === 'creciente' ? 'success' : 'danger'}"></i>
                ${trendDirection.charAt(0).toUpperCase() + trendDirection.slice(1)} (${trendStrength})
            </p>
        </div>
        <div class="mb-3">
            <h6 class="text-warning">Promedio General</h6>
            <p class="mb-2"><i class="bi bi-graph-up"></i> ${formatNumber(analysis.overall_avg)}</p>
        </div>
    `;
}

// Función para cargar predicciones de ventas
async function loadSalesForecast() {
    console.log('DEBUG: Cargando predicciones de ventas...');
    
    try {
        // Mostrar estado de carga
        document.getElementById('forecast-metrics').innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-success" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2">Generando predicciones...</p>
            </div>
        `;
        
        const response = await fetch('/api/sales_forecast');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateSalesForecast(data.forecast);
            console.log('DEBUG: Predicciones de ventas cargadas exitosamente');
        } else {
            throw new Error(data.error || 'Error al cargar predicciones de ventas');
        }
    } catch (error) {
        console.error('DEBUG: Error al cargar predicciones de ventas:', error);
        document.getElementById('forecast-metrics').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Error: ${error.message}
            </div>
        `;
    }
}

// Función para actualizar las predicciones de ventas
function updateSalesForecast(forecast) {
    // Actualizar gráfico de predicciones
    updateForecastChart(forecast);
    
    // Actualizar métricas del modelo
    updateForecastMetrics(forecast.model_metrics);
}

// Función para actualizar el gráfico de predicciones
function updateForecastChart(forecast) {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;
    
    // Destruir gráfico existente si existe
    if (forecastChart) {
        forecastChart.destroy();
    }
    
    // Combinar datos históricos y predicciones
    const allLabels = [...forecast.historical_data.labels, ...forecast.forecast_data.labels];
    const historicalData = forecast.historical_data.data;
    const forecastData = forecast.forecast_data.data;
    const upperBound = forecast.forecast_data.upper_bound;
    const lowerBound = forecast.forecast_data.lower_bound;
    
    // Crear datos para el gráfico
    const historicalDataset = {
        label: 'Datos Históricos',
        data: [...historicalData, ...Array(forecastData.length).fill(null)],
        borderColor: '#007bff',
        backgroundColor: 'rgba(0, 123, 255, 0.1)',
        borderWidth: 2,
        fill: false
    };
    
    const forecastDataset = {
        label: 'Predicciones',
        data: [...Array(historicalData.length).fill(null), ...forecastData],
        borderColor: '#28a745',
        backgroundColor: 'rgba(40, 167, 69, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false
    };
    
    const confidenceDataset = {
        label: 'Intervalo de Confianza',
        data: [...Array(historicalData.length).fill(null), ...upperBound],
        borderColor: 'rgba(40, 167, 69, 0.3)',
        backgroundColor: 'rgba(40, 167, 69, 0.1)',
        borderWidth: 1,
        fill: '+1',
        pointRadius: 0
    };
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [historicalDataset, forecastDataset, confidenceDataset]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#ffffff',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#ffffff',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    },
                    border: {
                        color: 'rgba(255, 255, 255, 0.3)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#ffffff'
                    },
                    border: {
                        color: 'rgba(255, 255, 255, 0.3)'
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Función para actualizar las métricas del modelo de predicción
function updateForecastMetrics(metrics) {
    const metricsContainer = document.getElementById('forecast-metrics');
    if (!metricsContainer) return;
    
    metricsContainer.innerHTML = `
        <div class="row">
            <div class="col-6">
                <div class="metric-item">
                    <h6 class="text-muted">Error Cuadrático Medio (RMSE)</h6>
                    <h4 class="text-primary">${metrics.rmse.toFixed(3)}</h4>
                    <small class="badge bg-success">Excelente</small>
                </div>
            </div>
            <div class="col-6">
                <div class="metric-item">
                    <h6 class="text-muted">Error Absoluto Medio (MAE)</h6>
                    <h4 class="text-info">${metrics.mae.toFixed(2)}</h4>
                    <small class="badge bg-primary">Buena</small>
                </div>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <div class="metric-item">
                    <h6 class="text-muted">Intervalo de Confianza</h6>
                    <h4 class="text-warning">±${(metrics.confidence_interval / 1000).toFixed(1)}K</h4>
                    <small class="text-muted">95% de confianza</small>
                </div>
            </div>
        </div>
    `;
}

// --- FUNCIONES DE ADMINISTRACIÓN ---

// Variables globales para administración
let currentUsers = [];
let currentRoles = [];
let currentActivities = [];
let currentEditUserId = null;

// Función para cargar usuarios
async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const data = await response.json();
        
        if (data.success) {
            currentUsers = data.users;
            updateUsersTable();
        } else {
            console.error('Error al cargar usuarios:', data.error);
        }
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
    }
}

// Función para cargar roles
async function loadRoles() {
    try {
        const response = await fetch('/api/admin/roles');
        const data = await response.json();
        
        if (data.success) {
            currentRoles = data.roles;
            updateRolesSelects();
        } else {
            console.error('Error al cargar roles:', data.error);
        }
    } catch (error) {
        console.error('Error al cargar roles:', error);
    }
}

// Función para cargar actividad
async function loadActivity() {
    try {
        const response = await fetch('/api/admin/activity');
        const data = await response.json();
        
        if (data.success) {
            currentActivities = data.activities;
            updateActivityTable();
        } else {
            console.error('Error al cargar actividad:', data.error);
        }
    } catch (error) {
        console.error('Error al cargar actividad:', error);
    }
}

// Función para actualizar tabla de usuarios
function updateUsersTable() {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;
    
    if (currentUsers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No hay usuarios</td></tr>';
        return;
    }
    
    tbody.innerHTML = currentUsers.map(user => `
        <tr>
            <td>
                <strong>${user.username}</strong>
            </td>
            <td>${user.email}</td>
            <td>${user.full_name}</td>
            <td><span class="badge bg-secondary">${user.role_name}</span></td>
            <td>
                ${user.is_active ? 
                    '<span class="badge bg-success">Activo</span>' : 
                    '<span class="badge bg-danger">Inactivo</span>'
                }
            </td>
            <td>${user.last_login || '<span class="text-muted">Nunca</span>'}</td>
            <td>
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="editUser(${user.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="confirmDeleteUser(${user.id}, '${user.username}')" title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Función para actualizar tabla de actividad
function updateActivityTable() {
    const tbody = document.getElementById('activity-table-body');
    if (!tbody) return;
    
    if (currentActivities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No hay actividad registrada</td></tr>';
        return;
    }
    
    tbody.innerHTML = currentActivities.map(activity => `
        <tr>
            <td>
                <strong>${activity.username}</strong><br>
                <small class="text-muted">${activity.full_name}</small>
            </td>
            <td>
                ${getActionBadge(activity.action)}
            </td>
            <td>
                ${activity.details ? `<small>${activity.details}</small>` : '<span class="text-muted">-</span>'}
            </td>
            <td><code>${activity.ip_address}</code></td>
            <td>${activity.timestamp}</td>
        </tr>
    `).join('');
}

// Función para obtener badge de acción
function getActionBadge(action) {
    const badges = {
        'login': '<span class="badge bg-success">Login</span>',
        'logout': '<span class="badge bg-warning">Logout</span>',
        'user_created': '<span class="badge bg-info">Crear Usuario</span>',
        'user_updated': '<span class="badge bg-primary">Actualizar Usuario</span>',
        'user_deleted': '<span class="badge bg-danger">Eliminar Usuario</span>'
    };
    return badges[action] || `<span class="badge bg-secondary">${action}</span>`;
}

// Función para actualizar selects de roles
function updateRolesSelects() {
    const roleSelects = ['role_id', 'edit_role_id'];
    
    roleSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">Seleccionar rol...</option>' +
                currentRoles.map(role => 
                    `<option value="${role.id}">${role.name} - ${role.description}</option>`
                ).join('');
        }
    });
}

// Función para mostrar modal de crear usuario
function showCreateUserModal() {
    const modal = new bootstrap.Modal(document.getElementById('createUserModal'));
    document.getElementById('createUserForm').reset();
    modal.show();
}

// Función para crear usuario
async function createUser() {
    const form = document.getElementById('createUserForm');
    const formData = new FormData(form);
    
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        role_id: parseInt(formData.get('role_id'))
    };
    
    try {
        const response = await fetch('/api/admin/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('success', data.message);
            bootstrap.Modal.getInstance(document.getElementById('createUserModal')).hide();
            loadUsers();
            loadActivity();
        } else {
            showAlert('error', data.error);
        }
    } catch (error) {
        console.error('Error al crear usuario:', error);
        showAlert('error', 'Error al crear usuario');
    }
}

// Función para editar usuario
function editUser(userId) {
    const user = currentUsers.find(u => u.id === userId);
    if (!user) return;
    
    currentEditUserId = userId;
    
    // Llenar formulario
    document.getElementById('edit_user_id').value = user.id;
    document.getElementById('edit_username').value = user.username;
    document.getElementById('edit_email').value = user.email;
    document.getElementById('edit_first_name').value = user.first_name || '';
    document.getElementById('edit_last_name').value = user.last_name || '';
    document.getElementById('edit_role_id').value = user.role_id;
    document.getElementById('edit_is_active').checked = user.is_active;
    document.getElementById('edit_new_password').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
    modal.show();
}

// Función para actualizar usuario
async function updateUser() {
    const form = document.getElementById('editUserForm');
    const formData = new FormData(form);
    
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        role_id: parseInt(formData.get('role_id')),
        is_active: formData.get('is_active') === 'on',
        new_password: formData.get('new_password') || null
    };
    
    try {
        const response = await fetch(`/api/admin/users/${currentEditUserId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('success', data.message);
            bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
            loadUsers();
            loadActivity();
        } else {
            showAlert('error', data.error);
        }
    } catch (error) {
        console.error('Error al actualizar usuario:', error);
        showAlert('error', 'Error al actualizar usuario');
    }
}

// Función para confirmar eliminación de usuario
function confirmDeleteUser(userId, username) {
    document.getElementById('deleteUsername').textContent = username;
    currentEditUserId = userId;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteUserModal'));
    modal.show();
}

// Función para eliminar usuario
async function deleteUser() {
    try {
        const response = await fetch(`/api/admin/users/${currentEditUserId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('success', data.message);
            bootstrap.Modal.getInstance(document.getElementById('deleteUserModal')).hide();
            loadUsers();
            loadActivity();
        } else {
            showAlert('error', data.error);
        }
    } catch (error) {
        console.error('Error al eliminar usuario:', error);
        showAlert('error', 'Error al eliminar usuario');
    }
}

// Función para cargar datos de administración cuando se muestra la pestaña
function loadAdminData() {
    loadUsers();
    loadRoles();
    loadActivity();
}

// Variable para el ID del usuario actual
const currentUserId = null; // Se establecerá dinámicamente desde el servidor

// Función para mostrar alertas
function showAlert(type, message) {
    // Crear elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Agregar al contenedor de alertas o crear uno si no existe
    let alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.style.position = 'fixed';
        alertContainer.style.top = '20px';
        alertContainer.style.right = '20px';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }
    
    // Agregar la alerta
    alertContainer.appendChild(alertDiv);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}
