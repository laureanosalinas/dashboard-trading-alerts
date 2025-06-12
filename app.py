import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
import requests
warnings.filterwarnings("ignore")

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Trading - Análisis Técnico",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar session para evitar bloqueos
@st.cache_resource
def get_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

# Lista completa de acciones
ACCIONES = [
    "MMM", "ABT", "ABBV", "ANF", "ACN", "ADBE", "JMIA", "AAP", "AMD", "AEG", "AEM", "ABNB", "BABA", "GOOGL", "MO", 
    "AMZN", "ABEV", "AMX", "AAL", "AXP", "AIG", "AMGN", "ADI", "AAPL", "AMAT", "ARCO", "ARKK", "ARM", "ASML", "AZN", 
    "TEAM", "T", "ADP", "AVY", "CAR", "BIDU", "BKR", "BBD", "BBDC3.SA", "BPA11.SA", "BBAS3.SA", "ITUB3.SA", "BSBR", 
    "SAN", "BCS", "B", "BAS", "BAYN", "BRK-B", "BHP", "BBV", "BIOX", "BIIB", "BITF", "BB", "BKNG", "BP", "LND", 
    "BAK", "BRFS", "BMY", "AVGO", "BNG", "C", "CAH", "CCL", "CAT", "CLS", "CX", "EBR", "SCHW", "CVX", "SBSP3.SA", 
    "CDE", "COIN", "CL", "ELP", "SID", "CSNA3.SA", "CEG", "GLW", "CAAP", "COST", "CS", "CVS", "DHR", "BSN", "DECK", 
    "DE", "DAL", "DTEA", "DEO", "SPXL", "DOCU", "DOW", "DD", "EOAN", "EBAY", "EA", "LLY", "AKO-B", "ERJ", "XLE", 
    "E", "EFX", "EQNR", "GLD", "ETSY", "XOM", "FNMA", "FDX", "RACE", "XLF", "FSLR", "XLU", "FMX", "F", "FMCC", 
    "FCX", "GRMN", "GE", "GM", "GPRK", "GGB", "GILD", "URA", "GLOB", "GFI", "GT", "PAC", "ASR", "TV", "GSK", 
    "HAL", "HAPV3.SA", "HOG", "HMY", "HDB", "HL", "HHPD", "HMC", "HON", "HWM", "HPQ", "HSBC", "HUT", "IBN", 
    "INFY", "ING", "INTC", "IBM", "IFF", "IP", "ISRG", "QQQ", "IBIT", "FXI", "IEUR", "IJH", "ETHA", "EWZ", 
    "EEM", "EWJ", "IBB", "IVW", "IVE", "SLV", "IWM", "ITUB", "JPM", "JBSS3.SA", "JD", "JNJ", "JCI", "JOYY", 
    "KB", "KMB", "KGC", "PHG", "KEP", "LRCX", "LVS", "LAR", "LAC", "LYG", "ERIC", "RENT3.SA", "LMT", "LREN3.SA", 
    "MGLU3.SA", "MMC", "MRVL", "MA", "MCD", "MUX", "MDT", "MELI", "MBG", "MRK", "META", "MU", "MSFT", "MSTR", 
    "MUFG", "MFG", "MBT", "MRNA", "MDLZ", "MSI", "NGG", "NTCO3.SA", "NEC1", "NTES", "NFLX", "NEM", "NXE", 
    "NKE", "NIO", "NSAN", "NOKA", "NMR", "NG", "NVS", "NLM", "NUE", "NVDA", "OXY", "ORCL", "ORLY", "PCAR", 
    "PAGS", "PLTR", "PANW", "PAAS", "PYPL", "PDD", "PSO", "PEP", "PRIO3.SA", "PETR3.SA", "PBR", "PTR", "PFE", 
    "PM", "PSX", "PINS", "PBI", "PKS", "PG", "SH", "PSQ", "QCOM", "RTX", "RGTI", "RIO", "RIOT", "RBLX", "ROKU", 
    "ROST", "SHEL", "SPGI", "CRM", "SMSN", "SAP", "SATL", "SLB", "SE", "NOW", "SHOP", "SIEGY", "SI", "SWKS", 
    "SNAP", "SNA", "SNOW", "SONY", "SCCO", "DIA", "SPY", "SPOT", "XYZ", "SBUX", "STLA", "STNE", "SDA", 
    "SUZB3.SA", "SUZ", "SYY", "TSM", "TGT", "TTM", "TIIAY", "VIV", "VIVT3.SA", "TEFO", "TIMS3.SA", "TEM", 
    "TEN", "TXR", "TSLA", "TXN", "BK", "BA", "KO", "XLC", "XLY", "XLP", "GS", "XLV", "HSY", "HD", "XLI", 
    "XLB", "MOS", "XLRE", "XLK", "TRVV", "DIS", "TMO", "TIMB", "TJX", "TMUS", "TTE", "TM", "TCOM", "TRIP", 
    "TWLO", "USB", "UBER", "PATH", "UGP", "UL", "UNP", "UAL", "X", "UNH", "UPST", "URBN", "XLU", "VALE", 
    "VALE3.SA", "VIG", "VEA", "SMH", "VRSN", "VZ", "VRTX", "SPCE", "V", "VIST", "VST", "VOD", "WBA", "WMT", 
    "WEGE3.SA", "WBO", "WFC", "XROX", "XP", "XPEV", "YZCA", "YELP", "ZM"
]

# Función optimizada para descargar datos en lotes
@st.cache_data(ttl=300)  # Cache por 5 minutos
def descargar_datos_lotes(simbolos, lote_size=30):
    """Descarga datos en lotes para evitar saturar la conexión"""
    session = get_session()
    datos_completos = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_lotes = len(simbolos) // lote_size + (1 if len(simbolos) % lote_size else 0)
    
    for i, lote_inicio in enumerate(range(0, len(simbolos), lote_size)):
        lote = simbolos[lote_inicio:lote_inicio + lote_size]
        
        try:
            status_text.text(f'Descargando lote {i+1} de {total_lotes}... ({len(lote)} acciones)')
            
            # Descargar con timeout y retry
            data = yf.download(
                lote, 
                period="5d",  # Usar menos días para ser más rápido
                interval="1d",
                group_by='ticker',
                auto_adjust=True,
                prepost=True,
                threads=True,
                session=session,
                timeout=20
            )
            
            if not data.empty:
                # Si es solo una acción, yfinance no agrupa por ticker
                if len(lote) == 1:
                    datos_completos[lote[0]] = data
                else:
                    # Múltiples acciones
                    for simbolo in lote:
                        if simbolo in data.columns.levels[0]:
                            datos_completos[simbolo] = data[simbolo]
            
            # Actualizar progress bar
            progress_bar.progress((i + 1) / total_lotes)
            
            # Pausa entre lotes para evitar rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            st.warning(f"Error en lote {i+1}: {str(e)[:100]}...")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return datos_completos

# Función para procesar los datos y calcular indicadores
def procesar_datos(datos_dict):
    """Procesa los datos descargados y calcula indicadores técnicos"""
    resultados = []
    
    for simbolo, data in datos_dict.items():
        try:
            if data.empty or len(data) < 2:
                continue
                
            # Obtener último precio y precio anterior
            ultimo_precio = data['Close'].iloc[-1]
            precio_anterior = data['Close'].iloc[-2] if len(data) > 1 else ultimo_precio
            cambio_pct = ((ultimo_precio - precio_anterior) / precio_anterior) * 100
            
            # Calcular RSI simple (14 períodos)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_actual = rsi.iloc[-1] if not rsi.empty else 50
            
            # Determinar señal
            señal = "NEUTRAL"
            if rsi_actual < 30 and cambio_pct > 0:
                señal = "COMPRA"
            elif rsi_actual > 70 and cambio_pct < 0:
                señal = "VENTA"
            
            resultados.append({
                'Símbolo': simbolo,
                'Precio': ultimo_precio,
                'Cambio %': cambio_pct,
                'RSI': rsi_actual,
                'Señal': señal
            })
            
        except Exception as e:
            continue
    
    return pd.DataFrame(resultados)

# INTERFAZ PRINCIPAL
st.title("📈 Dashboard de Trading - Análisis Técnico en Tiempo Real")

# Sidebar para controles
st.sidebar.header("🎛️ Controles")

# Botón para actualizar datos
if st.sidebar.button("🔄 Actualizar Datos", type="primary"):
    st.cache_data.clear()

# Número de acciones a procesar
num_acciones = st.sidebar.slider("Número de acciones a analizar:", 50, 263, 100)
acciones_seleccionadas = ACCIONES[:num_acciones]

# Mostrar información
st.sidebar.info(f"📊 Analizando {len(acciones_seleccionadas)} acciones")

# PROCESAMIENTO PRINCIPAL
try:
    with st.spinner("🔄 Descargando y procesando datos..."):
        # Descargar datos
        datos_dict = descargar_datos_lotes(acciones_seleccionadas)
        
        if not datos_dict:
            st.error("❌ No se pudieron obtener datos. Verifica tu conexión a internet.")
            st.stop()
        
        # Procesar datos
        df_resultados = procesar_datos(datos_dict)
        
        if df_resultados.empty:
            st.warning("⚠️ No se pudieron procesar los datos obtenidos.")
            st.stop()
    
    # MOSTRAR RESULTADOS
    st.success(f"✅ Datos actualizados exitosamente - {len(df_resultados)} acciones procesadas")
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Acciones", len(df_resultados))
    with col2:
        compras = len(df_resultados[df_resultados['Señal'] == 'COMPRA'])
        st.metric("Señales COMPRA", compras)
    with col3:
        ventas = len(df_resultados[df_resultados['Señal'] == 'VENTA'])
        st.metric("Señales VENTA", ventas)
    with col4:
        neutral = len(df_resultados[df_resultados['Señal'] == 'NEUTRAL'])
        st.metric("Neutral", neutral)
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_señal = st.selectbox("Filtrar por señal:", ["TODAS", "COMPRA", "VENTA", "NEUTRAL"])
    
    # Aplicar filtros
    df_filtrado = df_resultados.copy()
    if filtro_señal != "TODAS":
        df_filtrado = df_filtrado[df_filtrado['Señal'] == filtro_señal]
    
    # Mostrar tabla
    st.subheader("📋 Resultados del Análisis")
    
    # Formatear la tabla
    df_display = df_filtrado.copy()
    df_display['Precio'] = df_display['Precio'].apply(lambda x: f"${x:.2f}")
    df_display['Cambio %'] = df_display['Cambio %'].apply(lambda x: f"{x:+.2f}%")
    df_display['RSI'] = df_display['RSI'].apply(lambda x: f"{x:.1f}")
    
    # Aplicar colores según la señal
    def colorizar_señal(val):
        if val == 'COMPRA':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'VENTA':
            return 'background-color: #f8d7da; color: #721c24'
        else:
            return 'background-color: #fff3cd; color: #856404'
    
    st.dataframe(
        df_display.style.map(colorizar_señal, subset=['Señal']),
        use_container_width=True,
        height=400
    )
    
    # Información adicional
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Información:**")
    st.sidebar.markdown("- RSI < 30: Posible sobreventa")
    st.sidebar.markdown("- RSI > 70: Posible sobrecompra") 
    st.sidebar.markdown("- Datos se actualizan cada 5 minutos")
    
except Exception as e:
    st.error(f"❌ Error general: {str(e)}")
    st.info("🔧 Intenta reducir el número de acciones o actualizar los datos.")
