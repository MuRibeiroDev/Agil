// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

// Estado da aplicação
const AppState = {
    signatures: {
        cliente: null
    },
    photos: {},
    formData: {},
    currentStep: 1,
    totalSteps: 6
};

// Inicialização principal
function initApp() {
    try {
        // Inicializar componentes
        initDateTime();
        initPhotoHandlers();
        initSignature();
        initFormHandlers();
        initStepNavigation();
        initLucideIcons();
        
        console.log('Sistema inicializado com sucesso!');
        
    } catch (error) {
        console.error('Erro ao inicializar:', error);
        showToast('Erro', 'Erro ao inicializar o sistema', 'error');
    }
}

// Inicializar data e hora atual
function initDateTime() {
    const dataVistoria = document.getElementById('data_vistoria');
    if (dataVistoria) {
        const now = new Date();
        const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
            .toISOString().slice(0, 16);
        dataVistoria.value = localDateTime;
    }
}

// Inicializar handlers de fotos
function initPhotoHandlers() {
    const photoInputs = document.querySelectorAll('input[type="file"]');
    
    photoInputs.forEach(input => {
        input.addEventListener('change', handlePhotoUpload);
    });
}

// Handler para upload de fotos
function handlePhotoUpload(event) {
    const input = event.target;
    const file = input.files[0];
    
    if (!file) return;
    
    // Validar tipo de arquivo
    if (!file.type.startsWith('image/')) {
        showToast('Erro', 'Por favor, selecione apenas imagens', 'error');
        input.value = '';
        return;
    }
    
    // Validar tamanho (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('Erro', 'Imagem muito grande. Máximo 5MB', 'error');
        input.value = '';
        return;
    }
    
    const previewId = input.id.replace('foto_', 'preview_');
    const preview = document.getElementById(previewId);
    
    if (preview) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <span class="photo-success">✓ Foto capturada</span>
            `;
            preview.classList.add('has-image');
            
            // Armazenar no estado
            AppState.photos[input.name] = {
                file: file,
                dataUrl: e.target.result,
                timestamp: new Date().toISOString()
            };
            
            showToast('Foto', 'Foto capturada com sucesso', 'success');
        };
        
        reader.onerror = function() {
            showToast('Erro', 'Erro ao processar a imagem', 'error');
            input.value = '';
        };
        
        reader.readAsDataURL(file);
    }
}

// Inicializar assinatura digital
function initSignature() {
    const canvas = document.getElementById('signature-canvas');
    const clearBtn = document.getElementById('clear-signature');
    
    if (!canvas) {
        console.error('Canvas de assinatura não encontrado');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    
    // Configurar canvas
    function resizeCanvas() {
        const rect = canvas.getBoundingClientRect();
        const devicePixelRatio = window.devicePixelRatio || 1;
        
        // Definir tamanho real do canvas
        canvas.width = rect.width * devicePixelRatio;
        canvas.height = rect.height * devicePixelRatio;
        
        // Escalar o contexto para compensar a alta densidade de pixels
        ctx.scale(devicePixelRatio, devicePixelRatio);
        
        // Configurar estilo do desenho
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.imageSmoothingEnabled = true;
        
        console.log('Canvas redimensionado:', rect.width, 'x', rect.height);
    }
    
    // Configurar canvas inicial
    setTimeout(() => {
        resizeCanvas();
    }, 100);
    
    // Redimensionar canvas quando necessário
    window.addEventListener('resize', resizeCanvas);
    
    // Funções de desenho
    function startDrawing(e) {
        e.preventDefault();
        isDrawing = true;
        const coords = getCoordinates(e);
        lastX = coords[0];
        lastY = coords[1];
        
        // Desenhar um ponto inicial
        ctx.beginPath();
        ctx.arc(lastX, lastY, 1, 0, 2 * Math.PI);
        ctx.fill();
        
        console.log('Iniciou desenho em:', lastX, lastY);
    }
    
    function draw(e) {
        if (!isDrawing) return;
        e.preventDefault();
        
        const [currentX, currentY] = getCoordinates(e);
        
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(currentX, currentY);
        ctx.stroke();
        
        [lastX, lastY] = [currentX, currentY];
    }
    
    function stopDrawing(e) {
        if (isDrawing) {
            e?.preventDefault();
            isDrawing = false;
            // Salvar assinatura
            AppState.signatures.cliente = canvas.toDataURL();
            console.log('Assinatura salva');
        }
    }
    
    function getCoordinates(e) {
        const rect = canvas.getBoundingClientRect();
        const clientX = e.clientX || (e.touches && e.touches[0] && e.touches[0].clientX);
        const clientY = e.clientY || (e.touches && e.touches[0] && e.touches[0].clientY);
        
        if (clientX === undefined || clientY === undefined) {
            console.error('Não foi possível obter coordenadas');
            return [0, 0];
        }
        
        return [
            clientX - rect.left,
            clientY - rect.top
        ];
    }
    
    // Event listeners para mouse
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing);
    
    // Event listeners para touch
    canvas.addEventListener('touchstart', startDrawing, { passive: false });
    canvas.addEventListener('touchmove', draw, { passive: false });
    canvas.addEventListener('touchend', stopDrawing, { passive: false });
    canvas.addEventListener('touchcancel', stopDrawing, { passive: false });
    
    // Limpar assinatura
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            AppState.signatures.cliente = null;
            console.log('Assinatura limpa');
        });
    }
    
    console.log('Sistema de assinatura inicializado');
}

// Inicializar handlers do formulário
function initFormHandlers() {
    const form = document.getElementById('form-vistoria');
    const btnFinalizar = document.getElementById('btn-finalizar');

    if (btnFinalizar) {
        btnFinalizar.addEventListener('click', function(e) {
            e.preventDefault();
            showConfirmModal('Deseja realmente finalizar a vistoria?', async function() {
                if (form) {
                    // Simula submit
                    handleFormSubmit(new Event('submit'));
                }
            });
        });
    }

    // Inicializar campos de entrada automática maiúscula
    initUppercaseInputs();
}

// Inicializar campos de entrada automática maiúscula
function initUppercaseInputs() {
    const uppercaseInputs = document.querySelectorAll('.uppercase-input');
    
    uppercaseInputs.forEach(input => {
        // Converter valor inicial para maiúscula
        if (input.value) {
            input.value = input.value.toUpperCase();
        }
        
        // Verificar se é campo de placa
        const isPlacaField = input.id === 'placa' || input.name === 'placa';
        
        // Adicionar evento para converter durante a digitação
        input.addEventListener('input', function(e) {
            const cursorPosition = e.target.selectionStart;
            let oldValue = e.target.value;
            let newValue = oldValue.toUpperCase();
            
            // Aplicar formatação automática da placa
            if (isPlacaField) {
                newValue = formatPlacaAutomatically(newValue);
            }
            
            e.target.value = newValue;
            
            // Restaurar posição do cursor (ajustar se hífen foi adicionado/removido)
            const positionDiff = newValue.length - oldValue.length;
            const newCursorPosition = cursorPosition + positionDiff;
            e.target.setSelectionRange(newCursorPosition, newCursorPosition);
        });
        
        // Adicionar evento para conversão no paste
        input.addEventListener('paste', function(e) {
            // Pequeno delay para permitir que o paste complete
            setTimeout(() => {
                let newValue = e.target.value.toUpperCase();
                
                // Aplicar formatação automática da placa no paste
                if (isPlacaField) {
                    newValue = formatPlacaAutomatically(newValue);
                }
                
                e.target.value = newValue;
                // Posicionar cursor no final após paste
                e.target.setSelectionRange(newValue.length, newValue.length);
            }, 10);
        });
    });
}

// Função para formatar placa automaticamente
function formatPlacaAutomatically(placa) {
    // Remover hífen existente para analisar o padrão
    const placaLimpa = placa.replace(/-/g, '');
    
    // Limitar a 7 caracteres
    if (placaLimpa.length > 7) {
        return formatPlacaAutomatically(placaLimpa.substring(0, 7));
    }
    
    // Se não tem caracteres suficientes, retornar como está
    if (placaLimpa.length < 4) {
        return placaLimpa;
    }
    
    // Padrão para detectar tipo de placa
    const padraoAntigo = /^[A-Z]{3}[0-9]{4}$/;  // ABC1234
    const padraoMercosul = /^[A-Z]{3}[0-9][A-Z][0-9]{2}$/;  // ABC1D23
    
    // Se já está completa (7 caracteres)
    if (placaLimpa.length === 7) {
        if (padraoAntigo.test(placaLimpa)) {
            // Modelo antigo: sem hífen (conforme solicitado)
            return placaLimpa;
        } else if (padraoMercosul.test(placaLimpa)) {
            // Modelo Mercosul: sem hífen
            return placaLimpa;
        }
    }
    
    // Se tem 6 ou menos caracteres, ainda está sendo digitada
    if (placaLimpa.length <= 6) {
        // Retornar sem formatação até completar
        return placaLimpa;
    }
    
    // Retornar como está se não conseguir detectar o padrão
    return placaLimpa;
}

// Handler do submit do formulário
async function handleFormSubmit(event) {
    event.preventDefault();
    
    try {
        showLoading();
        
        // Validar formulário
        if (!validateForm()) {
            hideLoading();
            return;
        }
        
        // Coletar dados do formulário
        const formData = collectFormData();
        
        // Simular salvamento (substituir por API real)
        await saveVistoria(formData);
        
        showToast('Sucesso', 'Vistoria salva com sucesso!', 'success');
        
        // Limpar formulário após sucesso
        setTimeout(() => {
            clearForm();
        }, 2000);
        
    } catch (error) {
        console.error('Erro ao salvar vistoria:', error);
        showToast('Erro', 'Erro ao salvar vistoria: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Validar formulário
function validateForm() {
    let isValid = true;
    
    // Limpar erros anteriores
    clearValidationErrors();
    
    // Validar campos obrigatórios
    const requiredFields = [
        { id: 'placa', name: 'Placa' },
        { id: 'modelo', name: 'Modelo' },
        { id: 'nome_conferente', name: 'Nome do Conferente' }
    ];
    
    requiredFields.forEach(field => {
        const element = document.getElementById(field.id);
        if (!element || !element.value.trim()) {
            addFieldError(element);
            isValid = false;
        }
    });
    
    // Validar placa
    const placa = document.getElementById('placa');
    if (placa && placa.value && !isValidPlaca(placa.value)) {
        addFieldError(placa);
        isValid = false;
    }
    
    // Validar assinatura (não há campo visual para destacar, mas pode verificar)
    if (!AppState.signatures.cliente) {
        isValid = false;
        // Se estiver no passo 5, destacar de alguma forma
        if (AppState.currentStep === 5) {
            const canvas = document.getElementById('signature-canvas');
            if (canvas) {
                canvas.style.borderColor = 'var(--danger)';
                canvas.style.borderWidth = '3px';
                setTimeout(() => {
                    canvas.style.borderColor = '';
                    canvas.style.borderWidth = '';
                }, 3000);
            }
        }
    }
    
    // Verificar se há pelo menos uma foto (sem validação visual específica)
    const photoCount = Object.keys(AppState.photos).length;
    if (photoCount === 0) {
        isValid = false;
    }
    
    return isValid;
}

// Limpar erros de validação
function clearValidationErrors() {
    const errorElements = document.querySelectorAll('.validation-error');
    errorElements.forEach(element => {
        element.classList.remove('validation-error');
    });
}

// Coletar dados do formulário
function collectFormData() {
    const form = document.getElementById('form-vistoria');
    const formData = new FormData(form);
    
    const data = {
        // Informações do veículo
        veiculo: {},
        // Questionário
        questionario: {},
        // Fotos
        fotos: AppState.photos,
        // Assinatura
        assinatura: AppState.signatures.cliente,
        // Metadata
        metadata: {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        }
    };
    
    // Processar campos do formulário
    for (let [key, value] of formData.entries()) {
        if (key.startsWith('foto_') || key.startsWith('desc_') || key.startsWith('marca_')) {
            // Já processado nas fotos
            continue;
        }
        
        // Categorizar dados
        if (['placa', 'modelo', 'cor', 'ano'].includes(key)) {
            data.veiculo[key] = value;
        } else if (key === 'nome_conferente' || key === 'data_vistoria') {
            data[key] = value;
        } else {
            // Questionário (checkboxes)
            data.questionario[key] = formData.has(key);
        }
    }
    
    return data;
}

// Simular salvamento da vistoria
async function saveVistoria(data) {
    // Simular delay de rede
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Aqui você faria a chamada real para a API
    console.log('Dados da vistoria:', data);
    
    // Simular possível erro (descomente para testar)
    // throw new Error('Erro simulado de rede');
    
    return { success: true, id: 'VIST-' + Date.now() };
}

// Limpar formulário
function clearForm() {
    // Limpar campos do formulário
    const form = document.getElementById('form-vistoria');
    if (form) {
        form.reset();
    }
    // Limpar previews de fotos
    const previews = document.querySelectorAll('.photo-preview');
    previews.forEach(preview => {
        preview.innerHTML = `
            <i data-lucide="camera-off"></i>
            <span>Toque para fotografar</span>
        `;
        preview.classList.remove('has-image');
    });
    // Limpar assinatura
    const canvas = document.getElementById('signature-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    // Limpar estado
    AppState.photos = {};
    AppState.signatures.cliente = null;
    // Resetar data/hora
    initDateTime();
    // Reinicializar ícones
    initLucideIcons();
}

// Modal de confirmação - Versão simplificada e corrigida
function showConfirmModal(message, onConfirm) {
    const modal = document.getElementById('modal-confirm');
    const msg = document.getElementById('modal-message');
    const btnConfirm = document.getElementById('modal-confirm-btn');
    const btnCancel = document.getElementById('modal-cancel-btn');
    const overlay = modal?.querySelector('.modal-overlay');
    
    if (!modal || !msg || !btnConfirm || !btnCancel) {
        console.error('Modal elements not found');
        return;
    }
    
    // Garantir que o modal está anexado ao body
    if (modal.parentElement !== document.body) {
        document.body.appendChild(modal);
    }
    
    // Forçar estilos inline para garantir que apareça por cima
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.right = '0';
    modal.style.bottom = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.zIndex = '999999';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.padding = '20px';
    modal.style.boxSizing = 'border-box';
    
    // Definir mensagem
    msg.textContent = message;
    
    // Mostrar modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    
    // Limpar event listeners anteriores
    const newBtnConfirm = btnConfirm.cloneNode(true);
    const newBtnCancel = btnCancel.cloneNode(true);
    btnConfirm.parentNode.replaceChild(newBtnConfirm, btnConfirm);
    btnCancel.parentNode.replaceChild(newBtnCancel, btnCancel);
    
    function closeModal() {
        // Iniciar animação de fechamento
        modal.classList.add('hidden');
        
        // Aguardar animação terminar antes de restaurar scroll e limpar estilos
        setTimeout(() => {
            document.body.style.overflow = '';
            // Limpar estilos inline após fechar
            modal.style.cssText = '';
        }, 400); // 400ms para coincidir com a duração da animação CSS
    }
    
    // Event listeners
    newBtnConfirm.addEventListener('click', function() {
        closeModal();
        if (typeof onConfirm === 'function') {
            setTimeout(onConfirm, 100);
        }
    });
    
    newBtnCancel.addEventListener('click', function() {
        closeModal();
    });
    
    // Fechar clicando no overlay
    if (overlay) {
        const newOverlay = overlay.cloneNode(true);
        overlay.parentNode.replaceChild(newOverlay, overlay);
        newOverlay.addEventListener('click', function() {
            closeModal();
        });
    }
    
    // Fechar com ESC
    const escapeHandler = function(e) {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
    
    // Focar no botão cancelar
    setTimeout(() => {
        newBtnCancel.focus();
    }, 100);
}

// Inicializar ícones Lucide
function initLucideIcons() {
    if (window.lucide) {
        lucide.createIcons();
    }
}

// Sistema de Toast
function showToast(title, message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
    `;
    
    container.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remover
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// Loading
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.remove('hidden');
    }
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.add('hidden');
    }
}

// Tratamento de erros globais
window.addEventListener('error', function(event) {
    console.error('Erro global:', event.error);
    showToast('Erro', 'Ocorreu um erro inesperado', 'error');
});

// Service Worker (para futuro uso offline)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // navigator.serviceWorker.register('/sw.js');
    });
}

// Adicionar estilo de erro para validação
const style = document.createElement('style');
style.textContent = `
    .input.error, .textarea.error {
        border-color: var(--danger) !important;
        box-shadow: 0 0 0 3px rgb(220 38 38 / 0.1) !important;
    }
`;
document.head.appendChild(style);

// ========================
// SISTEMA DE NAVEGAÇÃO POR PASSOS
// ========================

// Inicializar navegação por passos
function initStepNavigation() {
    const btnProximo = document.getElementById('btn-proximo');
    const btnAnterior = document.getElementById('btn-anterior');
    
    if (btnProximo) {
        btnProximo.addEventListener('click', nextStep);
    }
    
    if (btnAnterior) {
        btnAnterior.addEventListener('click', previousStep);
    }
    
    // Mostrar primeiro passo
    showStep(1);
}

// Mostrar passo específico
function showStep(stepNumber) {
    // Ocultar todos os passos
    for (let i = 1; i <= AppState.totalSteps; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) {
            step.classList.add('hidden');
        }
        
        // Atualizar indicador de progresso
        const progressStep = document.querySelector(`[data-step="${i}"]`);
        if (progressStep) {
            progressStep.classList.remove('active', 'completed');
            if (i < stepNumber) {
                progressStep.classList.add('completed');
            } else if (i === stepNumber) {
                progressStep.classList.add('active');
            }
        }
    }
    
    // Mostrar passo atual
    const currentStep = document.getElementById(`step-${stepNumber}`);
    if (currentStep) {
        currentStep.classList.remove('hidden');
    }
    
    // Atualizar estado
    AppState.currentStep = stepNumber;
    
    // Preencher dados da revisão se for o passo 5
    if (stepNumber === 5) {
        populateReviewData();
    }
    
    // Re-inicializar assinatura se for o passo 6
    if (stepNumber === 6) {
        setTimeout(() => {
            initSignature();
        }, 200); // Pequeno delay para garantir que o canvas está visível
    }
    
    // Scroll suave para o topo
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    
    // Atualizar botões de navegação
    updateNavigationButtons();
}

// Atualizar botões de navegação
function updateNavigationButtons() {
    const btnProximo = document.getElementById('btn-proximo');
    const btnAnterior = document.getElementById('btn-anterior');
    const finalActions = document.getElementById('final-actions');
    const stepNavigation = document.querySelector('.step-navigation');
    
    console.log('Atualizando navegação - Passo atual:', AppState.currentStep, 'Total de passos:', AppState.totalSteps);
    console.log('Elementos encontrados:', {
        btnProximo: !!btnProximo,
        btnAnterior: !!btnAnterior,
        finalActions: !!finalActions,
        stepNavigation: !!stepNavigation
    });
    
    // Botão Anterior - sempre visível exceto no primeiro passo
    if (btnAnterior) {
        if (AppState.currentStep === 1) {
            btnAnterior.classList.add('hidden');
        } else {
            btnAnterior.classList.remove('hidden');
        }
    }
    
    // Botão Próximo e Ações Finais
    if (AppState.currentStep === AppState.totalSteps) {
        console.log('Último passo - transformando botão próximo em finalizar');
        // Último passo - transformar botão próximo em finalizar
        if (btnProximo) {
            btnProximo.innerHTML = '<span>Finalizar Vistoria</span>';
            btnProximo.classList.remove('hidden');
            btnProximo.classList.remove('button-primary');
            btnProximo.classList.add('button-success');
            
            // Limpar todos os event listeners
            const newBtn = btnProximo.cloneNode(true);
            btnProximo.parentNode.replaceChild(newBtn, btnProximo);
            
            // Adicionar event listener para finalizar
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showConfirmModal('Deseja realmente finalizar a vistoria?', async function() {
                    const form = document.getElementById('form-vistoria');
                    if (form) {
                        handleFormSubmit(new Event('submit'));
                    }
                });
            });
        }
        // Esconder ações finais pois agora usamos a navegação principal
        if (finalActions) finalActions.classList.add('hidden');
        if (stepNavigation) stepNavigation.classList.remove('hidden');
    } else {
        console.log('Passo intermediário - restaurando botão próximo');
        // Passos intermediários - restaurar botão próximo normal
        if (btnProximo) {
            btnProximo.innerHTML = '<span>Avançar</span><span class="button-icon">→</span>';
            btnProximo.classList.remove('hidden');
            btnProximo.classList.remove('button-success');
            btnProximo.classList.add('button-primary');
            
            // Limpar todos os event listeners
            const newBtn = btnProximo.cloneNode(true);
            btnProximo.parentNode.replaceChild(newBtn, btnProximo);
            
            // Adicionar event listener para próximo passo
            newBtn.addEventListener('click', nextStep);
        }
        if (stepNavigation) stepNavigation.classList.remove('hidden');
        if (finalActions) finalActions.classList.add('hidden');
    }
}

// Ir para próximo passo
function nextStep() {
    if (validateCurrentStep()) {
        if (AppState.currentStep < AppState.totalSteps) {
            showStep(AppState.currentStep + 1);
        }
    }
}

// Ir para passo anterior
function previousStep() {
    if (AppState.currentStep > 1) {
        showStep(AppState.currentStep - 1);
    }
}

// Validar passo atual antes de avançar
function validateCurrentStep() {
    const currentStep = AppState.currentStep;
    
    switch (currentStep) {
        case 1: // Informações do Veículo
            return validateVehicleInfo();
        case 2: // Questionário
            return true; // Questionário é opcional
        case 3: // Fotos
            return true; // Fotos serão validadas no final
        case 4: // Conferente
            return validateConferente();
        case 5: // Assinatura
            return true; // Será validada no final
        default:
            return true;
    }
}

// Validar informações do veículo
function validateVehicleInfo() {
    const placa = document.getElementById('placa');
    const modelo = document.getElementById('modelo');
    
    let isValid = true;
    
    // Limpar erros visuais anteriores
    clearFieldErrors([placa, modelo]);
    
    // Validar placa
    if (!placa || !placa.value.trim()) {
        addFieldError(placa);
        isValid = false;
    } else if (!isValidPlaca(placa.value)) {
        addFieldError(placa);
        isValid = false;
    }
    
    // Validar modelo
    if (!modelo || !modelo.value.trim()) {
        addFieldError(modelo);
        isValid = false;
    }
    
    return isValid;
}

// Validar informações do conferente
function validateConferente() {
    const nomeConferente = document.getElementById('nome_conferente');
    
    // Limpar erros visuais anteriores
    clearFieldErrors([nomeConferente]);
    
    if (!nomeConferente || !nomeConferente.value.trim()) {
        addFieldError(nomeConferente);
        return false;
    }
    
    return true;
}

// Adicionar erro visual ao campo
function addFieldError(field) {
    if (field) {
        field.classList.add('validation-error');
        
        // Remover erro quando o usuário começar a digitar
        const removeError = () => {
            field.classList.remove('validation-error');
            field.removeEventListener('input', removeError);
            field.removeEventListener('change', removeError);
        };
        
        field.addEventListener('input', removeError);
        field.addEventListener('change', removeError);
    }
}

// Limpar erros visuais de múltiplos campos
function clearFieldErrors(fields) {
    fields.forEach(field => {
        if (field) {
            field.classList.remove('validation-error');
        }
    });
}

// Preencher dados da revisão
function populateReviewData() {
    // Dados do veículo
    document.getElementById('review-placa').textContent = document.getElementById('placa').value || '-';
    document.getElementById('review-modelo').textContent = document.getElementById('modelo').value || '-';
    document.getElementById('review-cor').textContent = document.getElementById('cor').value || '-';
    document.getElementById('review-ano').textContent = document.getElementById('ano').value || '-';
    
    // Questionário
    const questionsContainer = document.getElementById('review-questions');
    questionsContainer.innerHTML = '';
    
    const questions = [
        { name: 'ar_condicionado', text: 'Tem ar condicionado?' },
        { name: 'antenas', text: 'Antenas?' },
        { name: 'tapetes', text: 'Tapetes?' },
        { name: 'tapete_porta_malas', text: 'Tapete porta malas?' },
        { name: 'bateria', text: 'Bateria?' },
        { name: 'retrovisor_direito', text: 'Retrovisor direito?' },
        { name: 'retrovisor_esquerdo', text: 'Retrovisor esquerdo?' },
        { name: 'extintor', text: 'Extintor?' },
        { name: 'roda_comum', text: 'Roda comum?' },
        { name: 'roda_especial', text: 'Roda especial?' },
        { name: 'chave_principal', text: 'Chave principal?' },
        { name: 'chave_reserva', text: 'Chave reserva?' },
        { name: 'manual', text: 'Manual?' },
        { name: 'documento', text: 'Documento?' },
        { name: 'nota_fiscal', text: 'Nota fiscal?' },
        { name: 'limpador_dianteiro', text: 'Limpador pára-brisa dianteiro?' },
        { name: 'limpador_traseiro', text: 'Limpador pára-brisa traseiro?' },
        { name: 'triangulo', text: 'Triângulo?' },
        { name: 'macaco', text: 'Macaco?' },
        { name: 'chave_roda', text: 'Chave de roda?' },
        { name: 'pneu_step', text: 'Pneu step?' }
    ];
    
    questions.forEach(question => {
        const element = document.querySelector(`input[name="${question.name}"]`);
        const isChecked = element ? element.checked : false;
        const answer = '';  // Sem texto, apenas a cor da bolinha
        const answerClass = isChecked ? 'sim' : 'nao';
        
        const questionDiv = document.createElement('div');
        questionDiv.className = 'review-question';
        
        questionDiv.innerHTML = `
            <span class="review-question-text">${question.text}</span>
            <span class="review-question-answer ${answerClass}">${answer}</span>
        `;
        
        questionsContainer.appendChild(questionDiv);
    });
    
    // Fotos
    const photosContainer = document.getElementById('review-photos');
    photosContainer.innerHTML = '';
    
    if (AppState.uploadedPhotos && AppState.uploadedPhotos.length > 0) {
        AppState.uploadedPhotos.forEach((photo, index) => {
            const photoDiv = document.createElement('div');
            photoDiv.className = 'review-photo';
            
            const img = document.createElement('img');
            img.src = photo.url || photo.src;
            img.alt = `Foto ${index + 1}`;
            
            photoDiv.appendChild(img);
            photosContainer.appendChild(photoDiv);
        });
    } else {
        photosContainer.innerHTML = '<p class="review-no-photos">Nenhuma foto adicionada</p>';
    }
    
    // Dados do conferente
    document.getElementById('review-conferente').textContent = document.getElementById('nome_conferente').value || '-';
    
    // Data e hora
    const dataVistoria = document.getElementById('data_vistoria').value;
    if (dataVistoria) {
        const date = new Date(dataVistoria);
        const formatted = date.toLocaleString('pt-BR');
        document.getElementById('review-data').textContent = formatted;
    } else {
        document.getElementById('review-data').textContent = '-';
    }
}

// ========================
// VALIDAÇÃO DE PLACA
// ========================

// Validar placa (formato antigo e Mercosul)
function isValidPlaca(placa) {
    if (!placa || typeof placa !== 'string') {
        return false;
    }
    
    // Remover espaços e converter para maiúsculo
    const placaLimpa = placa.trim().toUpperCase();
    
    // Formato antigo: ABC-1234 ou ABC1234 (3 letras + hífen opcional + 4 números)
    const formatoAntigo = /^[A-Z]{3}-?[0-9]{4}$/;
    
    // Formato Mercosul: ABC1D23 (3 letras + 1 número + 1 letra + 2 números)
    const formatoMercosul = /^[A-Z]{3}[0-9][A-Z][0-9]{2}$/;
    
    return formatoAntigo.test(placaLimpa) || formatoMercosul.test(placaLimpa);
}
