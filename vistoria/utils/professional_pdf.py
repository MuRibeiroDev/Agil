"""
Gerador de PDF Profissional - Vistoria Ágil
Design limpo e moderno com todas as informações da vistoria
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from flask import current_app


class ProfessionalPDFGenerator:
    """Gerador de PDF profissional e limpo"""
    
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """Configurar estilos profissionais"""
        self.styles = getSampleStyleSheet()
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1f2937')
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=colors.HexColor('#6b7280')
        ))
        
        # Título de seção
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#374151'),
            leftIndent=0
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            fontName='Helvetica',
            textColor=colors.HexColor('#374151')
        ))
        
        # Label para informações
        self.styles.add(ParagraphStyle(
            name='InfoLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#4b5563')
        ))
        
        # Valor para informações
        self.styles.add(ParagraphStyle(
            name='InfoValue',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            textColor=colors.HexColor('#111827')
        ))
    
    def generate_pdf(self, vistoria_data, output_path):
        """Gerar PDF profissional"""
        try:
            # Configuração do documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            elements = []
            
            # PRIMEIRA PÁGINA: Cabeçalho + Dados do Veículo + Questionário
            elements.extend(self._create_header())
            elements.extend(self._create_vehicle_section(vistoria_data))
            elements.extend(self._create_questionnaire_section(vistoria_data))
            
            # Quebra de página
            elements.append(PageBreak())
            
            # PÁGINAS SEGUINTES: Demais informações
            elements.extend(self._create_tires_section(vistoria_data))
            elements.extend(self._create_observations_section(vistoria_data))
            
            # Verificar se fotos devem ser incluídas no PDF
            pdf_options = vistoria_data.get('pdf_options', {})
            include_photos = pdf_options.get('include_photos', True)  # Default: incluir fotos
            
            if include_photos:
                print("📸 Incluindo fotos no PDF")
                elements.extend(self._create_photos_section(vistoria_data))
            else:
                print("🚫 Fotos não incluídas no PDF (toggle desativado)")
            
            elements.extend(self._create_signature_section(vistoria_data))
            elements.extend(self._create_footer(vistoria_data))
            
            # Gerar PDF
            doc.build(elements)
            
            print(f"✅ PDF profissional gerado: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            return False
    
    def _create_header(self):
        """Criar cabeçalho limpo e profissional"""
        elements = []
        
        # Título principal
        title = Paragraph("RELATÓRIO DE VISTORIA VEICULAR", self.styles['MainTitle'])
        elements.append(title)
        
        # Subtítulo
        subtitle = Paragraph("Sistema Agil - Documento Oficial", self.styles['Subtitle'])
        elements.append(subtitle)
        
        # Linha decorativa
        line_data = [['']]
        line_table = Table(line_data, colWidths=[15*cm])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(line_table)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_vehicle_section(self, data):
        """Criar seção de dados do veículo"""
        elements = []
        
        # Título da seção
        title = Paragraph("DADOS DO VEÍCULO", self.styles['SectionTitle'])
        elements.append(title)
        
        veiculo = data.get('veiculo', {})
        
        # Lógica para definir o proprietário/responsável
        nome_cliente = data.get('nome_cliente', '').strip() if data.get('nome_cliente') else ''
        nome_terceiro = data.get('nome_terceiro', '').strip() if data.get('nome_terceiro') else ''
        
        # Dados organizados em card limpo
        vehicle_data = [
            ['PLACA:', veiculo.get('placa', 'N/A'), 'MODELO:', veiculo.get('modelo', 'N/A')],
            ['ANO:', veiculo.get('ano', 'N/A'), 'COR:', veiculo.get('cor', 'N/A')],
            ['CHASSI:', veiculo.get('chassi', 'N/A'), 'KM RODADO:', data.get('km_rodado', 'N/A')]
        ]
        
        # Adicionar linha com proprietário baseado na lógica solicitada
        proprietario_info = []
        
        if nome_cliente and nome_terceiro:
            # Se tem os dois nomes, mostrar ambos
            proprietario_info = ['CLIENTE:', nome_cliente, 'TERCEIRO:', nome_terceiro]
        elif nome_cliente:
            # Se tem apenas nome do cliente
            proprietario_info = ['CLIENTE:', nome_cliente, '', '']
        elif nome_terceiro:
            # Se tem apenas nome do terceiro
            proprietario_info = ['TERCEIRO:', nome_terceiro, '', '']
        
        # Se há informação de proprietário, adicionar na tabela
        if proprietario_info and any(proprietario_info):
            vehicle_data.append(proprietario_info)
        
        # Tabela com largura automática baseada no conteúdo
        vehicle_table = Table(vehicle_data)
        vehicle_table.setStyle(TableStyle([
            # Fundo alternado
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
            # Bordas limpas
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#d1d5db')),
            # Fontes e cores
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Labels coluna 1
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Labels coluna 3
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),       # Valores coluna 2
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),       # Valores coluna 4
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            # Cores dos labels
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#4b5563')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111827')),
            ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#111827')),
            # Alinhamento e padding
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),   # Padding reduzido
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),  # Padding reduzido
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(vehicle_table)
        elements.append(Spacer(1, 25))
        
        return elements
    
    def _create_questionnaire_section(self, data):
        """Criar seção do questionário limpa e organizada"""
        elements = []
        
        # Título da seção
        title = Paragraph("QUESTIONÁRIO DE VISTORIA", self.styles['SectionTitle'])
        elements.append(title)
        
        # Mapear campos do questionário
        questionnaire_fields = {
            'ar_condicionado': 'Ar Condicionado',
            'antenas': 'Antenas',
            'tapetes': 'Tapetes',
            'tapete_porta_malas': 'Tapete Porta-malas',
            'bateria': 'Bateria',
            'retrovisor_direito': 'Retrovisor Direito',
            'retrovisor_esquerdo': 'Retrovisor Esquerdo',
            'extintor': 'Extintor',
            'roda_comum': 'Roda Comum',
            'roda_especial': 'Roda Especial',
            'chave_principal': 'Chave Principal',
            'chave_reserva': 'Chave Reserva',
            'manual': 'Manual do Veículo',
            'documento': 'Documento do Veículo',
            'nota_fiscal': 'Nota Fiscal',
            'limpador_dianteiro': 'Limpador Dianteiro',
            'limpador_traseiro': 'Limpador Traseiro',
            'triangulo': 'Triângulo',
            'macaco': 'Macaco',
            'chave_roda': 'Chave de Roda',
            'pneu_step': 'Pneu Step',
            'carregador_eletrico': 'Carregador Elétrico'
        }
        
        # Processar dados
        items = []
        for field, label in questionnaire_fields.items():
            value = data.get(field, False)
            
            # Converter para booleano
            if isinstance(value, str):
                value = value.lower() in ['true', '1', 'yes', 'sim']
            elif value is None:
                value = False
            
            status_symbol = '✓' if value else '✗'
            status_color = colors.HexColor('#10b981') if value else colors.HexColor('#ef4444')
            items.append((label, status_symbol, status_color))
        
        # Dividir em duas colunas
        mid_point = (len(items) + 1) // 2
        left_items = items[:mid_point]
        right_items = items[mid_point:]
        
        # Dados da tabela sem cabeçalho
        questionnaire_data = []
        
        # Preencher linhas
        max_rows = max(len(left_items), len(right_items))
        for i in range(max_rows):
            left_item = left_items[i] if i < len(left_items) else ('', '', colors.black)
            right_item = right_items[i] if i < len(right_items) else ('', '', colors.black)
            
            questionnaire_data.append([
                left_item[0], left_item[1], right_item[0], right_item[1]
            ])
        
        questionnaire_table = Table(questionnaire_data, colWidths=[7*cm, 1*cm, 7*cm, 1*cm])
        
        # Estilo da tabela
        table_style = [
            # Corpo da tabela
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),    # Itens à esquerda
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Status centralizados
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),    # Itens à esquerda
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Status centralizados
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Bordas e cores
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Linha separadora entre colunas
            ('LINEAFTER', (1, 0), (1, -1), 2, colors.HexColor('#9ca3af')),
        ]
        
        # Adicionar cores específicas para os status
        for i, (left_item, right_item) in enumerate(zip(left_items, right_items)):
            if i < max_rows:
                # Status da coluna esquerda
                table_style.append(('TEXTCOLOR', (1, i), (1, i), left_item[2]))
                table_style.append(('FONTSIZE', (1, i), (1, i), 14))
                
                # Status da coluna direita
                if i < len(right_items):
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), right_item[2]))
                    table_style.append(('FONTSIZE', (3, i), (3, i), 14))
        
        questionnaire_table.setStyle(TableStyle(table_style))
        elements.append(questionnaire_table)
        
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_tires_section(self, data):
        """Criar seção de informações dos pneus"""
        elements = []
        
        pneus = data.get('pneus', {})
        if not any(pneus.values()):
            return elements
        
        title = Paragraph("INFORMAÇÕES DOS PNEUS", self.styles['SectionTitle'])
        elements.append(title)
        
        tire_data = [
            ['POSIÇÃO', 'MARCA/INFORMAÇÃO'],
            ['Pneu Dianteiro Esquerdo', pneus.get('marca_pneu_dianteiro_esquerdo', 'N/A')],
            ['Pneu Dianteiro Direito', pneus.get('marca_pneu_dianteiro_direito', 'N/A')],
            ['Pneu Traseiro Esquerdo', pneus.get('marca_pneu_traseiro_esquerdo', 'N/A')],
            ['Pneu Traseiro Direito', pneus.get('marca_pneu_traseiro_direito', 'N/A')]
        ]
        
        tire_table = Table(tire_data)  # Sem largura fixa - adaptável ao conteúdo
        tire_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corpo
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(tire_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_observations_section(self, data):
        """Criar seção de observações"""
        elements = []
        
        # Verificar observações
        observations = []
        for i in range(1, 5):
            obs = data.get(f'desc_obs_{i}', '')
            if obs and obs.strip():
                observations.append((i, obs))
        
        if not observations:
            return elements
        
        title = Paragraph("OBSERVAÇÕES GERAIS", self.styles['SectionTitle'])
        elements.append(title)
        
        obs_data = [['Nº', 'OBSERVAÇÃO']]
        for num, obs_text in observations:
            obs_data.append([str(num), obs_text])
        
        obs_table = Table(obs_data, colWidths=[1.5*cm, None])  # Primeira coluna fixa, segunda adaptável
        obs_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(obs_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_photos_section(self, data):
        """Criar seção de fotos com imagens reais (4 por página)"""
        elements = []
        
        fotos = data.get('fotos', [])
        if not fotos:
            return elements
        
        title = Paragraph("REGISTRO FOTOGRÁFICO", self.styles['SectionTitle'])
        elements.append(title)
        elements.append(Spacer(1, 10))
        
        # Processar fotos em grupos de 2 (para dar mais espaço às imagens maiores)
        photos_per_page = 2
        photo_groups = [fotos[i:i + photos_per_page] for i in range(0, len(fotos), photos_per_page)]
        
        for group_index, photo_group in enumerate(photo_groups):
            if group_index > 0:
                # Nova página para cada grupo após o primeiro
                elements.append(PageBreak())
                title = Paragraph("REGISTRO FOTOGRÁFICO (continuação)", self.styles['SectionTitle'])
                elements.append(title)
                elements.append(Spacer(1, 10))
            
            # Organizar fotos - 3 por página, uma abaixo da outra (sem legendas)
            for foto in photo_group:
                try:
                    # Caminho da foto
                    photo_path = foto.get('path', '')
                    categoria = foto.get('categoria', 'Foto')
                    
                    if photo_path and os.path.exists(photo_path):
                        # Criar imagem redimensionada para caber 3 por página
                        img = Image(photo_path)
                        
                        # Calcular tamanho otimizado para 3 fotos por página (SEM legendas)
                        # Página tem ~25cm de altura útil, dividido por 3 = ~8.3cm por foto
                        max_width = 15*cm
                        max_height = 8*cm  # Aumentado já que não tem legenda
                        
                        # Obter dimensões naturais da imagem
                        img_width, img_height = img.imageWidth, img.imageHeight
                        
                        # Calcular escala mantendo proporção
                        scale_w = max_width / img_width
                        scale_h = max_height / img_height
                        scale = min(scale_w, scale_h)  # Sempre redimensionar para caber
                        
                        # Aplicar escala
                        img.drawWidth = img_width * scale
                        img.drawHeight = img_height * scale
                        img.hAlign = 'CENTER'
                        
                        # Adicionar apenas a imagem centralizada (SEM legenda)
                        elements.append(img)
                        elements.append(Spacer(1, 6))  # Espaçamento mínimo entre fotos
                        
                    else:
                        # Placeholder compacto se foto não existe (SEM legenda)
                        placeholder = Paragraph("<para align=center>Imagem não disponível</para>", self.styles['NormalText'])
                        elements.append(placeholder)
                        elements.append(Spacer(1, 6))
                        
                except Exception as e:
                    print(f"Erro ao processar foto {foto}: {e}")
                    # Placeholder em caso de erro (SEM legenda)
                    error_text = Paragraph("<para align=center>Erro ao carregar foto</para>", self.styles['NormalText'])
                    elements.append(error_text)
                    elements.append(Spacer(1, 6))
        
        return elements
    
    def _create_signature_section(self, data):
        """Criar seção de assinatura simplificada - apenas título e imagem da assinatura"""
        elements = []
        
        title = Paragraph("ASSINATURA DIGITAL", self.styles['SectionTitle'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Verificar se há assinatura
        token = data.get('token_assinatura')
        assinado_em = data.get('assinado_em')
        
        # Lógica para determinar o nome do cliente
        cliente_nome = None
        
        # 1. Primeiro tenta pegar o nome do cliente da primeira etapa
        if data.get('nome_cliente'):
            cliente_nome = data.get('nome_cliente')
        # 2. Se não tiver nome do cliente e o veículo for de terceiro, pega o nome do terceiro
        elif not data.get('proprio', True) and data.get('nome_terceiro'):
            cliente_nome = data.get('nome_terceiro')
        # 3. Fallback para o nome da assinatura se existir
        elif data.get('assinatura_cliente_nome'):
            cliente_nome = data.get('assinatura_cliente_nome')
        else:
            cliente_nome = 'N/A'
        
        if token and assinado_em and assinado_em != 'N/A':
            # Tentar exibir a imagem da assinatura
            try:
                # Buscar arquivo de assinatura na pasta assinaturas
                signature_path = None
                assinaturas_dir = os.path.join(os.path.dirname(__file__), '..', 'assinaturas')
                
                if os.path.exists(assinaturas_dir):
                    # Procurar por arquivo de assinatura com o token
                    for filename in os.listdir(assinaturas_dir):
                        if token in filename and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                            signature_path = os.path.join(assinaturas_dir, filename)
                            break
                
                if signature_path and os.path.exists(signature_path):
                    # Criar imagem da assinatura centralizada
                    signature_img = Image(signature_path)
                    # Redimensionar para caber bem no documento
                    signature_img.drawHeight = 3*cm
                    signature_img.drawWidth = 8*cm
                    signature_img.hAlign = 'CENTER'
                    
                    elements.append(signature_img)
                    elements.append(Spacer(1, 10))
                    
                    # Linha para assinatura
                    line_data = [['_' * 50]]
                    line_table = Table(line_data, colWidths=[10*cm])
                    line_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTSIZE', (0, 0), (-1, -1), 12),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#666666')),
                    ]))
                    elements.append(line_table)
                    elements.append(Spacer(1, 8))
                    
                    # Nome do cliente centralizado abaixo da linha
                    if cliente_nome and cliente_nome != 'N/A':
                        # Usar Paragraph com alinhamento central
                        cliente_name_para = Paragraph(
                            f"<para align=center><b>{cliente_nome}</b></para>",
                            self.styles['InfoValue']
                        )
                        elements.append(cliente_name_para)
                
                else:
                    # Assinado mas sem imagem disponível
                    no_img_text = Paragraph(
                        "<i>Assinatura digital registrada, mas imagem não disponível para exibição.</i>",
                        self.styles['NormalText']
                    )
                    elements.append(no_img_text)
                    
            except Exception as e:
                print(f"Erro ao carregar assinatura: {e}")
                error_text = Paragraph(
                    "<i>Erro ao carregar imagem da assinatura.</i>",
                    self.styles['NormalText']
                )
                elements.append(error_text)
        else:
            # Sem assinatura
            no_sig_text = Paragraph(
                "<b>Documento Pendente de Assinatura</b><br/><br/>"
                "Este relatório aguarda assinatura digital do cliente. "
                "A vistoria foi realizada e os dados coletados, mas ainda não foi finalizada.",
                self.styles['NormalText']
            )
            elements.append(no_sig_text)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self, data):
        """Criar rodapé do documento"""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        # Linha separadora
        line_data = [['']]
        line_table = Table(line_data, colWidths=[15*cm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 2, colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(line_table)
        
        elements.append(Spacer(1, 15))
        
        # Informações do rodapé
        footer_data = [
            ['Sistema Agil - Vistoria de Veículos', f'Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}'],
            ['Conferente: ' + data.get('nome_conferente', 'N/A'), 'ID: ' + str(data.get('id', 'N/A'))]
        ]
        
        footer_table = Table(footer_data, colWidths=[7.5*cm, 7.5*cm])
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#6b7280')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(footer_table)
        
        return elements


def generate_professional_pdf(vistoria_data, output_path):
    """Função principal para gerar PDF profissional"""
    generator = ProfessionalPDFGenerator()
    return generator.generate_pdf(vistoria_data, output_path)
