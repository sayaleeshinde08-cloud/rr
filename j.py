import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None
    st.warning("OpenAI API key not found. Translation features will be limited.")

# Page config
st.set_page_config(
    page_title="Stitching Inspection Report",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chinese cities dictionary
CHINESE_CITIES = {
    "Guangzhou": "广州",
    "Shenzhen": "深圳",
    "Dongguan": "东莞",
    "Foshan": "佛山",
    "Zhongshan": "中山",
    "Huizhou": "惠州",
    "Zhuhai": "珠海",
    "Jiangmen": "江门",
    "Zhaoqing": "肇庆",
    "Shanghai": "上海",
    "Beijing": "北京",
    "Suzhou": "苏州",
    "Hangzhou": "杭州",
    "Ningbo": "宁波",
    "Wenzhou": "温州",
    "Wuhan": "武汉",
    "Chengdu": "成都",
    "Chongqing": "重庆",
    "Tianjin": "天津",
    "Nanjing": "南京",
    "Xi'an": "西安",
    "Qingdao": "青岛",
    "Dalian": "大连",
    "Shenyang": "沈阳",
    "Changsha": "长沙",
    "Zhengzhou": "郑州",
    "Jinan": "济南",
    "Harbin": "哈尔滨",
    "Changchun": "长春",
    "Taiyuan": "太原",
    "Shijiazhuang": "石家庄",
    "Lanzhou": "兰州",
    "Xiamen": "厦门",
    "Fuzhou": "福州",
    "Nanning": "南宁",
    "Kunming": "昆明",
    "Guiyang": "贵阳",
    "Haikou": "海口",
    "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨"
}

# Custom icons for stitching inspection - ADDED MISSING 'style' KEY
ICONS = {
    "title": "🧵",
    "basic_info": "📋",
    "personnel": "👥",
    "order_info": "📦",
    "quality_check": "✅",
    "outsourcing": "🔄",
    "signatures": "✍️",
    "generate": "📊",
    "download": "📥",
    "settings": "⚙️",
    "language": "🌐",
    "location": "📍",
    "time": "🕐",
    "info": "ℹ️",
    "factory": "🏭",
    "qc": "👁️",
    "supervisor": "👔",
    "stitching": "🪡",
    "worker": "👷",
    "order": "📝",
    "color": "🎨",
    "quantity": "🔢",
    "risk": "⚠️",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "check": "✓",
    "ratio": "📊",
    "capacity": "📈",
    "production": "🏭",
    "style": "👕",  # ADDED THIS MISSING KEY
    "lot": "🏷️",   # Added for lot number
    "date": "📅",   # Added for date
    "abnormality": "🚨",  # Added for quality abnormality
    "solution": "💡"  # Added for action plan
}

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.9rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header-icon {
        font-size: 1.8rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    .stButton>button:hover:before {
        left: 100%;
    }
    .info-box {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        padding: 1.8rem;
        border-radius: 15px;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-right: 1px solid #dee2e6;
    }
    .stSelectbox, .stTextInput, .stTextArea, .stRadio {
        background-color: white;
        border-radius: 10px;
        padding: 0.8rem;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stRadio:hover {
        border-color: #4CAF50;
        box-shadow: 0 5px 10px rgba(76, 175, 80, 0.1);
    }
    .stExpander {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border: 1px solid #e0e0e0;
        overflow: hidden;
    }
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px 12px 0 0;
    }
    .inspection-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .location-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin-top: 2rem;
        border-top: 3px solid #4CAF50;
    }
    .data-row {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.2rem 0;
    }
    .check-item {
        font-weight: 600;
        color: #2c3e50;
    }
    .risk-badge {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .yes-no-box {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .table-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 8px 8px 0 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"
if 'translations_cache' not in st.session_state:
    st.session_state.translations_cache = {}

# Translation function using GPT-4o mini
def translate_text(text, target_language="zh"):
    """Translate text using GPT-4o mini with caching"""
    if not text or not text.strip():
        return text
    
    # Check cache first
    cache_key = f"{text}_{target_language}"
    if cache_key in st.session_state.translations_cache:
        return st.session_state.translations_cache[cache_key]
    
    # Don't translate numbers or alphanumeric codes
    if text.strip().replace('.', '').replace(',', '').replace('-', '').isdigit():
        st.session_state.translations_cache[cache_key] = text
        return text
    
    if not openai_client:
        # Fallback to simple translations if no API key
        st.session_state.translations_cache[cache_key] = text
        return text
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {'Chinese (Mandarin)' if target_language == 'zh' else 'English'}. Only return the translation, no explanations. Preserve any numbers, dates, and special formatting."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        translated_text = response.choices[0].message.content.strip()
        st.session_state.translations_cache[cache_key] = translated_text
        return translated_text
    except Exception as e:
        st.warning(f"Translation failed: {str(e)}. Using original text.")
        st.session_state.translations_cache[cache_key] = text
        return text

# Helper function to translate user content
def translate_user_content(text, target_language="zh"):
    """Translate user-filled content to target language"""
    if not text or not text.strip():
        return text
    
    if target_language == "en":
        # If target is English, return as is (assuming user entered in English)
        return text
    
    # Translate to Chinese
    return translate_text(text, target_language)

# Helper function to get translated text with caching
def get_text(key, fallback=None):
    """Get translated text based on current UI language"""
    lang = st.session_state.ui_language
    
    # Base English texts for stitching inspection
    texts = {
        # Titles and Headers
        "title": "Stitching Inspection Report",
        "basic_info": "Basic Information",
        "personnel_stats": "Personnel Statistics",
        "order_info": "Order Information",
        "quality_assessment": "Quality Assessment",
        "outsourcing_check": "Outsourcing Check",
        "signatures": "Signatures",
        
        # Buttons
        "generate_pdf": "Generate Inspection Report",
        "download_pdf": "Download PDF Report",
        
        # Form Fields - Basic Info
        "qc_manager": "QC Manager",
        "qc_inspector": "QC Inspector",
        "factory_name": "Factory Name",
        "inspection_date": "Inspection Date",
        "stitching_lines": "Number of Stitching Lines",
        "workers_quantity": "Number of Workers",
        
        # Personnel Statistics
        "personnel_change": "Personnel Increase/Decrease",
        "add_quantity": "Added Quantity",
        "loss_quantity": "Loss Quantity",
        "change_ratio": "Increase/Decrease Ratio",
        
        # Order Information
        "style_number": "Style Number",
        "ci_po_number": "CI/PO Number",
        "order_quantity": "Order Quantity",
        "lot_number": "Lot Number",
        "lot_quantity": "Lot Quantity",
        "color": "Color",
        "stitched_quantity": "Stitched Quantity",
        
        # Quality Assessment
        "quality_abnormality": "Quality Abnormality Description",
        "action_plan": "Action Plan & Solution",
        
        # Outsourcing Check
        "risk_capacity": "Risk of affecting production capacity due to worker loss",
        "outsourcing_found": "Outsourcing found with records",
        "risk_outsourcing": "Risk of outsourcing shoe uppers due to capacity error",
        "outsourcing_handling": "How to handle outsourcing risk",
        "yes": "Yes",
        "no": "No",
        
        # Signatures
        "grandstep_qc_manager": "GrandStep QC Manager",
        "factory_supervisor": "Factory Stitching Supervisor",
        "grandstep_qc": "GrandStep QC Inspector",
        
        # Footer and Messages
        "footer_text": "Stitching Inspection System",
        "generate_success": "PDF Report Generated Successfully!",
        "fill_required": "Please fill in at least Factory Name and QC Manager!",
        "creating_pdf": "Creating your stitching inspection PDF report...",
        "pdf_details": "PDF Details",
        "report_language": "Report Language",
        "generated": "Generated",
        "location": "Location",
        "error_generating": "Error generating PDF",
        "select_location": "Select Inspection Location",
        "user_interface_language": "User Interface Language",
        "pdf_report_language": "PDF Report Language",
        "test_location": "Inspection Location",
        "local_time": "Local Time",
        "quick_guide": "Quick Guide",
        "powered_by": "Powered by Streamlit",
        "copyright": "© 2025 - Stitching Inspection Platform",
        "disclaimer": "Disclaimer",
        "disclaimer_text": "Note: This inspection report documents current observations and does not guarantee future performance.",
        
        # Instructions
        "instruction_1": "Fill basic factory information",
        "instruction_2": "Record personnel statistics",
        "instruction_3": "Enter order details",
        "instruction_4": "Assess quality and risks",
        "instruction_5": "Complete with signatures",
        
        # Risk Assessment
        "capacity_risk": "Production Capacity Risk",
        "outsourcing_risk": "Outsourcing Risk",
        "quality_issues": "Quality Issues"
    }
    
    text = texts.get(key, fallback or key)
    
    # Translate if needed
    if lang == "zh" and openai_client:
        return translate_text(text, "zh")
    return text

# PDF text based on selected language
def get_pdf_text(key, pdf_lang):
    """Get text for PDF based on selected language"""
    # English texts for PDF
    pdf_texts_en = {
        "title": "Stitching Inspection Report",
        "subtitle": "On-site Stitching Inspection Report",
        "page_num": "Page 1",
        "qc_manager": "QC Manager",
        "qc_inspector": "QC Inspector",
        "factory": "Factory",
        "date": "Date",
        "stitching_lines": "How many stitching lines",
        "workers_qty": "Worker quantity",
        "personnel_change": "Add or loss quantity this month",
        "add_qty": "Add quantity",
        "loss_qty": "Loss quantity",
        "change_ratio": "Increase/decrease ratio",
        
        "order_info": "Order information of on-site stitching",
        "style": "Style",
        "ci_po": "CI/PO Number",
        "order_qty": "Order Quantity",
        "lot": "Lot",
        "lot_qty": "LOT QTY",
        "color": "Color",
        "stitched_qty": "Stitched quantity",
        
        "quality_header": "Is there any abnormality in the on-site quality? If so, please describe",
        "action_plan": "Action Plan & Solution",
        
        "outsourcing_check": "Outsourcing check",
        "no": "No",
        "yes": "Yes",
        
        "risk_capacity": "Is there a risk of affecting production capacity due to the loss of on-site needle workers",
        "outsourcing_found": "Is there any outsourcing of the needle car, and is there a record of outsourcing found",
        "risk_outsourcing": "Does the error between the actual and estimated production capacity of the stitching machine affect the shipment and pose a risk of outsourcing shoe uppers",
        "outsourcing_handling": "If there is a risk of outsourcing, how to handle it",
        
        "signature_gs_qc": "GrandStep QC Manager",
        "signature_factory": "Factory Stitching Supervisor",
        "signature_gs_inspector": "GrandStep QC Inspector",
        
        "header": "STITCHING INSPECTION REPORT",
        "footer_location": "Location",
        "generated": "Generated"
    }
    
    # Chinese texts for PDF
    pdf_texts_zh = {
        "title": "针车巡检表",
        "subtitle": "现场针车巡检报告 （志途 Grand Step）",
        "page_num": "第 1 页",
        "qc_manager": "QC经理",
        "qc_inspector": "验货员",
        "factory": "工厂",
        "date": "日期/时间",
        "stitching_lines": "多少条针车线",
        "workers_qty": "面部有多少人",
        "personnel_change": "当月人员增加还是流失",
        "add_qty": "增加多少人",
        "loss_qty": "流失多少人",
        "change_ratio": "增减比例",
        
        "order_info": "现场针车车的订单信息",
        "style": "款式",
        "ci_po": "单号 CI/PO",
        "order_qty": "订单数量",
        "lot": "批次",
        "lot_qty": "批次数量",
        "color": "颜色",
        "stitched_qty": "已车数量",
        
        "quality_header": "现场品质是否存在异常，如有请描述",
        "action_plan": "处理方式和结果",
        
        "outsourcing_check": "外发检查",
        "no": "没有",
        "yes": "有",
        
        "risk_capacity": "现场针车工人的流失是否有影响产能的风险",
        "outsourcing_found": "针车是否存在外发，发现外发记录",
        "risk_outsourcing": "针车实际产能与预估产能的误差是否影响出货而存在需要外发鞋面的风险",
        "outsourcing_handling": "如果发现存在外发的风险，如何处理",
        
        "signature_gs_qc": "志途QC经理",
        "signature_factory": "工厂针车主管",
        "signature_gs_inspector": "志途QC",
        
        "header": "针车巡检报告",
        "footer_location": "地点",
        "generated": "生成时间"
    }
    
    if pdf_lang == "en":
        return pdf_texts_en.get(key, key)
    else:
        return pdf_texts_zh.get(key, key)

# PDF Generation with Headers and Footers
class StitchingInspectionPDF(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.header_text = kwargs.pop('header_text', '')
        self.location = kwargs.pop('location', '')
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        self.chinese_font = kwargs.pop('chinese_font', 'Helvetica')
        super().__init__(*args, **kwargs)
        
    def afterFlowable(self, flowable):
        """Add header and footer"""
        # Add header on all pages except first
        if self.page > 1:
            self.canv.saveState()
            # Header
            self.canv.setFillColor(colors.HexColor('#4CAF50'))
            self.canv.rect(0, self.pagesize[1] - 0.6*inch, self.pagesize[0], 0.6*inch, fill=1, stroke=0)
            
            # Use Chinese font if needed
            font_size = 12
            if self.pdf_language == "zh":
                self.canv.setFont(self.chinese_font, font_size)
            else:
                self.canv.setFont('Helvetica-Bold', font_size)
                
            self.canv.setFillColor(colors.white)
            header_title = get_pdf_text("header", self.pdf_language)
            self.canv.drawCentredString(
                self.pagesize[0]/2.0, 
                self.pagesize[1] - 0.4*inch, 
                header_title
            )
            self.canv.restoreState()
            
        # Footer on all pages
        self.canv.saveState()
        
        # Footer background
        self.canv.setFillColor(colors.HexColor('#f8f9fa'))
        self.canv.rect(0, 0, self.pagesize[0], 0.7*inch, fill=1, stroke=0)
        
        # Top border
        self.canv.setStrokeColor(colors.HexColor('#4CAF50'))
        self.canv.setLineWidth(1)
        self.canv.line(0, 0.7*inch, self.pagesize[0], 0.7*inch)
        
        # Footer text
        font_size = 8
        if self.pdf_language == "zh":
            self.canv.setFont(self.chinese_font, font_size)
        else:
            self.canv.setFont('Helvetica', font_size)
            
        self.canv.setFillColor(colors.HexColor('#666666'))
        
        # Left: Location
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz)
        
        location_info = f"{get_pdf_text('footer_location', self.pdf_language)}: {self.selected_city}"
        if self.pdf_language == "zh" and self.chinese_city:
            location_info = f"{get_pdf_text('footer_location', self.pdf_language)}: {self.selected_city} ({self.chinese_city})"
        
        self.canv.drawString(0.5*inch, 0.25*inch, location_info)
        
        # Center: Timestamp
        if self.pdf_language == "zh":
            timestamp = f"{get_pdf_text('generated', self.pdf_language)}: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            timestamp = f"{get_pdf_text('generated', self.pdf_language)}: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.canv.drawCentredString(self.pagesize[0]/2.0, 0.25*inch, timestamp)
        
        # Right: Page number
        if self.pdf_language == "zh":
            page_num = f"第 {self.page} 页"
        else:
            page_num = f"Page {self.page}"
        self.canv.drawRightString(self.pagesize[0] - 0.5*inch, 0.25*inch, page_num)
        
        self.canv.restoreState()
def generate_pdf():
    """Generate Stitching Inspection PDF report"""
    buffer = io.BytesIO()
    
    # Get location info
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    # Register Chinese font if needed
    chinese_font = 'Helvetica'
    
    if pdf_lang == "zh":
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            chinese_font = 'STSong-Light'
        except:
            chinese_font = 'Helvetica'
    
    # Create PDF with custom header/footer
    doc = StitchingInspectionPDF(
        buffer, 
        pagesize=A4,
        topMargin=0.7*inch,
        bottomMargin=0.8*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
        header_text=get_pdf_text("header", pdf_lang),
        location=selected_city,
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city,
        chinese_font=chinese_font
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Create styles based on language
    title_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    normal_font = 'Helvetica' if pdf_lang != "zh" else chinese_font
    bold_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=bold_font
    )
    
    # Section header style
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=8,
        alignment=TA_LEFT,
        fontName=bold_font,
        leftIndent=0
    )
    
    # Table cell style
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        fontName=normal_font,
        leading=12
    )
    
    # Normal style
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName=normal_font
    )
    
    # Bold style
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=normal_style,
        fontSize=9,
        fontName=bold_font
    )
    
    # Answer style (for Yes/No)
    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=normal_style,
        fontSize=10,
        fontName=bold_font,
        textColor=colors.HexColor('#2E7D32')
    )
    
    # Helper function for creating paragraphs
    def create_paragraph(text, style=normal_style, bold=False, alignment='LEFT'):
        """Create paragraph with appropriate font"""
        if bold:
            font_name = bold_font
        else:
            font_name = normal_font
        
        align_map = {'LEFT': TA_LEFT, 'CENTER': TA_CENTER, 'RIGHT': TA_RIGHT, 'JUSTIFY': TA_JUSTIFY}
        
        custom_style = ParagraphStyle(
            f"CustomStyle_{bold}_{alignment}",
            parent=style,
            fontName=font_name,
            alignment=align_map.get(alignment, TA_LEFT)
        )
        
        return Paragraph(text, custom_style)
    
    # Helper function to create colored box with border
    def create_section_box(title, content, bg_color='#f8f9fa', border_color='#4CAF50'):
        """Create a professional section with colored background and border"""
        box_elements = []
        
        # Title with background
        title_para = create_paragraph(title, ParagraphStyle(
            'BoxTitle',
            parent=bold_style,
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            fontName=bold_font,
            leftIndent=5
        ), bold=True)
        
        # Content with padding
        content_para = create_paragraph(content, ParagraphStyle(
            'BoxContent',
            parent=normal_style,
            fontSize=9,
            alignment=TA_LEFT,
            fontName=normal_font,
            leftIndent=10,
            rightIndent=10,
            textColor=colors.HexColor('#333333'),
            leading=13
        ))
        
        # Create a table with borders
        box_data = [
            [title_para],
            [content_para]
        ]
        
        box_table = Table(box_data, colWidths=[doc.width])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(bg_color)),
            ('BACKGROUND', (0, 1), (0, 1), colors.white),
            ('BOX', (0, 0), (0, -1), 1, colors.HexColor(border_color)),
            ('INNERGRID', (0, 0), (0, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('VALIGN', (0, 0), (0, -1), 'TOP'),
            ('PADDING', (0, 0), (0, -1), 8),
            ('LEFTPADDING', (0, 0), (0, -1), 10),
            ('RIGHTPADDING', (0, 0), (0, -1), 10),
        ]))
        
        return box_table
    
    # Build the PDF content
    elements.append(Spacer(1, 10))
    
    # Title based on language
    elements.append(Paragraph(get_pdf_text("title", pdf_lang), title_style))
    elements.append(Paragraph(get_pdf_text("subtitle", pdf_lang), subtitle_style))
    elements.append(Spacer(1, 15))
    
    # Get values from session state
    qc_manager_val = st.session_state.get('qc_manager', '')
    qc_inspector_val = st.session_state.get('qc_inspector', '')
    factory_val = st.session_state.get('factory_name', '')
    inspection_date_val = st.session_state.get('inspection_date', datetime.now())
    inspection_time_val = st.session_state.get('inspection_time', datetime.now().time())
    
    # Translate user-filled content if PDF language is Chinese
    if pdf_lang == "zh":
        qc_manager_val = translate_user_content(qc_manager_val, "zh")
        qc_inspector_val = translate_user_content(qc_inspector_val, "zh")
        factory_val = translate_user_content(factory_val, "zh")
    
    # Combine date and time
    if 'inspection_date' in st.session_state and 'inspection_time' in st.session_state:
        combined_datetime = datetime.combine(
            st.session_state.inspection_date,
            st.session_state.inspection_time
        )
        date_display = combined_datetime.strftime('%Y-%m-%d %H:%M')
    else:
        date_display = inspection_date_val.strftime('%Y-%m-%d %H:%M') if hasattr(inspection_date_val, 'strftime') else str(inspection_date_val)
    
    # ===== SECTION 1: BASIC INFORMATION =====
    elements.append(create_paragraph("1. " + get_pdf_text("qc_manager", pdf_lang), section_header_style, bold=True))
    
    # Create a symmetrical 2x2 grid for basic info
    basic_data = [
        [
            create_paragraph(get_pdf_text("qc_manager", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(qc_manager_val or "________________"),
            create_paragraph(get_pdf_text("factory", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(factory_val or "________________")
        ],
        [
            create_paragraph(get_pdf_text("qc_inspector", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(qc_inspector_val or "________________"),
            create_paragraph(get_pdf_text("date", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(date_display)
        ]
    ]
    
    basic_table = Table(basic_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    basic_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e8f5e9')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 15))
    
    # ===== SECTION 2: PERSONNEL STATISTICS =====
    elements.append(create_paragraph("2. " + get_text("personnel_stats"), section_header_style, bold=True))
    
    # Get personnel values
    stitching_lines_val = st.session_state.get('stitching_lines', 0)
    workers_qty_val = st.session_state.get('workers_quantity', 0)
    add_qty_val = st.session_state.get('add_quantity', 0)
    loss_qty_val = st.session_state.get('loss_quantity', 0)
    change_ratio_val = st.session_state.get('change_ratio', '0%')
    personnel_change_val = st.session_state.get('personnel_change', '')
    
    # Create symmetrical personnel table with 3 columns
    personnel_data = [
        [
            create_paragraph(get_pdf_text("stitching_lines", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(str(stitching_lines_val), alignment='CENTER'),
            create_paragraph(get_pdf_text("workers_qty", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(str(workers_qty_val), alignment='CENTER'),
            create_paragraph(get_pdf_text("personnel_change", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(personnel_change_val or "-", alignment='CENTER')
        ],
        [
            create_paragraph(get_pdf_text("add_qty", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(str(add_qty_val), alignment='CENTER'),
            create_paragraph(get_pdf_text("loss_qty", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(str(loss_qty_val), alignment='CENTER'),
            create_paragraph(get_pdf_text("change_ratio", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(change_ratio_val, alignment='CENTER')
        ]
    ]
    
    personnel_table = Table(personnel_data, colWidths=[1.5*inch, 0.8*inch] * 3)
    personnel_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (4, 0), (4, -1), colors.HexColor('#e3f2fd')),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (5, 0), (5, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(personnel_table)
    elements.append(Spacer(1, 15))
    
    # ===== SECTION 3: ORDER INFORMATION =====
    elements.append(create_paragraph("3. " + get_pdf_text("order_info", pdf_lang), section_header_style, bold=True))
    
    # Get order values
    style_val = st.session_state.get('style_number', '')
    ci_po_val = st.session_state.get('ci_po_number', '')
    order_qty_val = st.session_state.get('order_quantity', 0)
    lot_val = st.session_state.get('lot_number', '')
    lot_qty_val = st.session_state.get('lot_quantity', 0)
    color_val = st.session_state.get('color', '')
    stitched_qty_val = st.session_state.get('stitched_quantity', 0)
    
    # Order Information Table - Symmetrical 3x3 grid
    order_data = [
        [
            create_paragraph(get_pdf_text("style", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(style_val or "________________"),
            create_paragraph(get_pdf_text("ci_po", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(ci_po_val or "________________"),
            create_paragraph(get_pdf_text("order_qty", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(str(order_qty_val), alignment='CENTER')
        ],
        [
            create_paragraph(get_pdf_text("lot", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(lot_val or "________________"),
            create_paragraph(get_pdf_text("lot_qty", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(str(lot_qty_val), alignment='CENTER'),
            create_paragraph(get_pdf_text("color", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(color_val or "________________")
        ],
        [
            create_paragraph("", bold_style, bold=True),
            create_paragraph(""),
            create_paragraph(get_pdf_text("stitched_qty", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(str(stitched_qty_val), alignment='CENTER'),
            create_paragraph("", bold_style, bold=True),
            create_paragraph("")
        ]
    ]
    
    order_table = Table(order_data, colWidths=[1.0*inch, 1.5*inch] * 3)
    order_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#fff3e0')),
        ('BACKGROUND', (4, 0), (4, -1), colors.HexColor('#fff3e0')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (0, 2), (1, 2)),  # Span first two cells in last row
        ('SPAN', (4, 2), (5, 2)),  # Span last two cells in last row
    ]))
    elements.append(order_table)
    elements.append(Spacer(1, 20))
    
    # ===== SECTION 4: QUALITY ASSESSMENT =====
    elements.append(create_paragraph("4. " + get_text("quality_assessment"), section_header_style, bold=True))
    elements.append(Spacer(1, 8))
    
    quality_val = st.session_state.get('quality_abnormality', '')
    action_plan_val = st.session_state.get('action_plan', '')
    
    # Translate if needed
    if pdf_lang == "zh":
        quality_val = translate_user_content(quality_val, "zh")
        action_plan_val = translate_user_content(action_plan_val, "zh")
    
    # Create professional box for quality abnormality
    quality_box = create_section_box(
        title=get_pdf_text("quality_header", pdf_lang),
        content=quality_val or "No abnormalities reported.",
        bg_color='#fff3e0',
        border_color='#FF9800'
    )
    elements.append(quality_box)
    elements.append(Spacer(1, 12))
    
    # Create professional box for action plan
    action_box = create_section_box(
        title=get_pdf_text("action_plan", pdf_lang),
        content=action_plan_val or "No action plan required.",
        bg_color='#e8f5e9',
        border_color='#4CAF50'
    )
    elements.append(action_box)
    elements.append(Spacer(1, 20))
    
    # ===== SECTION 5: OUTSOURCING CHECK =====
    elements.append(create_paragraph("5. " + get_pdf_text("outsourcing_check", pdf_lang), section_header_style, bold=True))
    elements.append(Spacer(1, 8))
    
    # Get outsourcing values
    risk_capacity_val = st.session_state.get('risk_capacity', 'No')
    outsourcing_found_val = st.session_state.get('outsourcing_found', 'No')
    risk_outsourcing_val = st.session_state.get('risk_outsourcing', 'No')
    outsourcing_handling_val = st.session_state.get('outsourcing_handling', '')
    
    # Get Yes/No text in appropriate language
    yes_text = get_pdf_text("yes", pdf_lang)
    no_text = get_pdf_text("no", pdf_lang)
    
    # Helper function to get simple Yes/No answer
    def get_simple_answer(value, yes_text, no_text):
        if value == "Yes" or value == "有" or value == yes_text:
            return yes_text
        else:
            return no_text
    
    # Create outsourcing questions with simple Yes/No answers
    outsourcing_data = [
        [
            create_paragraph(get_pdf_text("risk_capacity", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(get_simple_answer(risk_capacity_val, yes_text, no_text), answer_style)
        ],
        [
            create_paragraph(get_pdf_text("outsourcing_found", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(get_simple_answer(outsourcing_found_val, yes_text, no_text), answer_style)
        ],
        [
            create_paragraph(get_pdf_text("risk_outsourcing", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph(get_simple_answer(risk_outsourcing_val, yes_text, no_text), answer_style)
        ]
    ]
    
    outsourcing_table = Table(outsourcing_data, colWidths=[4.5*inch, 1.0*inch])
    outsourcing_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#e8f5e9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('RIGHTPADDING', (1, 0), (1, -1), 10),
    ]))
    elements.append(outsourcing_table)
    elements.append(Spacer(1, 12))
    
    # Create professional box for outsourcing handling
    outsourcing_handling_box = create_section_box(
        title=get_pdf_text("outsourcing_handling", pdf_lang),
        content=outsourcing_handling_val or "No outsourcing risks identified.",
        bg_color='#e3f2fd',
        border_color='#2196F3'
    )
    elements.append(outsourcing_handling_box)
    elements.append(Spacer(1, 25))
    
    # ===== SECTION 6: SIGNATURES =====
    elements.append(create_paragraph("6. " + get_text("signatures"), section_header_style, bold=True))
    elements.append(Spacer(1, 10))
    
    grandstep_qc_val = st.session_state.get('grandstep_qc_manager', '')
    factory_supervisor_val = st.session_state.get('factory_supervisor', '')
    grandstep_inspector_val = st.session_state.get('grandstep_qc', '')
    
    # Translate if needed
    if pdf_lang == "zh":
        grandstep_qc_val = translate_user_content(grandstep_qc_val, "zh")
        factory_supervisor_val = translate_user_content(factory_supervisor_val, "zh")
        grandstep_inspector_val = translate_user_content(grandstep_inspector_val, "zh")
    
    # Create signature table with lines
    signature_data = [
        [
            create_paragraph(get_pdf_text("signature_gs_qc", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph("_________________________", ParagraphStyle('SignatureLine', parent=normal_style, fontSize=9)),
            create_paragraph("Date: ___________________", normal_style)
        ],
        [
            create_paragraph("Name:", bold_style, bold=True),
            create_paragraph(grandstep_qc_val or "", normal_style),
            create_paragraph("", normal_style)
        ],
        [
            Spacer(1, 15),  # Spacer row
            Spacer(1, 15),
            Spacer(1, 15)
        ],
        [
            create_paragraph(get_pdf_text("signature_factory", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph("_________________________", ParagraphStyle('SignatureLine', parent=normal_style, fontSize=9)),
            create_paragraph("Date: ___________________", normal_style)
        ],
        [
            create_paragraph("Name:", bold_style, bold=True),
            create_paragraph(factory_supervisor_val or "", normal_style),
            create_paragraph("", normal_style)
        ],
        [
            Spacer(1, 15),  # Spacer row
            Spacer(1, 15),
            Spacer(1, 15)
        ],
        [
            create_paragraph(get_pdf_text("signature_gs_inspector", pdf_lang) + ":", bold_style, bold=True),
            create_paragraph("_________________________", ParagraphStyle('SignatureLine', parent=normal_style, fontSize=9)),
            create_paragraph("Date: ___________________", normal_style)
        ],
        [
            create_paragraph("Name:", bold_style, bold=True),
            create_paragraph(grandstep_inspector_val or "", normal_style),
            create_paragraph("", normal_style)
        ]
    ]
    
    signature_table = Table(signature_data, colWidths=[2.0*inch, 2.5*inch, 2.0*inch])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (1, 2), (2, 2)),  # Span spacer row
    ]))
    elements.append(signature_table)
    
    # Add final disclaimer
    elements.append(Spacer(1, 20))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        fontName=normal_font,
        italic=True
    )
    elements.append(Paragraph("This inspection report documents current observations and does not guarantee future performance.", disclaimer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Sidebar with enhanced filters
with st.sidebar:
    st.markdown(f'### {ICONS["settings"]} Settings & Filters')
    
    # Language filters with icons
    st.markdown(f'#### {ICONS["language"]} Language Settings')
    ui_language = st.selectbox(
        "User Interface Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select"
    )
    st.session_state.ui_language = "en" if ui_language == "English" else "zh"
    
    pdf_language = st.selectbox(
        "PDF Report Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select"
    )
    st.session_state.pdf_language = "en" if pdf_language == "English" else "zh"
    
    # Location filter with enhanced UI
    st.markdown(f'#### {ICONS["location"]} Location Settings')
    selected_city = st.selectbox(
        "Select Inspection Location",
        list(CHINESE_CITIES.keys()),
        index=list(CHINESE_CITIES.keys()).index(st.session_state.selected_city) 
        if st.session_state.selected_city in CHINESE_CITIES else 0,
        key="city_select"
    )
    st.session_state.selected_city = selected_city
    
    # Display selected location in a badge
    st.markdown(f"""
    <div class="location-badge">
        {ICONS["location"]} {selected_city} ({CHINESE_CITIES[selected_city]})
    </div>
    """, unsafe_allow_html=True)
    
    # Timezone information
    st.markdown(f'#### {ICONS["time"]} Timezone Info')
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    st.metric(
        "Local Time", 
        current_time.strftime('%H:%M:%S'),
        current_time.strftime('%Y-%m-%d')
    )
    
    # Translation status
    if openai_client:
        st.success(f"{ICONS['success']} Translation API: Active")
    else:
        st.warning(f"{ICONS['warning']} Translation API: Not Configured")
    
    st.markdown("---")
    
    # Quick Guide
    st.markdown(f'### {ICONS["info"]} Instructions')
    st.info(f"""
    {ICONS["info"]} **Quick Guide:**
    1. {ICONS["basic_info"]} {get_text("instruction_1")}
    2. {ICONS["personnel"]} {get_text("instruction_2")}
    3. {ICONS["order_info"]} {get_text("instruction_3")}
    4. {ICONS["quality_check"]} {get_text("instruction_4")}
    5. {ICONS["signatures"]} {get_text("instruction_5")}
    """)

# Title with enhanced styling
st.markdown(f"""
<div class="main-header">
    {ICONS["title"]} Stitching Inspection Report
</div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs([
    f"{ICONS['basic_info']} Basic Info",
    f"{ICONS['personnel']} Personnel",
    f"{ICONS['order_info']} Order Info",
    f"{ICONS['quality_check']} Quality & Risks"
])

with tab1:
    # Basic Information Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["basic_info"]}</span>
        {get_text("basic_info")}
    </div>
    """, unsafe_allow_html=True)
    
    # Main basic info in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        qc_manager = st.text_input(
            f"{ICONS['qc']} {get_text('qc_manager')}", 
            placeholder="QC Manager Name",
            key="qc_manager"
        )
        
        factory_name = st.text_input(
            f"{ICONS['factory']} {get_text('factory_name')}", 
            placeholder="Factory Name",
            key="factory_name"
        )
    
    with col2:
        qc_inspector = st.text_input(
            f"{ICONS['qc']} {get_text('qc_inspector')}", 
            placeholder="QC Inspector Name",
            key="qc_inspector"
        )
        
        inspection_date = st.date_input(
            f"{ICONS['time']} {get_text('inspection_date')}", 
            datetime.now(),
            key="inspection_date"
        )
        
        # Time input
        inspection_time = st.time_input(
            f"{ICONS['time']} Inspection Time",
            datetime.now().time(),
            key="inspection_time"
        )
    
    with col3:
        # Combine date and time
        if 'inspection_date' in st.session_state and 'inspection_time' in st.session_state:
            combined_datetime = datetime.combine(
                st.session_state.inspection_date,
                st.session_state.inspection_time
            )
            st.session_state.inspection_datetime = combined_datetime

with tab2:
    # Personnel Statistics Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["personnel"]}</span>
        {get_text("personnel_stats")}
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"{ICONS['info']} Record current personnel statistics and changes.")
    
    # Personnel data in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stitching_lines = st.number_input(
            f"{ICONS['stitching']} {get_text('stitching_lines')}", 
            min_value=0,
            step=1,
            key="stitching_lines"
        )
        
        workers_quantity = st.number_input(
            f"{ICONS['worker']} {get_text('workers_quantity')}", 
            min_value=0,
            step=1,
            key="workers_quantity"
        )
    
    with col2:
        personnel_change = st.selectbox(
            f"{ICONS['personnel']} {get_text('personnel_change')}",
            ["Increase", "Decrease", "Stable"],
            key="personnel_change"
        )
        
        add_quantity = st.number_input(
            f"{ICONS['personnel']} {get_text('add_quantity')}", 
            min_value=0,
            step=1,
            key="add_quantity"
        )
    
    with col3:
        loss_quantity = st.number_input(
            f"{ICONS['personnel']} {get_text('loss_quantity')}", 
            min_value=0,
            step=1,
            key="loss_quantity"
        )
        
        # Calculate change ratio
        if 'add_quantity' in st.session_state and 'loss_quantity' in st.session_state:
            if st.session_state.add_quantity + st.session_state.loss_quantity > 0:
                ratio = (st.session_state.add_quantity - st.session_state.loss_quantity) / (st.session_state.add_quantity + st.session_state.loss_quantity)
                st.session_state.change_ratio = f"{ratio:.2%}"
            else:
                st.session_state.change_ratio = "0%"
        
        st.metric(
            f"{ICONS['ratio']} {get_text('change_ratio')}",
            st.session_state.get('change_ratio', '0%')
        )

with tab3:
    # Order Information Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["order_info"]}</span>
        {get_text("order_info")}
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"{ICONS['info']} Enter details about the order being inspected.")
    
    # Order information in columns
    col1, col2 = st.columns(2)
    
    with col1:
        style_number = st.text_input(
            f"{ICONS['style']} {get_text('style_number')}", 
            placeholder="Style-2024-001",
            key="style_number"
        )
        
        order_quantity = st.number_input(
            f"{ICONS['quantity']} {get_text('order_quantity')}", 
            min_value=0,
            step=1,
            key="order_quantity"
        )
        
        lot_quantity = st.number_input(
            f"{ICONS['quantity']} {get_text('lot_quantity')}", 
            min_value=0,
            step=1,
            key="lot_quantity"
        )
        
        stitched_quantity = st.number_input(
            f"{ICONS['stitching']} {get_text('stitched_quantity')}", 
            min_value=0,
            step=1,
            key="stitched_quantity"
        )
    
    with col2:
        ci_po_number = st.text_input(
            f"{ICONS['order']} {get_text('ci_po_number')}", 
            placeholder="CI-2024-001",
            key="ci_po_number"
        )
        
        lot_number = st.text_input(
            f"{ICONS['lot']} {get_text('lot_number')}", 
            placeholder="LOT-001",
            key="lot_number"
        )
        
        color = st.text_input(
            f"{ICONS['color']} {get_text('color')}", 
            placeholder="Black/White",
            key="color"
        )

with tab4:
    # Quality Assessment and Outsourcing Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["quality_check"]}</span>
        {get_text("quality_assessment")}
    </div>
    """, unsafe_allow_html=True)
    
    quality_abnormality = st.text_area(
        f"{ICONS['abnormality']} {get_text('quality_abnormality')}",
        placeholder="Describe any quality abnormalities found during inspection...",
        height=100,
        key="quality_abnormality"
    )
    
    action_plan = st.text_area(
        f"{ICONS['solution']} {get_text('action_plan')}",
        placeholder="Describe the action plan and solutions for quality issues...",
        height=100,
        key="action_plan"
    )
    
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["outsourcing"]}</span>
        {get_text("outsourcing_check")}
    </div>
    """, unsafe_allow_html=True)
    
    # Risk assessment questions
    st.markdown(f"#### {ICONS['risk']} {get_text('capacity_risk')}")
    risk_capacity = st.radio(
        get_text("risk_capacity"),
        ["No", "Yes"],
        horizontal=True,
        key="risk_capacity"
    )
    
    st.markdown(f"#### {ICONS['risk']} {get_text('outsourcing_risk')}")
    outsourcing_found = st.radio(
        get_text("outsourcing_found"),
        ["No", "Yes"],
        horizontal=True,
        key="outsourcing_found"
    )
    
    risk_outsourcing = st.radio(
        get_text("risk_outsourcing"),
        ["No", "Yes"],
        horizontal=True,
        key="risk_outsourcing"
    )
    
    outsourcing_handling = st.text_area(
        f"{ICONS['check']} {get_text('outsourcing_handling')}",
        placeholder="Describe how outsourcing risks would be handled...",
        height=80,
        key="outsourcing_handling"
    )
    
    # Signatures Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["signatures"]}</span>
        {get_text("signatures")}
    </div>
    """, unsafe_allow_html=True)
    
    # Signatures in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        grandstep_qc_manager = st.text_input(
            f"{ICONS['qc']} {get_text('grandstep_qc_manager')}",
            placeholder="GrandStep QC Manager",
            key="grandstep_qc_manager"
        )
    
    with col2:
        factory_supervisor = st.text_input(
            f"{ICONS['supervisor']} {get_text('factory_supervisor')}",
            placeholder="Factory Supervisor Name",
            key="factory_supervisor"
        )
    
    with col3:
        grandstep_qc = st.text_input(
            f"{ICONS['qc']} {get_text('grandstep_qc')}",
            placeholder="GrandStep QC Inspector",
            key="grandstep_qc"
        )
    
    # Disclaimer
    st.markdown("---")
    st.markdown(f"#### {ICONS['warning']} {get_text('disclaimer')}")
    st.warning(get_text("disclaimer_text"))

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not st.session_state.get('factory_name') or not st.session_state.get('qc_manager'):
            st.error(f"{ICONS['error']} {get_text('fill_required')}")
        else:
            with st.spinner(f"{ICONS['time']} {get_text('creating_pdf')}"):
                try:
                    pdf_buffer = generate_pdf()
                    st.success(f"{ICONS['success']} {get_text('generate_success')}")
                    
                    # Display PDF preview info
                    with st.expander(f"{ICONS['info']} {get_text('pdf_details')}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric(get_text("location"), f"{selected_city} ({CHINESE_CITIES[selected_city]})")
                            st.metric(get_text("report_language"), "Mandarin" if st.session_state.pdf_language == "zh" else "English")
                        with col_info2:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(get_text("generated"), current_time.strftime('%H:%M:%S'))
                    
                    # Download button
                    filename = f"Stitching_Inspection_{st.session_state.get('factory_name', '')}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label=f"{ICONS['download']} {get_text('download_pdf')}",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"{ICONS['error']} {get_text('error_generating')}: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p style='font-size: 1.2rem; font-weight: 600; color: #4CAF50; margin-bottom: 0.5rem;'>
        {ICONS['title']} {get_text('footer_text')}
    </p>
    <p style='font-size: 0.9rem; color: #666666;'>
        {ICONS['location']} {get_text('location')}: {selected_city} ({CHINESE_CITIES[selected_city]}) | 
        {ICONS['language']} {get_text('report_language')}: {'Mandarin' if st.session_state.pdf_language == 'zh' else 'English'}
    </p>
    <p style='font-size: 0.8rem; color: #999999; margin-top: 1rem;'>
        {get_text('powered_by')} | {get_text('copyright')}
    </p>
</div>
""", unsafe_allow_html=True)

# Create .env file instructions in sidebar
with st.sidebar:
    with st.expander(f"{ICONS['info']} API Setup"):
        st.code("""
# Create .env file in your project folder
OPENAI_API_KEY=your-api-key-here
""")
        st.info("Restart the app after adding your API key to enable translations.")
