"""
Utilitário para geração de PDF de vistoria
"""
import os
import base64
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image as PILImage


class VistoriaPDFGenerator:
    """Gerador de PDF para vistorias"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos customizados"""
        # Título principal - verificar se já existe
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
                alignment=1  # Center
            ))
        
        # Subtítulo de seção
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceBefore=20,
            spaceAfter=10,
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8,
            backColor=colors.HexColor('#f9fafb')
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Label para informações
        self.styles.add(ParagraphStyle(
            name='InfoLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#374151'),
            spaceAfter=3
        ))
        
        # Valor para informações
        self.styles.add(ParagraphStyle(
            name='InfoValue',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=6
        ))
    
    def generate_pdf(self, vistoria_data, output_path):
        """Gerar PDF da vistoria"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Lista de elementos do PDF
            elements = []
            
            # Cabeçalho
            elements.extend(self._create_header(vistoria_data))
            
            # Informações do veículo
            elements.extend(self._create_vehicle_info(vistoria_data))
            
            # Questionário
            elements.extend(self._create_questionnaire(vistoria_data))
            
            # Informações dos pneus
            elements.extend(self._create_tire_info(vistoria_data))
            
            # Observações
            elements.extend(self._create_observations(vistoria_data))
            
            # Fotos
            elements.extend(self._create_photos_section(vistoria_data))
            
            # Assinatura
            elements.extend(self._create_signature_section(vistoria_data))
            
            # Rodapé
            elements.extend(self._create_footer(vistoria_data))
            
            # Gerar PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            return False
    
    def _create_header(self, data):
        """Criar cabeçalho do PDF"""
        elements = []
        
        # Título
        title = Paragraph("Relatório de Vistoria de Veículo", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Informações básicas em tabela
        token = data.get('token', 'N/A')
        data_vistoria = data.get('data_vistoria', datetime.now().strftime('%d/%m/%Y %H:%M'))
        if isinstance(data_vistoria, str) and 'T' in data_vistoria:
            try:
                dt = datetime.fromisoformat(data_vistoria.replace('Z', ''))
                data_vistoria = dt.strftime('%d/%m/%Y %H:%M')
            except:
                pass
        
        header_data = [
            ['Token da Vistoria:', token],
            ['Data da Vistoria:', data_vistoria],
            ['Status:', data.get('status', 'Concluída').title()]
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_vehicle_info(self, data):
        """Criar seção de informações do veículo"""
        elements = []
        
        # Título da seção
        section_title = Paragraph("Informações do Veículo", self.styles['SectionTitle'])
        elements.append(section_title)
        
        # Dados do veículo
        veiculo = data.get('veiculo', {})
        
        # Debug: verificar nome do cliente
        nome_cliente = data.get('nome_cliente')
        nome_terceiro = data.get('nome_terceiro')
        print(f"📄 DEBUG PDF_UTILS - nome_cliente recebido: '{nome_cliente}'")
        print(f"📄 DEBUG PDF_UTILS - nome_terceiro recebido: '{nome_terceiro}'")
        
        # Lógica: usar nome_terceiro se nome_cliente estiver vazio
        nome_para_exibir = nome_cliente if nome_cliente else (nome_terceiro if nome_terceiro else 'N/A')
        print(f"📄 DEBUG PDF_UTILS - nome que será exibido: '{nome_para_exibir}'")
        
        vehicle_data = [
            ['Nome do Cliente:', nome_para_exibir],
            ['Placa:', veiculo.get('placa', 'N/A') or 'Não informado'],
            ['Modelo:', veiculo.get('modelo', 'N/A')],
            ['Cor:', veiculo.get('cor', 'N/A')],
            ['Ano:', veiculo.get('ano', 'N/A') or 'Não informado'],
            ['KM Rodado:', veiculo.get('km_rodado', 'N/A') or 'Não informado']
        ]
        
        vehicle_table = Table(vehicle_data, colWidths=[2*inch, 3*inch])
        vehicle_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        elements.append(vehicle_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_questionnaire(self, data):
        """Criar seção do questionário"""
        elements = []
        
        # Título da seção
        section_title = Paragraph("Itens Verificados", self.styles['SectionTitle'])
        elements.append(section_title)
        
        # Mapeamento de campos do questionário
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
            'pneu_step': 'Pneu Step'
        }
        
        # Criar dados da tabela
        questionnaire_data = [['Item', 'Status']]
        for field, label in questionnaire_fields.items():
            value = data.get(field, False)
            status = '✓ Sim' if value else '✗ Não'
            questionnaire_data.append([label, status])
        
        questionnaire_table = Table(questionnaire_data, colWidths=[3*inch, 1.5*inch])
        questionnaire_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb'))
        ]))
        
        elements.append(questionnaire_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_tire_info(self, data):
        """Criar seção das informações dos pneus"""
        elements = []
        
        # Verificar se há dados de pneus
        pneus = data.get('pneus', {})
        if not any(pneus.values()):
            return elements
        
        # Título da seção
        section_title = Paragraph("Informações dos Pneus", self.styles['SectionTitle'])
        elements.append(section_title)
        
        tire_data = [
            ['Pneu Dianteiro Esquerdo:', pneus.get('marca_pneu_dianteiro_esquerdo', 'N/A') or 'Não informado'],
            ['Pneu Dianteiro Direito:', pneus.get('marca_pneu_dianteiro_direito', 'N/A') or 'Não informado'],
            ['Pneu Traseiro Esquerdo:', pneus.get('marca_pneu_traseiro_esquerdo', 'N/A') or 'Não informado'],
            ['Pneu Traseiro Direito:', pneus.get('marca_pneu_traseiro_direito', 'N/A') or 'Não informado']
        ]
        
        tire_table = Table(tire_data, colWidths=[2.5*inch, 2.5*inch])
        tire_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        elements.append(tire_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_observations(self, data):
        """Criar seção de observações"""
        elements = []
        
        # Verificar se há observações
        observations = []
        for i in range(1, 5):
            obs = data.get(f'desc_obs_{i}', '')
            if obs and obs.strip():
                observations.append(f"Observação {i}: {obs}")
        
        if not observations:
            return elements
        
        # Título da seção
        section_title = Paragraph("Observações", self.styles['SectionTitle'])
        elements.append(section_title)
        
        for obs in observations:
            obs_para = Paragraph(obs, self.styles['NormalText'])
            elements.append(obs_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_photos_section(self, data):
        """Criar seção de fotos com layout otimizado (4 fotos por página)"""
        elements = []
        
        # Verificar se há fotos
        photos = data.get('photos', [])
        if not photos:
            return elements
        
        # Título da seção
        section_title = Paragraph("Fotos da Vistoria", self.styles['SectionTitle'])
        elements.append(section_title)
        
        # Adicionar informações sobre as fotos
        photo_info = Paragraph(f"Total de fotos anexadas: {len(photos)}", self.styles['NormalText'])
        elements.append(photo_info)
        elements.append(Spacer(1, 15))
        
        # Processar fotos em grupos de 4 (2x2 por página)
        photos_per_page = 4
        
        for page_index in range(0, len(photos), photos_per_page):
            # Obter até 4 fotos para esta página
            photos_on_page = photos[page_index:page_index + photos_per_page]
            
            # Criar lista para armazenar as imagens processadas desta página
            page_images = []
            page_labels = []
            
            for photo in photos_on_page:
                try:
                    category = photo.get('category', 'N/A')
                    filename = photo.get('name', 'N/A')
                    photo_path = photo.get('path', '')
                    
                    # Label da foto
                    label = f"{category.replace('_', ' ').title()}"
                    page_labels.append(label)
                    
                    # Construir caminho absoluto para a foto
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                    possible_paths = [
                        photo_path if photo_path and os.path.isabs(photo_path) else None,
                        os.path.join(base_dir, 'uploads', 'fotos', filename),
                        os.path.join(base_dir, 'uploads', filename),
                        os.path.join(os.getcwd(), 'uploads', 'fotos', filename),
                        filename if os.path.exists(filename) else None
                    ]
                    
                    # Filtrar None
                    possible_paths = [p for p in possible_paths if p]
                    
                    found_image = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            try:
                                print(f"📸 Carregando foto: {path}")
                                
                                # Criar imagem com tamanho otimizado para 4 fotos por página
                                photo_img = Image(path)
                                
                                # Tamanho otimizado para 4 fotos (2x2)
                                # Cada foto terá aproximadamente 2.5" x 1.8"
                                max_width = 2.5*inch  
                                max_height = 1.8*inch
                                
                                # Obter dimensões originais
                                from PIL import Image as PILImage
                                pil_img = PILImage.open(path)
                                orig_width, orig_height = pil_img.size
                                
                                # Calcular proporção mantendo aspecto original
                                ratio = min(max_width/orig_width, max_height/orig_height)
                                new_width = orig_width * ratio
                                new_height = orig_height * ratio
                                
                                photo_img.drawWidth = new_width
                                photo_img.drawHeight = new_height
                                
                                found_image = photo_img
                                print(f"✅ Foto carregada: {path} ({new_width:.1f}x{new_height:.1f})")
                                break
                                
                            except Exception as e:
                                print(f"⚠️ Erro ao carregar foto em {path}: {e}")
                                continue
                    
                    if found_image:
                        page_images.append(found_image)
                    else:
                        print(f"❌ Foto não encontrada: {filename}")
                        # Criar placeholder para foto não encontrada
                        placeholder = Paragraph(f"[Foto não encontrada]", self.styles['InfoValue'])
                        page_images.append(placeholder)
                        
                except Exception as e:
                    print(f"⚠️ Erro ao processar foto: {e}")
                    error_placeholder = Paragraph(f"[Erro na foto]", self.styles['InfoValue'])
                    page_images.append(error_placeholder)
                    page_labels.append("Erro")
            
            # Organizar as fotos em uma tabela 2x2
            if page_images:
                # Preparar dados da tabela (2 linhas x 2 colunas)
                table_data = []
                
                # Primeira linha - Fotos
                row1_images = []
                row1_labels = []
                
                for i in range(2):  # 2 colunas
                    if i < len(page_images):
                        row1_images.append(page_images[i])
                        row1_labels.append(Paragraph(page_labels[i], self.styles['InfoLabel']))
                    else:
                        row1_images.append("")
                        row1_labels.append("")
                
                # Segunda linha - Fotos (se houver mais de 2)
                row2_images = []
                row2_labels = []
                
                for i in range(2, 4):  # Próximas 2 colunas
                    if i < len(page_images):
                        row2_images.append(page_images[i])
                        row2_labels.append(Paragraph(page_labels[i], self.styles['InfoLabel']))
                    else:
                        row2_images.append("")
                        row2_labels.append("")
                
                # Montar tabela apenas se há fotos na segunda linha
                if any(row2_images):
                    table_data = [
                        row1_images,
                        row1_labels,
                        row2_images,
                        row2_labels
                    ]
                else:
                    table_data = [
                        row1_images,
                        row1_labels
                    ]
                
                # Criar tabela com larguras iguais
                available_width = 6.5*inch  # Largura disponível na página
                col_width = available_width / 2  # 2 colunas
                
                photo_table = Table(table_data, colWidths=[col_width, col_width])
                photo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    # Bordas suaves entre fotos
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    # Background alternado para labels
                    ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f9fafb')),  # Labels primeira linha
                ] + ([('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f9fafb'))] if len(table_data) > 2 else [])))
                
                elements.append(photo_table)
                elements.append(Spacer(1, 20))
                
                # Adicionar quebra de página se não for a última página de fotos
                if page_index + photos_per_page < len(photos):
                    elements.append(PageBreak())
        
        return elements
    
    def _create_signature_section(self, data):
        """Criar seção de assinatura"""
        elements = []
        
        # Título da seção
        section_title = Paragraph("Assinatura do Cliente", self.styles['SectionTitle'])
        elements.append(section_title)
        
        # Informações da assinatura
        nome_cliente_assinatura = data.get('nome_cliente')
        nome_terceiro_assinatura = data.get('nome_terceiro')
        print(f"📄 DEBUG PDF_UTILS - nome_cliente para assinatura: '{nome_cliente_assinatura}'")
        print(f"📄 DEBUG PDF_UTILS - nome_terceiro para assinatura: '{nome_terceiro_assinatura}'")
        
        # Lógica: usar nome_terceiro se nome_cliente estiver vazio
        nome_assinatura = nome_cliente_assinatura if nome_cliente_assinatura else (nome_terceiro_assinatura if nome_terceiro_assinatura else 'N/A')
        print(f"📄 DEBUG PDF_UTILS - nome que será usado na assinatura: '{nome_assinatura}'")
        
        assinatura_info = [
            ['Cliente:', nome_assinatura],
            ['Data da Assinatura:', data.get('assinado_em', 'N/A') or 'Assinado eletronicamente'],
            ['Status:', 'Assinado digitalmente']
        ]
        
        signature_table = Table(assinatura_info, colWidths=[2*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 15))
        
        # Incluir imagem da assinatura se disponível
        assinatura_path = data.get('assinatura_path')
        
        # Debug da assinatura
        print(f"🖊️ DEBUG assinatura_path: {assinatura_path}")
        print(f"🖊️ DEBUG dados assinatura: {[(k,v) for k,v in data.items() if 'assinatura' in k.lower()]}")
        
        # Construir caminho absoluto para assinatura
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Voltar para pasta vistoria
        token = data.get('token', '')
        
        # Tentar diferentes caminhos para a assinatura
        possible_signature_paths = []
        
        # Se há caminho da assinatura no banco, tentar usá-lo
        if assinatura_path:
            # Se é caminho relativo, construir absoluto
            if not os.path.isabs(assinatura_path):
                possible_signature_paths.append(os.path.join(base_dir, assinatura_path))
                # Normalizar barras do Windows
                normalized_path = assinatura_path.replace('\\', os.sep)
                possible_signature_paths.append(os.path.join(base_dir, normalized_path))
            else:
                possible_signature_paths.append(assinatura_path)
        
        # Adicionar caminhos alternativos baseados no token
        possible_signature_paths.extend([
            os.path.join(base_dir, 'assinaturas', f'assinatura_{token}.png'),
            os.path.join(base_dir, f'assinatura_{token}.png'),
            os.path.join(os.getcwd(), 'assinaturas', f'assinatura_{token}.png'),
        ])
        
        # Se ainda não encontrou, buscar por padrão na pasta assinaturas
        assinaturas_dir = os.path.join(base_dir, 'assinaturas')
        if os.path.exists(assinaturas_dir):
            for filename in os.listdir(assinaturas_dir):
                if token in filename and filename.endswith('.png'):
                    possible_signature_paths.append(os.path.join(assinaturas_dir, filename))
        
        signature_loaded = False
        
        for sig_path in possible_signature_paths:
            if os.path.exists(sig_path):
                try:
                    print(f"🖊️ Carregando assinatura: {sig_path}")
                    
                    # Título para a imagem da assinatura
                    sig_title = Paragraph("Assinatura Digital:", self.styles['InfoLabel'])
                    elements.append(sig_title)
                    elements.append(Spacer(1, 5))
                    
                    # Carregar e redimensionar imagem da assinatura
                    signature_img = Image(sig_path)
                    signature_img.drawHeight = 1.5*inch  # Altura fixa
                    signature_img.drawWidth = 4*inch     # Largura fixa
                    
                    elements.append(signature_img)
                    elements.append(Spacer(1, 10))
                    
                    # Informação sobre integridade
                    checksum_info = data.get('assinatura_checksum')
                    if checksum_info:
                        integrity_text = f"Verificação de integridade: {checksum_info[:16]}..."
                        integrity = Paragraph(integrity_text, self.styles['InfoValue'])
                        elements.append(integrity)
                    
                    signature_loaded = True
                    print(f"✅ Assinatura carregada com sucesso: {sig_path}")
                    break
                    
                except Exception as e:
                    print(f"⚠️ Erro ao carregar assinatura em {sig_path}: {e}")
                    continue
        
        if not signature_loaded:
            # Verificar se há data de assinatura
            assinado_em = data.get('assinado_em')
            if assinado_em and assinado_em != 'N/A':
                # Existe assinatura mas sem imagem
                signed_text = Paragraph("Vistoria assinada digitalmente (imagem não encontrada)", self.styles['InfoValue'])
                elements.append(signed_text)
                print(f"❌ Assinatura não encontrada. Token: {token}")
                print(f"   Caminho do banco: {assinatura_path}")
                print(f"   Caminhos testados: {possible_signature_paths}")
            else:
                # Sem assinatura, mostrar espaço para assinatura manual
                no_sig_text = Paragraph("Assinatura não disponível ou pendente", self.styles['InfoValue'])
                elements.append(no_sig_text)
                elements.append(Spacer(1, 30))
                
                # Linha para assinatura manual
                line_text = Paragraph("_" * 50, self.styles['Normal'])
                elements.append(line_text)
                sig_label = Paragraph("Assinatura do Cliente", self.styles['InfoLabel'])
                elements.append(sig_label)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self, data):
        """Criar rodapé do PDF"""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        footer_text = f"""
        <para align="center">
        <b>Sistema Ágil - Vistoria de Veículos</b><br/>
        Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/>
        Conferente: {data.get('nome_conferente', 'N/A')}
        </para>
        """
        
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
        
        return elements


def generate_vistoria_pdf(vistoria_data, output_path):
    """Função principal para gerar PDF de vistoria"""
    generator = VistoriaPDFGenerator()
    return generator.generate_pdf(vistoria_data, output_path)


# Função de teste
if __name__ == "__main__":
    # Dados de exemplo para teste
    test_data = {
        'token': 'VIST_TEST_12345',
        'nome_cliente': 'João Silva',
        'nome_conferente': 'Maria Santos',
        'data_vistoria': '2025-08-31T12:00:00',
        'status': 'concluida',
        'veiculo': {
            'placa': 'ABC1234',
            'modelo': 'Honda Civic',
            'cor': 'Prata',
            'ano': '2020',
            'km_rodado': '50000'
        },
        'ar_condicionado': True,
        'antenas': True,
        'tapetes': False,
        'bateria': True,
        'photos': [
            {'category': 'foto_painel', 'name': 'Painel'},
            {'category': 'foto_lateral', 'name': 'Lateral'}
        ],
        'desc_obs_1': 'Veículo em bom estado geral',
        'pneus': {
            'marca_pneu_dianteiro_esquerdo': 'Michelin',
            'marca_pneu_dianteiro_direito': 'Michelin'
        }
    }
    
    output_file = 'test_vistoria.pdf'
    if generate_vistoria_pdf(test_data, output_file):
        print(f"✅ PDF gerado com sucesso: {output_file}")
    else:
        print("❌ Erro ao gerar PDF")
