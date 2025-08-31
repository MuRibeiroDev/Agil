// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM carregado, inicializando aplicação...');
    
    // Verificar se elementos essenciais existem
    setTimeout(() => {
        const documentInput = document.getElementById('documento_nota_fiscal');
        const documentPreview = document.getElementById('preview_documento');
        
        console.log('🔍 Verificação de elementos:');
        console.log('   - Input documento:', !!documentInput, documentInput);
        console.log('   - Preview documento:', !!documentPreview, documentPreview);
    }, 100);
    
    initApp();
});

// Estado da aplicação
const AppState = {
    signatures: {
        cliente: null
    },
    photos: {},
    uploadedPhotos: [],
    documentFile: null,  // Arquivo do documento
    documentData: null,  // Dados processados do documento
    formData: {},
    currentStep: 1,
    totalSteps: 6
};

// Utilitários de performance para mobile
const PerformanceUtils = {
    // Debounce para reduzir chamadas de função
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle para limitar frequência de execução
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Verificar se é dispositivo móvel
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               (window.innerWidth <= 768);
    },
    
    // Otimizar eventos de toque
    addTouchOptimizedEvent(element, eventType, handler) {
        if (this.isMobile()) {
            // Para mobile, usar touchstart para resposta mais rápida
            if (eventType === 'click') {
                element.addEventListener('touchstart', handler, { passive: true });
                return;
            }
        }
        element.addEventListener(eventType, handler);
    }
};

// Inicialização principal
function initApp() {
    try {
        // Inicializar componentes
        initDateTime();
        initPhotoHandlers(); // Agora inclui documentos também
        initSignature();
        initRemoteSignature();
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
    // Incluir TODOS os inputs de arquivo, incluindo documento
    const photoInputs = document.querySelectorAll('input[type="file"]');
    
    photoInputs.forEach(input => {
        // Se for documento, usar handler específico
        if (input.id === 'documento_nota_fiscal') {
            input.addEventListener('change', handleDocumentUpload);
        } else {
            input.addEventListener('change', handlePhotoUpload);
        }
        
        // Adicionar clique ao preview correspondente
        let previewId;
        if (input.id === 'documento_nota_fiscal') {
            previewId = 'preview_documento';
        } else {
            previewId = input.id.replace('foto_', 'preview_');
        }
        
        const preview = document.getElementById(previewId);
        
        if (preview) {
            preview.addEventListener('click', function() {
                input.click();
            });
            
            // Adicionar estilo de cursor pointer
            preview.style.cursor = 'pointer';
        }
    });
}

// Inicializar handler para documentos (estilo foto)
function initDocumentHandler() {
    console.log('🔧 Inicializando handler de documentos...');
    
    const documentInput = document.getElementById('documento_nota_fiscal');
    const documentPreview = document.getElementById('preview_documento');
    const uploadButton = document.getElementById('btn_upload_documento');
    
    console.log('📄 Input:', documentInput);
    console.log('🖼️ Preview:', documentPreview);
    console.log('🔘 Button:', uploadButton);
    
    // Detectar se é desktop (múltiplas verificações)
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    const isLargeScreen = window.innerWidth > 768;
    const isDesktop = !isTouchDevice && isLargeScreen;
    
    console.log('� Touch device?', isTouchDevice);
    console.log('🖥️ Large screen?', isLargeScreen);
    console.log('�💻 É desktop?', isDesktop);
    
    if (documentInput) {
        console.log('✅ Input encontrado, configurando eventos...');
        
        // Evento de mudança no input (principal funcionalidade)
        documentInput.addEventListener('change', handleDocumentUpload);
        
        // Debug: listener para verificar cliques
        documentInput.addEventListener('click', function(e) {
            console.log('🖱️ Click no input detectado');
        });
        
        console.log('✅ Eventos configurados - usando labels nativos!');
    } else {
        console.error('❌ Input não encontrado!');
    }
}

// Handler para upload de documentos (baseado no de fotos)
async function handleDocumentUpload(event) {
    console.log('📁 Iniciando upload de documento...');
    const input = event.target;
    const file = input.files[0];
    
    if (!file) return;
    
    console.log('📄 Arquivo selecionado:', file);
    
    // Validar tipo de arquivo
    const allowedTypes = [
        'application/pdf',
        'image/jpeg', 'image/jpg', 'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    
    console.log('🔍 Tipo do arquivo:', file.type);
    
    if (!allowedTypes.includes(file.type)) {
        notifications.error('Arquivo inválido', 'Por favor, selecione apenas PDF, imagens ou documentos Word.');
        input.value = '';
        return;
    }
    
    // Validar tamanho (máximo 10MB)
    console.log('📏 Tamanho do arquivo:', file.size, 'bytes');
    if (file.size > 10 * 1024 * 1024) {
        notifications.error('Arquivo muito grande', 'Documento deve ter no máximo 10MB.');
        input.value = '';
        return;
    }
    
    const preview = document.getElementById('preview_documento');
    
    if (preview) {
        // Mostrar indicador de processamento
        preview.innerHTML = `
            <div class="photo-processing">
                <div class="spinner"></div>
                <span>Processando documento...</span>
            </div>
        `;
        
        try {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                let icon = '📄';
                let displayContent = '';
                
                if (file.type.includes('pdf')) {
                    icon = '📕';
                    displayContent = `<div class="document-icon-large">${icon}</div>`;
                } else if (file.type.includes('image')) {
                    icon = '🖼️';
                    // Para imagens, mostrar preview igual às fotos
                    displayContent = `<img src="${e.target.result}" alt="Preview" style="cursor: pointer;" onclick="openPhotoModal('${e.target.result}', 'Preview do documento')">`;
                } else if (file.type.includes('word')) {
                    icon = '📝';
                    displayContent = `<div class="document-icon-large">${icon}</div>`;
                }
                
                preview.innerHTML = `
                    ${displayContent}
                    <button type="button" class="photo-remove" onclick="removeDocument()">×</button>
                    <span class="photo-success">✓ Documento selecionado</span>
                    <div class="document-info-overlay">
                        <div class="document-name">${fileName}</div>
                        <div class="document-size">${fileSize} MB</div>
                    </div>
                `;
                preview.classList.add('has-image'); // Usar a mesma classe das fotos
                
                // Salvar documento separadamente das fotos
                const documentData = {
                    file: file,
                    url: e.target.result,
                    name: 'documento_nota_fiscal',
                    timestamp: new Date().toISOString(),
                    fileName: fileName,
                    fileSize: file.size,
                    fileType: file.type
                };
                
                // NÃO adicionar ao AppState.photos para evitar processamento como foto
                // AppState.photos['documento_nota_fiscal'] = documentData;
                AppState.documentFile = file;
                AppState.documentData = documentData;
                
                console.log('💾 Documento salvo no AppState:', documentData);
                
                notifications.success('Documento selecionado', `${fileName} adicionado com sucesso.`);
            };
            
            reader.onerror = function() {
                notifications.error('Erro no processamento', 'Não foi possível processar o documento. Tente novamente.');
                input.value = '';
                resetDocumentPreview(preview);
            };
            
            reader.readAsDataURL(file);
            
        } catch (error) {
            console.error('Erro ao processar documento:', error);
            notifications.error('Erro no processamento', 'Erro ao processar o documento. Tente novamente.');
            input.value = '';
            resetDocumentPreview(preview);
        }
    }
}

// Resetar preview do documento
function resetDocumentPreview(preview) {
    preview.innerHTML = '📄 Toque para selecionar documento';
    preview.classList.remove('has-image');
}

// Remover documento selecionado
function removeDocument() {
    console.log('🗑️ Removendo documento...');
    
    const documentInput = document.getElementById('documento_nota_fiscal');
    const documentPreview = document.getElementById('preview_documento');
    
    if (documentInput) {
        documentInput.value = '';
        console.log('✅ Input limpo');
    }
    
    if (documentPreview) {
        resetDocumentPreview(documentPreview);
        console.log('✅ Preview resetado');
    }
    
    // Limpar do AppState (tanto no formato antigo quanto no novo)
    AppState.documentFile = null;
    AppState.documentData = null;
    if (AppState.photos && AppState.photos['documento_nota_fiscal']) {
        delete AppState.photos['documento_nota_fiscal'];
    }
    
    console.log('✅ AppState limpo:', AppState.documentFile);
    
    notifications.info('Documento removido', 'Nenhum documento selecionado.');
}

// Handler para upload de fotos
// Otimizar processamento de fotos para mobile
async function handlePhotoUpload(event) {
    const input = event.target;
    const file = input.files[0];
    
    if (!file) return;
    
    // Validar tipo de arquivo
    if (!file.type.startsWith('image/')) {
        notifications.error('Erro', 'Por favor, selecione apenas imagens');
        input.value = '';
        return;
    }
    
    // Limite reduzido para mobile: 50MB
    const maxSizeMB = PerformanceUtils.isMobile() ? 50 : 700;
    if (file.size > maxSizeMB * 1024 * 1024) {
        notifications.error('Arquivo muito grande', `Imagem deve ter no máximo ${maxSizeMB}MB. Tente comprimir a imagem antes de enviar.`);
        input.value = '';
        return;
    }
    
    const previewId = input.id.replace('foto_', 'preview_');
    const preview = document.getElementById(previewId);
    
    if (preview) {
        // Mostrar indicador de processamento
        preview.innerHTML = `
            <div class="photo-processing">
                <div class="spinner"></div>
                <span>Processando foto...</span>
            </div>
        `;
        
        try {
            // Comprimir imagem se for muito grande (otimização mobile)
            const processedFile = await optimizeImageForMobile(file);
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const photoData = {
                    file: processedFile,
                    url: e.target.result,
                    name: input.name,
                    timestamp: new Date().toISOString()
                };
                
                preview.innerHTML = `
                    <img src="${e.target.result}" alt="Preview" style="cursor: pointer;" onclick="openPhotoModal('${e.target.result}', 'Preview da foto')">
                    <button type="button" class="photo-remove" onclick="removePhoto('${input.name}', '${previewId}')">×</button>
                    <span class="photo-success">✓ Foto capturada</span>
                `;
                preview.classList.add('has-image');
                
                // Armazenar no estado (tanto no formato antigo quanto no novo)
                AppState.photos[input.name] = photoData;
                
                // Adicionar ao array uploadedPhotos se não existir (com verificação de segurança)
                if (!AppState.uploadedPhotos || !Array.isArray(AppState.uploadedPhotos)) {
                    AppState.uploadedPhotos = [];
                }
                
                const existingIndex = AppState.uploadedPhotos.findIndex(p => p.name === input.name);
                if (existingIndex >= 0) {
                    AppState.uploadedPhotos[existingIndex] = photoData;
                } else {
                    AppState.uploadedPhotos.push(photoData);
                }
            };
            
            reader.onerror = function() {
                notifications.error('Erro no processamento', 'Não foi possível processar a imagem. Tente novamente com outra imagem.');
                input.value = '';
                resetPhotoPreview(preview);
            };
            
            reader.readAsDataURL(processedFile);
            
        } catch (error) {
            console.error('Erro ao otimizar imagem:', error);
            notifications.error('Erro no processamento', 'Erro ao processar a imagem. Tente novamente.');
            input.value = '';
            resetPhotoPreview(preview);
        }
    }
}

// Otimização de imagem para dispositivos móveis
async function optimizeImageForMobile(file) {
    return new Promise((resolve) => {
        // Se a imagem é pequena o suficiente, não otimizar
        if (file.size < 1024 * 1024) { // Menor que 1MB
            resolve(file);
            return;
        }
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = function() {
            // Calcular dimensões otimizadas para mobile
            let { width, height } = calculateOptimalDimensions(img.width, img.height);
            
            canvas.width = width;
            canvas.height = height;
            
            // Desenhar imagem redimensionada
            ctx.drawImage(img, 0, 0, width, height);
            
            // Converter para blob com qualidade otimizada
            canvas.toBlob((blob) => {
                resolve(blob || file);
            }, 'image/jpeg', 0.8); // 80% de qualidade
        };
        
        img.onerror = () => resolve(file);
        img.src = URL.createObjectURL(file);
    });
}

function calculateOptimalDimensions(originalWidth, originalHeight) {
    const MAX_WIDTH = PerformanceUtils.isMobile() ? 1280 : 1920;
    const MAX_HEIGHT = PerformanceUtils.isMobile() ? 1280 : 1920;
    
    let width = originalWidth;
    let height = originalHeight;
    
    // Redimensionar se necessário
    if (width > MAX_WIDTH) {
        height = (height * MAX_WIDTH) / width;
        width = MAX_WIDTH;
    }
    
    if (height > MAX_HEIGHT) {
        width = (width * MAX_HEIGHT) / height;
        height = MAX_HEIGHT;
    }
    
    return { width: Math.round(width), height: Math.round(height) };
}

function resetPhotoPreview(preview) {
    preview.innerHTML = `
        <i data-lucide="camera-off"></i>
        <span>Toque para fotografar</span>
    `;
    preview.classList.remove('has-image');
    loadLucideIcons();
}

// Função para remover foto
function removePhoto(photoName, previewId) {
    // Remover do estado
    delete AppState.photos[photoName];
    
    // Remover do array uploadedPhotos (com verificação de segurança)
    if (AppState.uploadedPhotos && Array.isArray(AppState.uploadedPhotos)) {
        AppState.uploadedPhotos = AppState.uploadedPhotos.filter(p => p.name !== photoName);
    }
    
    // Restaurar preview
    const preview = document.getElementById(previewId);
    if (preview) {
        preview.innerHTML = '📸 Toque para fotografar';
        preview.classList.remove('has-image');
    }
    
    // Limpar input - buscar pelo name
    const input = document.querySelector(`input[name="${photoName}"]`);
    if (input) {
        input.value = '';
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

// Inicializar sistema de assinatura remota
function initRemoteSignature() {
    const generateLinkBtn = document.getElementById('generate-signature-link');
    
    if (generateLinkBtn) {
        generateLinkBtn.addEventListener('click', generateSignatureLink);
    }
}

// Gerar link de assinatura para o cliente
async function generateSignatureLink() {
    try {
        // Validar campos obrigatórios antes de gerar link
        if (!validateBasicFields()) {
        notifications.warning('Atenção', 'Preencha os campos obrigatórios: Placa, Modelo e Nome do Conferente');
            return;
        }
        
        showLoading();
        
        // Coletar dados da vistoria atual (sem assinatura)
        const vistoriaData = collectVistoriaData();
        
        // Enviar para o servidor para gerar token e salvar vistoria
        const response = await fetch('/api/gerar_link_assinatura', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(vistoriaData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            const link = `${window.location.origin}/assinatura_cliente?token=${result.token}`;
            
            // Mostrar modal de sucesso
            showSuccessModal(result, link, vistoriaData);
            
        } else {
            showToast('Erro', result.message || 'Erro ao gerar link', 'error');
        }
    } catch (error) {
        console.error('Erro ao gerar link:', error);
        showToast('Erro', 'Erro de conexão ao gerar link', 'error');
    } finally {
        hideLoading();
    }
}

// Coletar dados da vistoria para envio (sem assinatura)
function collectVistoriaData() {
    const form = document.getElementById('form-vistoria');
    
    const data = {
        // Informações do veículo
        veiculo: {},
        // Questionário
        questionario: {},
        // Dados dos pneus
        pneus: {},
        // Fotos
        fotos: AppState.photos,
        // SEM assinatura para link remoto
        assinatura: null,
        // Metadata
        metadata: {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        }
    };
    
    // Coletar dados dos inputs do formulário
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        const name = input.name || input.id;
        if (!name) return;
        
        if (input.type === 'checkbox') {
            // Para checkboxes, verificar se está marcado
            data.questionario[name] = input.checked;
        } else if (input.type === 'radio') {
            // Para radio buttons, só adicionar se estiver selecionado
            if (input.checked) {
                if (['placa', 'modelo', 'cor', 'ano'].includes(name)) {
                    data.veiculo[name] = input.value;
                } else {
                    data[name] = input.value;
                }
            }
        } else if (input.type === 'file') {
            // Arquivos já estão em AppState.photos
            return;
        } else {
            // Input normal (text, select, textarea, etc.)
            const value = input.value.trim();
            
            // Tratamento especial para campos de observação (sempre incluir, mesmo se vazio)
            if (name.startsWith('desc_obs_')) {
                data[name] = value;
            } else if (value) {
                if (['placa', 'modelo', 'cor', 'ano'].includes(name)) {
                    data.veiculo[name] = value;
                } else {
                    if (name.startsWith("marca_pneu_")) { 
                        data.pneus[name] = value; 
                    } else { 
                        data[name] = value; 
                    }
                }
            }
        }
    });
    
    // Garantir que campos obrigatórios existam
    if (!data.veiculo.placa) data.veiculo.placa = '';
    if (!data.veiculo.modelo) data.veiculo.modelo = '';
    if (!data.veiculo.cor) data.veiculo.cor = '';
    if (!data.veiculo.ano) data.veiculo.ano = '';
    if (!data.nome_conferente) data.nome_conferente = '';
    if (!data.data_vistoria) data.data_vistoria = new Date().toISOString();
    
    console.log('Dados coletados para link:', data);
    return data;
}

// Inicializar handlers do formulário com otimização mobile
function initFormHandlers() {
    const form = document.getElementById('form-vistoria');
    const btnFinalizar = document.getElementById('btn-finalizar');

    if (btnFinalizar) {
        // Usar evento otimizado para mobile
        PerformanceUtils.addTouchOptimizedEvent(btnFinalizar, 'click', function(e) {
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
        const formData = await collectFormData();
        
        // Salvar vistoria (incluindo assinatura se presente)
        const result = await saveVistoria(formData);
        
        if (result.success) {
            notifications.success('Sucesso', 'Vistoria e assinatura salvadas com sucesso!');
            
            // Voltar para a tela inicial imediatamente
            clearForm();
            showStep(1);
            notifications.info('Info', 'Sistema reiniciado. Você pode iniciar uma nova vistoria.');
        } else {
            throw new Error(result.message || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('Erro ao salvar vistoria:', error);
        showToast('Erro', 'Erro ao salvar vistoria: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Validar apenas campos básicos (sem assinatura)
function validateBasicFields() {
    let isValid = true;
    
    // Limpar erros anteriores
    clearValidationErrors();
    
    // Validar campos obrigatórios básicos
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
    
    return isValid;
}

// Validar formulário completo (incluindo assinatura)
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
    
    // Validar assinatura
    if (!AppState.signatures.cliente) {
        isValid = false;
        showToast('Atenção', 'Assinatura é obrigatória para finalizar a vistoria', 'warning');
        
        // Se estiver no passo 5, destacar canvas de assinatura
        if (AppState.currentStep === 5) {
            const canvas = document.getElementById('signature-canvas');
            if (canvas) {
                canvas.style.borderColor = 'var(--danger)';
                canvas.style.borderWidth = '3px';
                canvas.style.animation = 'shake 0.5s ease-in-out';
                setTimeout(() => {
                    canvas.style.borderColor = '';
                    canvas.style.borderWidth = '';
                    canvas.style.animation = '';
                }, 3000);
            }
        } else {
            // Se não estiver no passo 5, navegar para ele
            showStep(5);
        }
    } else {
        console.log('✅ Assinatura presente:', AppState.signatures.cliente ? 'Sim' : 'Não');
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
async function collectFormData() {
    const form = document.getElementById('form-vistoria');
    const formData = new FormData(form);
    
    const data = {
        // Informações do veículo
        veiculo: {},
        // Questionário
        questionario: {},
        // Dados dos pneus
        pneus: {},
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
    
    // Coletar dados dos inputs do formulário
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        const name = input.name || input.id;
        if (!name) return;
        
        if (input.type === 'checkbox') {
            // Para checkboxes, verificar se está marcado
            data.questionario[name] = input.checked;
        } else if (input.type === 'radio') {
            // Para radio buttons, só adicionar se estiver selecionado
            if (input.checked) {
                if (['placa', 'modelo', 'cor', 'ano', 'km_rodado'].includes(name)) {
                    data.veiculo[name] = input.value;
                } else {
                    data[name] = input.value;
                }
            }
        } else if (input.type === 'file') {
            // Arquivos já estão em AppState.photos
            return;
        } else {
            // Input normal (text, select, textarea, etc.)
            const value = input.value.trim();
            
            // Tratamento especial para campos de observação (sempre incluir, mesmo se vazio)
            if (name.startsWith('desc_obs_')) {
                data[name] = value;
            } else if (value) {
                if (['placa', 'modelo', 'cor', 'ano', 'km_rodado'].includes(name)) {
                    data.veiculo[name] = value;
                } else {
                    if (name.startsWith("marca_pneu_")) { 
                        data.pneus[name] = value; 
                    } else { 
                        data[name] = value; 
                    }
                }
            }
        }
    });
    
    // Garantir que campos obrigatórios existam
    if (!data.veiculo.placa) data.veiculo.placa = '';
    if (!data.veiculo.modelo) data.veiculo.modelo = '';
    if (!data.veiculo.cor) data.veiculo.cor = '';
    if (!data.veiculo.ano) data.veiculo.ano = '';
    if (!data.veiculo.km_rodado) data.veiculo.km_rodado = '';  // Novo campo KM
    if (!data.nome_conferente) data.nome_conferente = '';
    if (!data.data_vistoria) data.data_vistoria = new Date().toISOString();
    
    // Adicionar documento se existir (priorizar AppState.documentData, depois verificar outros locais)
    const documentData = AppState.documentData || 
                         AppState.photos['documento_nota_fiscal'] || 
                         (AppState.documentFile ? {
        url: null, // Será convertido depois
        file: AppState.documentFile,
        name: AppState.documentFile.name,
        size: AppState.documentFile.size,
        type: AppState.documentFile.type
    } : null);
    
    if (documentData && documentData.file) {
        // Se o documento tem URL (base64), usar ela
        if (documentData.url) {
            data.documento = {
                file: documentData.url, // Base64
                name: documentData.name || documentData.file.name,
                size: documentData.size || documentData.file.size,
                type: documentData.type || documentData.file.type
            };
        } else {
            // Se não tem URL, converter para base64
            const reader = new FileReader();
            const base64Promise = new Promise((resolve) => {
                reader.onload = () => resolve(reader.result);
                reader.readAsDataURL(documentData.file);
            });
            
            try {
                const base64Data = await base64Promise;
                data.documento = {
                    file: base64Data,
                    name: documentData.file.name,
                    size: documentData.file.size,
                    type: documentData.file.type
                };
                console.log('📄 Documento convertido para base64:', data.documento.name);
            } catch (error) {
                console.error('❌ Erro ao converter documento para base64:', error);
                data.documento = null;
            }
        }
    }
    
    console.log('Dados coletados:', data);
    return data;
}

// Salvar vistoria na API
async function saveVistoria(data) {
    try {
        const response = await fetch('/api/salvar_vistoria_completa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Erro HTTP: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'Erro desconhecido ao salvar');
        }
        
        // Armazenar dados da vistoria para uso posterior
        AppState.savedVistoria = {
            id: result.id,
            token: result.token,
            data: data
        };
        
        return result;
        
    } catch (error) {
        console.error('Erro ao salvar vistoria:', error);
        throw error;
    }
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
    AppState.uploadedPhotos = [];
    AppState.signatures.cliente = null;
    AppState.documentFile = null;  // Limpar documento
    AppState.documentData = null;  // Limpar dados do documento
    
    // Limpar preview do documento
    removeDocument();
    
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

// Lazy loading para ícones Lucide - otimização mobile
function initLucideIcons() {
    // Usar requestIdleCallback para não bloquear a thread principal
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
            loadLucideIcons();
        });
    } else {
        // Fallback para navegadores sem suporte
        setTimeout(loadLucideIcons, 100);
    }
}

function loadLucideIcons() {
    try {
        if (window.lucide) {
            lucide.createIcons();
        }
    } catch (error) {
        console.warn('Erro ao carregar ícones Lucide:', error);
    }
}

// ===== SISTEMA DE NOTIFICAÇÕES MODERNAS =====
class NotificationSystem {
    constructor() {
        this.container = null;
        this.notifications = [];
        this.maxNotifications = 5;
        this.init();
    }
    
    init() {
        // Criar container se não existir
        if (!document.querySelector('.notification-container')) {
            this.container = document.createElement('div');
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.notification-container');
        }
    }
    
    show(title, message, type = 'info', duration = 5000) {
        // Remover notificações antigas se exceder o máximo
        if (this.notifications.length >= this.maxNotifications) {
            this.remove(this.notifications[0]);
        }
        
        const notification = this.create(title, message, type, duration);
        this.notifications.push(notification);
        this.container.appendChild(notification);
        
        // Animar entrada
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });
        
        // Auto-remover se duration > 0
        if (duration > 0) {
            const progressBar = notification.querySelector('.notification-progress');
            if (progressBar) {
                progressBar.style.width = '100%';
                progressBar.style.transition = `width ${duration}ms linear`;
                setTimeout(() => {
                    if (progressBar.parentNode) {
                        progressBar.style.width = '0%';
                    }
                }, 50);
            }
            
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }
        
        return notification;
    }
    
    create(title, message, type, duration) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">${icons[type] || icons.info}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" type="button">&times;</button>
            ${duration > 0 ? '<div class="notification-progress"></div>' : ''}
        `;
        
        // Event listener para fechar
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.remove(notification);
        });
        
        // Fechar ao clicar na notificação (opcional)
        notification.addEventListener('click', (e) => {
            if (e.target === notification || e.target.closest('.notification-content')) {
                this.remove(notification);
            }
        });
        
        return notification;
    }
    
    remove(notification) {
        if (!notification || !notification.parentNode) return;
        
        const index = this.notifications.indexOf(notification);
        if (index > -1) {
            this.notifications.splice(index, 1);
        }
        
        notification.classList.add('hide');
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
    }
    
    // Métodos de conveniência
    success(title, message, duration = 4000) {
        return this.show(title, message, 'success', duration);
    }
    
    error(title, message, duration = 6000) {
        return this.show(title, message, 'error', duration);
    }
    
    warning(title, message, duration = 5000) {
        return this.show(title, message, 'warning', duration);
    }
    
    info(title, message, duration = 4000) {
        return this.show(title, message, 'info', duration);
    }
}

// Instância global do sistema de notificações
const notifications = new NotificationSystem();

// Função de compatibilidade para substituir showToast
function showToast(title, message, type = 'info', duration = 5000) {
    return notifications.show(title, message, type, duration);
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

function showSuccessModal(result, link, vistoriaData) {
    // Criar modal simplificado
    const modalHTML = `
        <div id="success-modal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-body">
                    <h2 class="modal-title">Vistoria gerada!</h2>
                    <p class="modal-subtitle">Envie o link abaixo para o cliente assinar.</p>
                    
                    <div class="link-section">
                        <div class="link-container">
                            <input type="text" value="${link}" readonly class="link-input" id="modal-link-input">
                            <button onclick="copyLinkFromModal('${link}')" class="copy-btn">📋 Copiar</button>
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button onclick="startNewVistoria()" class="btn-new-vistoria" 
                                ontouchstart="this.style.transform='scale(0.95)'" 
                                ontouchend="this.style.transform='scale(1)'"
                                data-mobile-optimized="true">🆕 Nova Vistoria</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar modal ao DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Otimização adicional para mobile - garantir que o botão funcione
    setTimeout(() => {
        const newVistoriaBtn = document.querySelector('.btn-new-vistoria');
        if (newVistoriaBtn && PerformanceUtils.isMobile()) {
            // Adicionar listener adicional para garantir funcionamento em mobile
            newVistoriaBtn.addEventListener('touchend', function(e) {
                e.preventDefault();
                e.stopPropagation();
                setTimeout(() => {
                    startNewVistoria();
                }, 100);
            }, { passive: false });
        }
    }, 100);
    
    // Adicionar estilos CSS simplificados
    const style = document.createElement('style');
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            animation: fadeIn 0.3s ease-out;
        }
        
        .modal-content {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 90%;
            animation: slideUp 0.3s ease-out;
        }
        
        .modal-body {
            padding: 40px 30px;
            text-align: center;
        }
        
        .modal-title {
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
        }
        
        .modal-subtitle {
            font-size: 16px;
            color: #666;
            margin-bottom: 30px;
        }
        
        .link-section {
            margin-bottom: 30px;
        }
        
        .link-container {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .link-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            background: #f9f9f9;
            color: #333;
        }
        
        .copy-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            white-space: nowrap;
            transition: background 0.3s;
        }
        
        .copy-btn:hover {
            background: #45a049;
        }
        
        .modal-actions {
            display: flex;
            justify-content: center;
        }
        
        .btn-new-vistoria {
            background: #2196F3;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-new-vistoria:hover {
            background: #1976D2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        
        @keyframes slideUp {
            from { 
                opacity: 0; 
                transform: translateY(30px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        @media (max-width: 600px) {
            .link-container {
                flex-direction: column;
            }
            
            .copy-btn {
                padding: 12px;
            }
        }
    `;
    document.head.appendChild(style);
}

function copyLinkFromModal(link) {
    navigator.clipboard.writeText(link).then(() => {
        const button = document.querySelector('.copy-btn');
        const originalText = button.innerHTML;
        button.innerHTML = '✅ Copiado!';
        button.style.background = '#2E7D32';
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.background = '#4CAF50';
        }, 2000);
    });
}

function closeSuccessModal() {
    const modal = document.getElementById('success-modal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

function startNewVistoria() {
    try {
        // Fechar modal primeiro
        const modal = document.getElementById('success-modal');
        if (modal) {
            modal.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                modal.remove();
                
                // Reset imediato para mobile
                resetToInitialState();
            }, 100); // Reduzido para ser mais rápido
        } else {
            // Se não tem modal, reset direto
            resetToInitialState();
        }
        
    } catch (error) {
        console.error('Erro em startNewVistoria:', error);
        // Em caso de erro, reset forçado
        resetToInitialState();
    }
}

// Nova função para reset otimizado mobile
function resetToInitialState() {
    try {
        // Limpar formulário completamente
        clearForm();
        
        // Voltar para step 1 imediatamente
        showStep(1);
        
        // Ocultar loading se estiver ativo
        hideLoading();
        
        // Limpar qualquer modal ativo
        const modals = document.querySelectorAll('.modal, #success-modal');
        modals.forEach(modal => {
            if (modal && modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        });
        
        // Remover classes de estados ativos
        document.querySelectorAll('.has-image').forEach(el => {
            el.classList.remove('has-image');
        });
        
        // Reinicializar previews de foto
        const previews = document.querySelectorAll('.photo-preview');
        previews.forEach(preview => {
            resetPhotoPreview(preview);
        });
        
        // Scroll para o topo
        if (window.scrollTo) {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        } else {
            // Fallback para mobile antigo
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        }
        
        // Feedback visual de reset
        notifications.success('Sucesso', 'Sistema reiniciado! Pronto para nova vistoria.');
        
        // Forçar re-render dos ícones
        setTimeout(() => {
            loadLucideIcons();
        }, 200);
        
        // Garantir que voltou ao estado inicial (fallback de segurança)
        setTimeout(() => {
            if (AppState.currentStep !== 1) {
                console.warn('Estado não resetado corretamente, forçando reset...');
                AppState.currentStep = 1;
                showStep(1);
            }
        }, 1000);
        
    } catch (error) {
        console.error('Erro em resetToInitialState:', error);
        // Em último caso, recarregar página
        window.location.reload();
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

// Inicializar navegação por passos com otimização mobile
function initStepNavigation() {
    const btnProximo = document.getElementById('btn-proximo');
    const btnAnterior = document.getElementById('btn-anterior');
    
    // Usar throttle para evitar cliques duplos em navegação
    const throttledNext = PerformanceUtils.throttle(nextStep, 300);
    const throttledPrevious = PerformanceUtils.throttle(previousStep, 300);
    
    if (btnProximo) {
        PerformanceUtils.addTouchOptimizedEvent(btnProximo, 'click', throttledNext);
    }
    
    if (btnAnterior) {
        PerformanceUtils.addTouchOptimizedEvent(btnAnterior, 'click', throttledPrevious);
    }
    
    // Mostrar primeiro passo
    showStep(1);
}

// Mostrar passo específico - otimizado para mobile
function showStep(stepNumber) {
    // Scroll para o topo imediatamente (importante para mobile)
    if (window.scrollTo) {
        window.scrollTo(0, 0);
    } else {
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
    }
    
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
        
        // Forçar re-render para mobile
        currentStep.style.opacity = '0';
        setTimeout(() => {
            currentStep.style.opacity = '1';
        }, 50);
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
    
    // Novos campos
    const kmElement = document.getElementById('review-km');
    if (kmElement) {
        kmElement.textContent = document.getElementById('km_rodado').value || '-';
    }
    
    const docElement = document.getElementById('review-documento');
    if (docElement) {
        const docFile = AppState.documentFile;
        docElement.textContent = docFile ? `📄 ${docFile.name}` : 'Nenhum documento anexado';
    }
    
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
        // Criar container do carrossel
        const carouselContainer = document.createElement('div');
        carouselContainer.className = 'photos-container';
        
        const carousel = document.createElement('div');
        carousel.className = 'photos-carousel';
        carousel.id = 'photos-carousel';
        
        // Adicionar fotos ao carrossel
        AppState.uploadedPhotos.forEach((photo, index) => {
            const photoDiv = document.createElement('div');
            photoDiv.className = 'review-photo';
            
            const img = document.createElement('img');
            img.src = photo.url || photo.src;
            img.alt = `Foto ${index + 1}`;
            img.style.cursor = 'pointer';
            img.onclick = () => openPhotoModal(photo.url || photo.src, `Foto ${index + 1}`);
            
            photoDiv.appendChild(img);
            carousel.appendChild(photoDiv);
        });
        
        carouselContainer.appendChild(carousel);
        
        // Adicionar controles se houver mais de uma foto
        if (AppState.uploadedPhotos.length > 1) {
            const prevBtn = document.createElement('button');
            prevBtn.className = 'carousel-controls carousel-prev';
            prevBtn.innerHTML = '‹';
            prevBtn.onclick = () => moveCarousel(-1);
            
            const nextBtn = document.createElement('button');
            nextBtn.className = 'carousel-controls carousel-next';
            nextBtn.innerHTML = '›';
            nextBtn.onclick = () => moveCarousel(1);
            
            const counter = document.createElement('div');
            counter.className = 'photos-counter';
            counter.id = 'photos-counter';
            counter.textContent = `1 / ${AppState.uploadedPhotos.length}`;
            
            carouselContainer.appendChild(prevBtn);
            carouselContainer.appendChild(nextBtn);
            carouselContainer.appendChild(counter);
            
            // Adicionar suporte a toque para dispositivos móveis
            addTouchSupport(carousel);
        }
        
        photosContainer.appendChild(carouselContainer);
        
        // Inicializar estado do carrossel
        if (!window.carouselState) {
            window.carouselState = { currentIndex: 0 };
        }
        
        updateCarouselControls();
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

// FUNÇÕES DO CARROSSEL DE FOTOS
// ===============================

// Mover carrossel de fotos
function moveCarousel(direction) {
    if (!window.carouselState || !AppState.uploadedPhotos || AppState.uploadedPhotos.length <= 1) {
        return;
    }
    
    const totalPhotos = AppState.uploadedPhotos.length;
    const newIndex = window.carouselState.currentIndex + direction;
    
    // Verificar limites
    if (newIndex < 0) {
        window.carouselState.currentIndex = 0;
    } else if (newIndex >= totalPhotos) {
        window.carouselState.currentIndex = totalPhotos - 1;
    } else {
        window.carouselState.currentIndex = newIndex;
    }
    
    updateCarouselPosition();
    updateCarouselControls();
}

// Atualizar posição do carrossel
function updateCarouselPosition() {
    const carousel = document.getElementById('photos-carousel');
    if (!carousel || !window.carouselState) return;
    
    const photoWidth = 200; // Largura da foto + gap
    const gap = 16; // Espaçamento entre fotos
    const offset = -(window.carouselState.currentIndex * (photoWidth + gap));
    
    carousel.style.transform = `translateX(${offset}px)`;
}

// Atualizar controles do carrossel
function updateCarouselControls() {
    if (!window.carouselState || !AppState.uploadedPhotos) return;
    
    const prevBtn = document.querySelector('.carousel-prev');
    const nextBtn = document.querySelector('.carousel-next');
    const counter = document.getElementById('photos-counter');
    
    if (prevBtn) {
        prevBtn.disabled = window.carouselState.currentIndex === 0;
    }
    
    if (nextBtn) {
        nextBtn.disabled = window.carouselState.currentIndex >= AppState.uploadedPhotos.length - 1;
    }
    
    if (counter) {
        counter.textContent = `${window.carouselState.currentIndex + 1} / ${AppState.uploadedPhotos.length}`;
    }
}

// Adicionar suporte a toque para carrossel
function addTouchSupport(carousel) {
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    
    carousel.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        isDragging = true;
        carousel.style.transition = 'none';
    });
    
    carousel.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        
        currentX = e.touches[0].clientX;
        const diffX = currentX - startX;
        
        // Prevenir scroll vertical quando arrastando horizontalmente
        if (Math.abs(diffX) > 10) {
            e.preventDefault();
        }
    });
    
    carousel.addEventListener('touchend', (e) => {
        if (!isDragging) return;
        
        isDragging = false;
        carousel.style.transition = 'transform 0.3s ease';
        
        const diffX = currentX - startX;
        const threshold = 50; // Distância mínima para trocar foto
        
        if (Math.abs(diffX) > threshold) {
            if (diffX > 0) {
                moveCarousel(-1); // Swipe direita = foto anterior
            } else {
                moveCarousel(1);  // Swipe esquerda = próxima foto
            }
        } else {
            // Voltar para posição original se não passou do threshold
            updateCarouselPosition();
        }
    });
    
    // Adicionar também suporte para mouse drag (desktop)
    carousel.addEventListener('mousedown', (e) => {
        startX = e.clientX;
        isDragging = true;
        carousel.style.transition = 'none';
        carousel.style.cursor = 'grabbing';
        e.preventDefault();
    });
    
    carousel.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        currentX = e.clientX;
        e.preventDefault();
    });
    
    carousel.addEventListener('mouseup', (e) => {
        if (!isDragging) return;
        
        isDragging = false;
        carousel.style.transition = 'transform 0.3s ease';
        carousel.style.cursor = 'grab';
        
        const diffX = currentX - startX;
        const threshold = 50;
        
        if (Math.abs(diffX) > threshold) {
            if (diffX > 0) {
                moveCarousel(-1);
            } else {
                moveCarousel(1);
            }
        } else {
            updateCarouselPosition();
        }
    });
    
    carousel.addEventListener('mouseleave', (e) => {
        if (isDragging) {
            isDragging = false;
            carousel.style.transition = 'transform 0.3s ease';
            carousel.style.cursor = 'grab';
            updateCarouselPosition();
        }
    });
    
    // Definir cursor padrão
    carousel.style.cursor = 'grab';
}

// Função para abrir modal de visualização de foto
function openPhotoModal(imageSrc, altText) {
    // Criar modal se não existir
    let modal = document.getElementById('photo-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'photo-modal';
        modal.className = 'photo-modal';
        modal.innerHTML = `
            <div class="photo-modal-content">
                <span class="photo-modal-close">&times;</span>
                <img class="photo-modal-image" src="" alt="">
                <div class="photo-modal-caption"></div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Adicionar eventos de fechamento
        const closeBtn = modal.querySelector('.photo-modal-close');
        closeBtn.onclick = closePhotoModal;
        
        modal.onclick = function(e) {
            if (e.target === modal) {
                closePhotoModal();
            }
        };
        
        // Fechar com ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closePhotoModal();
            }
        });
    }
    
    // Atualizar conteúdo do modal
    const img = modal.querySelector('.photo-modal-image');
    const caption = modal.querySelector('.photo-modal-caption');
    
    img.src = imageSrc;
    img.alt = altText;
    caption.textContent = altText;
    
    // Mostrar modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevenir scroll do body
}

// Função para fechar modal de visualização de foto
function closePhotoModal() {
    const modal = document.getElementById('photo-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restaurar scroll do body
    }
}
