# 🚗 Sistema Ágil - Vistoria de Veículos

Sistema moderno e responsivo para realizar vistorias de veículos de forma ágil e eficiente.

## 📋 Funcionalidades

- **Sistema de 5 Etapas**: Navegação intuitiva através das etapas da vistoria
- **Entrada Inteligente**: Formatação automática de placas e campos em maiúscula
- **Assinatura Digital**: Canvas para assinatura do cliente
- **Upload de Fotos**: Sistema de upload para documentação visual
- **Validação em Tempo Real**: Feedback visual imediato para campos obrigatórios
- **Design Responsivo**: Interface otimizada para mobile e desktop
- **Navegação Fluida**: Botões de voltar/avançar em todas as etapas

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- Flask 3.0.0

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/MuRibeiroDev/Agil.git
cd Agil
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute o servidor:
```bash
cd vistoria
python create_app.py
```

6. Acesse: `http://localhost:5000`

## 📁 Estrutura do Projeto

```
SistemaAgil/
├── vistoria/
│   ├── templates/
│   │   └── index.html          # Interface principal
│   ├── css/
│   │   └── style.css           # Estilos modernos e responsivos
│   ├── js/
│   │   └── app.js              # Lógica da aplicação
│   ├── uploads/                # Diretório para uploads
│   └── create_app.py           # Servidor Flask
├── database/
│   └── migrations/
│       └── init.sql            # Schema do banco de dados
└── README.md
```

## 🎨 Características Técnicas

### Frontend
- **HTML5 Semântico**: Estrutura moderna e acessível
- **CSS3 Avançado**: Gradientes, animações e design responsivo
- **JavaScript ES6+**: Código moderno e eficiente
- **Canvas API**: Para assinatura digital
- **Mobile-First**: Otimizado para dispositivos móveis

### Backend
- **Flask 3.0.0**: Framework web minimalista e poderoso
- **Upload de Arquivos**: Sistema seguro para imagens
- **Validação de Dados**: Sanitização e validação robusta

### Recursos Visuais
- **Design Moderno**: Interface limpa e profissional
- **Animações Suaves**: Transições e feedback visual
- **Cores Inteligentes**: Esquema de cores baseado em gradientes
- **Tipografia**: Fontes otimizadas para legibilidade

## 📱 Funcionalidades Detalhadas

### Etapa 1: Informações do Veículo
- Placa (máximo 7 caracteres)
- Modelo do veículo
- Cor e ano
- Formatação automática

### Etapa 2: Questionário de Vistoria
- Perguntas de múltipla escolha
- Observações adicionais
- Validação opcional

### Etapa 3: Upload de Fotos
- Múltiplas fotos
- Preview das imagens
- Compressão automática

### Etapa 4: Dados do Conferente
- Informações do responsável
- Validação obrigatória

### Etapa 5: Assinatura Digital
- Canvas responsivo
- Suporte touch e mouse
- Função de limpar assinatura

## 🛠️ Desenvolvimento

### Tecnologias Utilizadas
- **Python 3.8+**
- **Flask 3.0.0**
- **HTML5**
- **CSS3 (Grid, Flexbox, Animations)**
- **JavaScript ES6+**
- **Canvas API**

### Padrões de Código
- Código limpo e documentado
- Separação de responsabilidades
- Design patterns modernos
- Mobile-first approach

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

**Murillo Ribeiro**
- GitHub: [@MuRibeiroDev](https://github.com/MuRibeiroDev)

---

⭐ **Gostou do projeto? Deixe uma estrela!**
