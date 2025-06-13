import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
import threading

warnings.filterwarnings("ignore")

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Trading - Análisis Técnico",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar sesión de requests con reintentos
def crear_sesion_robusta():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Título principal
st.title("📈 Dashboard de Trading - Análisis Técnico en Tiempo Real")

# Lista de acciones optimizada para Heroku (solo las más importantes)
ACCIONES_PRINCIPALES = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "V", "JNJ", "UNH",
    "XOM", "JPM", "PG", "HD", "CVX", "MA", "ABBV", "PFE", "KO", "BAC",
    "AVGO", "PEP", "COST", "DIS", "ABT", "WMT", "LLY", "VZ", "ADBE", "CRM"
]

# Lista intermedia para usuarios avanzados
ACCIONES_INTERMEDIAS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "V", "JNJ", "UNH",
    "XOM", "JPM", "PG", "HD", "CVX", "MA", "ABBV", "PFE", "KO", "BAC",
    "AVGO", "PEP", "COST", "DIS", "ABT", "WMT", "LLY", "VZ", "ADBE", "CRM",
    "NFLX", "TMUS", "INTC", "NKE", "AMD", "T", "QCOM", "IBM", "ORCL", "TXN",
    "UPS", "HON", "SBUX", "INTU", "PYPL", "BABA", "TSM", "UBER", "SPOT", "ZM"
]

# Acciones adicionales para filtro avanzado
ACCIONES_COMPLETAS = [
    "MMM", "ABT", "ABBV", "ANF", "ACN", "ADBE", "JMIA", "AAP", "AMD", "AEG", "AEM", "ABNB", "BABA", "GOOGL", "MO", 
    "AMZN", "ABEV", "AMX", "AAL", "AXP", "AIG", "AMGN", "ADI", "AAPL", "AMAT", "ARCO", "ARKK", "ARM", "ASML", "AZN", 
    "TEAM", "T", "ADP", "AVY", "CAR", "BIDU", "BKR", "BBD", "BSBR", 
    "SAN", "BCS", "B", "BAS", "BAYN", "BRK-B", "BHP", "BBV", "BIOX", "BIIB", "BITF", "BB", "BKNG", "BP", "LND", 
    "BAK", "BRFS", "BMY", "AVGO", "BNG", "C", "CAH", "CCL", "CAT", "CLS", "CX", "EBR", "SCHW", "CVX",
    "CDE", "COIN", "CL", "ELP", "SID","CEG", "GLW", "CAAP", "COST", "CS", "CVS", "DHR", "BSN", "DECK", 
    "DE", "DAL", "DTEA", "DEO", "SPXL", "DOCU", "DOW", "DD", "EOAN", "EBAY", "EA", "LLY", "AKO-B", "ERJ", "XLE", 
    "E", "EFX", "EQNR", "GLD", "ETSY", "XOM", "FNMA", "FDX", "RACE", "XLF", "FSLR", "XLU", "FMX", "F", "FMCC", 
    "FCX", "GRMN", "GE", "GM", "GPRK", "GGB", "GILD", "URA", "GLOB", "GFI", "GT", "PAC", "ASR", "TV", "GSK", 
    "HAL", "HOG", "HMY", "HDB", "HL", "HHPD", "HMC", "HON", "HWM", "HPQ", "HSBC", "HUT", "IBN", 
    "INFY", "ING", "INTC", "IBM", "IFF", "IP", "ISRG", "QQQ", "IBIT", "FXI", "IEUR", "IJH", "ETHA", "EWZ", 
    "EEM", "EWJ", "IBB", "IVW", "IVE", "SLV", "IWM", "ITUB", "JPM", "JD", "JNJ", "JCI", 
    "KB", "KMB", "KGC", "PHG", "KEP", "LRCX", "LVS", "LAR", "LAC", "LYG", "ERIC", "LMT", 
    "MMC", "MRVL", "MA", "MCD", "MUX", "MDT", "MELI", "MBG", "MRK", "META", "MU", "MSFT", "MSTR", 
    "MUFG", "MFG", "MBT", "MRNA", "MDLZ", "MSI", "NGG", "NTES", "NFLX", "NEM", "NXE", 
    "NKE", "NIO", "NSAN", "NOKA", "NMR", "NG", "NVS", "NLM", "NUE", "NVDA", "OXY", "ORCL", "ORLY", "PCAR", 
    "PAGS", "PLTR", "PANW", "PAAS", "PYPL", "PDD", "PSO", "PEP", "PBR", "PTR", "PFE", 
    "PM", "PSX", "PINS", "PBI", "PKS", "PG", "SH", "PSQ", "QCOM", "RTX", "RGTI", "RIO", "RIOT", "RBLX", "ROKU", 
    "ROST", "SHEL", "SPGI", "CRM", "SMSN", "SAP", "SATL", "SLB", "SE", "NOW", "SHOP", "SIEGY", "SI", "SWKS", 
    "SNAP", "SNA", "SNOW", "SONY", "SCCO", "DIA", "SPY", "SPOT", "XYZ", "SBUX", "STLA", "STNE", "SDA", 
    "SUZ", "SYY", "TSM", "TGT", "TTM", "TIIAY", "VIV", "TEFO", "TEM", 
    "TEN", "TXR", "TSLA", "TXN", "BK", "BA", "KO", "XLC", "XLY", "XLP", "GS", "XLV", "HSY", "HD", "XLI", 
    "XLB", "MOS", "XLRE", "XLK", "TRVV", "DIS", "TMO", "TIMB", "TJX", "TMUS", "TTE", "TM", "TCOM", "TRIP", 
    "TWLO", "USB", "UBER", "PATH", "UGP", "UL", "UNP", "UAL", "X", "UNH", "UPST", "URBN", "XLU", "VALE", 
    "VIG", "VEA", "SMH", "VRSN", "VZ", "VRTX", "SPCE", "V", "VIST", "VST", "VOD", "WBA", "WMT", 
    "WBO", "WFC", "XROX", "XP", "XPEV", "YZCA", "YELP", "ZM"
]

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Modo de operación
modo_operacion = st.sidebar.selectbox(
    "Modo de Operación:",
    ["Ultra Rápido (30 acciones)", "Rápido (50 acciones)", "Completo (100+ acciones)", "Personalizado"]
)

# Selección de acciones según modo
if modo_operacion == "Ultra Rápido (30 acciones)":
    acciones_seleccionadas = ACCIONES_PRINCIPALES
    st.sidebar.success("🚀 Modo ultra rápido: ~30 segundos")
elif modo_operacion == "Rápido (50 acciones)":
    acciones_seleccionadas = ACCIONES_INTERMEDIAS
    st.sidebar.info("⚡ Modo rápido: ~60 segundos")
elif modo_operacion == "Completo (100+ acciones)":
    acciones_seleccionadas = ACCIONES_COMPLETAS
    st.sidebar.warning("⏳ Modo completo: 2-5 minutos")
else:
    filtro_texto = st.sidebar.text_input("🔍 Símbolos (separados por coma):", "AAPL,MSFT,GOOGL,AMZN,TSLA")
    if filtro_texto:
        acciones_seleccionadas = [acc.strip().upper() for acc in filtro_texto.split(",")]
    else:
        acciones_seleccionadas = ACCIONES_PRINCIPALES

# Límite de acciones para evitar timeouts (más conservador)
max_acciones = st.sidebar.slider("Máximo de acciones a procesar:", 5, 50, 30)
acciones_seleccionadas = acciones_seleccionadas[:max_acciones]

# Configuración de alertas
st.sidebar.subheader("🚨 Configuración de Alertas")
alerta_rsi_sobrecompra = st.sidebar.slider("RSI Sobrecompra (>):", 60, 90, 70)
alerta_rsi_sobreventa = st.sidebar.slider("RSI Sobreventa (<):", 10, 40, 30)

# Función para calcular SMA
def calcular_sma(datos, periodo):
    return datos.rolling(window=periodo).mean()

# Función para calcular RSI
def calcular_rsi(datos, periodo=14):
    delta = datos.diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
    rs = ganancia / perdida
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Función para obtener datos de una sola acción (con manejo de errores robusto)
def obtener_datos_accion(simbolo, timeout=10):
    try:
        # Configurar yfinance con timeout
        ticker = yf.Ticker(simbolo)
        
        # Obtener datos históricos con timeout reducido
        hist = ticker.history(period="2mo", interval="1d", timeout=timeout)
        
        if len(hist) >= 30:
            # Precio actual
            precio_actual = hist['Close'].iloc[-1]
            
            # Calcular SMAs
            sma_20 = calcular_sma(hist['Close'], 20).iloc[-1]
            sma_30 = calcular_sma(hist['Close'], 30).iloc[-1]
            
            # Calcular RSI
            rsi = calcular_rsi(hist['Close']).iloc[-1]
            
            # Calcular porcentajes respecto a SMAs
            pct_sma_20 = ((precio_actual - sma_20) / sma_20) * 100
            pct_sma_30 = ((precio_actual - sma_30) / sma_30) * 100
            
            # Determinar alerta de compra
            if precio_actual > sma_30 and rsi < 50:
                alerta_compra = "🟢 RIESGO BAJO"
            elif precio_actual > sma_20 and rsi >= 50:
                alerta_compra = "🟡 RIESGO MEDIO"
            elif precio_actual > sma_20:
                alerta_compra = "🔴 RIESGO ALTO"
            else:
                alerta_compra = "⚫ SIN SEÑAL"
            
            return {
                'Símbolo': simbolo,
                'Precio': precio_actual,
                'SMA 20': sma_20,
                'SMA 30': sma_30,
                '% vs SMA 20': pct_sma_20,
                '% vs SMA 30': pct_sma_30,
                'RSI': rsi,
                'Alerta Compra': alerta_compra,
                'Status': 'OK'
            }
    except Exception as e:
        return {
            'Símbolo': simbolo,
            'Status': 'ERROR',
            'Error': str(e)
        }

# Función para obtener datos técnicos con procesamiento optimizado para Heroku
def obtener_datos_tecnicos(simbolos, max_workers=3):
    datos_tecnicos = []
    errores = []
    
    # Crear barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Procesar en lotes más pequeños para Heroku
    lote_size = 5  # Reducido para mejor rendimiento en Heroku
    total_lotes = len(simbolos) // lote_size + (1 if len(simbolos) % lote_size else 0)
    
    for i in range(0, len(simbolos), lote_size):
        lote_actual = i // lote_size + 1
        lote_simbolos = simbolos[i:i+lote_size]
        
        status_text.text(f'📊 Lote {lote_actual}/{total_lotes} - Procesando {len(lote_simbolos)} acciones...')
        
        # Usar ThreadPoolExecutor con menos workers para Heroku
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todas las tareas con timeout más corto
            future_to_symbol = {
                executor.submit(obtener_datos_accion, simbolo, 10): simbolo 
                for simbolo in lote_simbolos
            }
            
            # Recoger resultados con timeout total por lote
            try:
                for future in concurrent.futures.as_completed(future_to_symbol, timeout=25):
                    resultado = future.result()
                    if resultado.get('Status') == 'OK':
                        datos_tecnicos.append(resultado)
                    else:
                        errores.append(resultado)
            except concurrent.futures.TimeoutError:
                st.warning(f"⏰ Timeout en lote {lote_actual}")
                break
        
        # Actualizar progreso
        progress_bar.progress(min(1.0, (i + lote_size) / len(simbolos)))
        
        # Pequeña pausa entre lotes para no sobrecargar
        time.sleep(0.5)
    
    progress_bar.empty()
    status_text.empty()
    
    # Mostrar estadísticas
    total_exitosas = len(datos_tecnicos)
    total_errores = len(errores)
    
    if total_exitosas > 0:
        st.success(f"✅ {total_exitosas} acciones procesadas exitosamente")
    
    if total_errores > 0:
        st.warning(f"⚠️ {total_errores} acciones con errores")
        if st.expander("🔍 Ver detalles de errores"):
            for error in errores[:3]:  # Mostrar solo los primeros 3
                st.text(f"• {error['Símbolo']}: {error.get('Error', 'Error desconocido')[:50]}...")
    
    return pd.DataFrame(datos_tecnicos)

# Función principal para mostrar el dashboard
def mostrar_dashboard():
    st.info(f"📊 Procesando {len(acciones_seleccionadas)} acciones...")
    
    # Obtener datos
    df_datos = obtener_datos_tecnicos(acciones_seleccionadas)
    
    if df_datos.empty:
        st.error("❌ No se pudieron obtener datos. Posibles causas:")
        st.error("- Problemas de conectividad")
        st.error("- Límites de la API de Yahoo Finance")
        st.error("- Símbolos incorrectos")
        st.info("💡 Intenta con menos acciones o usa el modo 'Acciones Principales'")
        return
    
    # Estadísticas de éxito
    total_procesadas = len(df_datos)
    st.success(f"✅ Datos obtenidos exitosamente de {total_procesadas} acciones")
    
    # Contar alertas de compra por tipo
    riesgo_bajo = len(df_datos[df_datos['Alerta Compra'] == "🟢 RIESGO BAJO"])
    riesgo_medio = len(df_datos[df_datos['Alerta Compra'] == "🟡 RIESGO MEDIO"])
    riesgo_alto = len(df_datos[df_datos['Alerta Compra'] == "🔴 RIESGO ALTO"])
    sin_senal = len(df_datos[df_datos['Alerta Compra'] == "⚫ SIN SEÑAL"])
    
    # Mostrar resumen de alertas
    st.subheader("🚦 RESUMEN DE ALERTAS DE COMPRA")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.success(f"**🟢 RIESGO BAJO**\n{riesgo_bajo} acciones")
        st.caption("Precio > SMA30 y RSI < 50")
    
    with col2:
        st.warning(f"**🟡 RIESGO MEDIO**\n{riesgo_medio} acciones")
        st.caption("Precio > SMA20 y RSI ≥ 50")
    
    with col3:
        st.error(f"**🔴 RIESGO ALTO**\n{riesgo_alto} acciones")
        st.caption("Precio > SMA20 solamente")
    
    with col4:
        st.info(f"**⚫ SIN SEÑAL**\n{sin_senal} acciones")
        st.caption("Precio ≤ SMA20")
    
    # Mostrar top oportunidades
    if riesgo_bajo > 0:
        st.subheader("🟢 TOP OPORTUNIDADES - RIESGO BAJO")
        top_bajo = df_datos[df_datos['Alerta Compra'] == "🟢 RIESGO BAJO"].head(10)
        st.dataframe(
            top_bajo[['Símbolo', 'Precio', '% vs SMA 30', 'RSI']].round(2),
            use_container_width=True
        )
    
    # Preparar tabla principal
    df_display = df_datos.copy()
    
    # Formatear columnas numéricas
    df_display['Precio'] = df_display['Precio'].apply(lambda x: f"${x:.2f}")
    df_display['SMA 20'] = df_display['SMA 20'].apply(lambda x: f"${x:.2f}")
    df_display['SMA 30'] = df_display['SMA 30'].apply(lambda x: f"${x:.2f}")
    df_display['% vs SMA 20'] = df_display['% vs SMA 20'].apply(lambda x: f"{x:+.1f}%")
    df_display['% vs SMA 30'] = df_display['% vs SMA 30'].apply(lambda x: f"{x:+.1f}%")
    df_display['RSI'] = df_display['RSI'].apply(lambda x: f"{x:.1f}")
    
    # Eliminar columnas de control
    df_display = df_display.drop(['Status'], axis=1, errors='ignore')
    
    # Mostrar tabla principal
    st.subheader("📊 Análisis Técnico - Tabla Completa")
    st.dataframe(
        df_display,
        use_container_width=True,
        height=600
    )
    
    # Estadísticas técnicas
    st.subheader("📈 Estadísticas Técnicas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sobrecompra = len(df_datos[df_datos['RSI'] > alerta_rsi_sobrecompra])
        st.metric(f"RSI > {alerta_rsi_sobrecompra} (Sobrecompra)", sobrecompra)
    
    with col2:
        sobreventa = len(df_datos[df_datos['RSI'] < alerta_rsi_sobreventa])
        st.metric(f"RSI < {alerta_rsi_sobreventa} (Sobreventa)", sobreventa)
    
    with col3:
        arriba_sma20 = len(df_datos[df_datos['% vs SMA 20'] > 0])
        st.metric("Arriba de SMA 20", arriba_sma20)
    
    with col4:
        arriba_sma30 = len(df_datos[df_datos['% vs SMA 30'] > 0])
        st.metric("Arriba de SMA 30", arriba_sma30)
    
    # Información de actualización
    st.info(f"🕒 Actualización completada: {datetime.now().strftime('%H:%M:%S')}")

# Botón de actualización
if st.button("🔄 Actualizar Dashboard", type="primary"):
    mostrar_dashboard()
else:
    st.info("👆 Haz clic en 'Actualizar Dashboard' para obtener los datos más recientes")
    
    # Mostrar dashboard automáticamente si es la primera vez
    if 'dashboard_loaded' not in st.session_state:
        st.session_state.dashboard_loaded = True
        mostrar_dashboard()

# Información adicional
st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Información")
st.sidebar.info("""
**Recomendaciones para Heroku:**
- **Ultra Rápido**: 30 acciones (~30 seg)
- **Rápido**: 50 acciones (~1 min)
- **Máximo recomendado**: 30-40 acciones

**Indicadores:**
- **SMA**: Media Móvil Simple
- **RSI**: Índice de Fuerza Relativa
- **Riesgo Bajo**: Precio > SMA30 y RSI < 50
""")

st.sidebar.warning("⚠️ Solo para fines educativos. No es consejo financiero.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>📊 Dashboard de Trading con Análisis Técnico | Datos: Yahoo Finance</p>
        <p><small>Optimizado para Heroku | Versión: 2.0</small></p>
    </div>
    """, 
    unsafe_allow_html=True
)
