import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings("ignore")

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Trading - Análisis Técnico",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📈 Dashboard de Trading - Análisis Técnico en Tiempo Real")

# Lista completa de acciones
ACCIONES = [
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

# Filtro de acciones
filtro_texto = st.sidebar.text_input("🔍 Filtrar acciones (escribe parte del símbolo):", "")

# Configuración de alertas
st.sidebar.subheader("🚨 Configuración de Alertas")
alerta_rsi_sobrecompra = st.sidebar.slider("RSI Sobrecompra (>):", 60, 90, 70)
alerta_rsi_sobreventa = st.sidebar.slider("RSI Sobreventa (<):", 10, 40, 30)
alerta_sma_distancia = st.sidebar.slider("Alerta distancia SMA (%):", 5, 20, 10)

# Intervalo de actualización
intervalo_actualizacion = st.sidebar.selectbox(
    "Intervalo de actualización:",
    options=[30, 60, 120, 300],
    index=1,
    format_func=lambda x: f"{x} segundos"
)

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

# Función para obtener datos técnicos
@st.cache_data(ttl=60)  # Cache por 1 minuto
def obtener_datos_tecnicos(simbolos):
    datos_tecnicos = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, simbolo in enumerate(simbolos):
        try:
            status_text.text(f'Obteniendo datos de {simbolo}... ({i+1}/{len(simbolos)})')
            progress_bar.progress((i + 1) / len(simbolos))
            
            ticker = yf.Ticker(simbolo)
            
            # Obtener datos históricos (3 meses para tener suficientes datos para SMA30)
            hist = ticker.history(period="3mo", interval="1d")
            
            if len(hist) >= 30:  # Necesitamos al menos 30 días para SMA30
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
                
                # Determinar alerta de compra según criterios
                alerta_compra = ""
                if precio_actual > sma_30 and rsi < 50:
                    alerta_compra = "🟢 RIESGO BAJO"
                elif precio_actual > sma_20 and rsi >= 50:
                    alerta_compra = "🟡 RIESGO MEDIO"
                elif precio_actual > sma_20:
                    alerta_compra = "🔴 RIESGO ALTO"
                else:
                    alerta_compra = "⚫ SIN SEÑAL"
                
                datos_tecnicos.append({
                    'Símbolo': simbolo,
                    'Precio': precio_actual,
                    'SMA 20': sma_20,
                    'SMA 30': sma_30,
                    '% vs SMA 20': pct_sma_20,
                    '% vs SMA 30': pct_sma_30,
                    'RSI': rsi,
                    'Alerta Compra': alerta_compra
                })
                
        except Exception as e:
            # Continuar con el siguiente símbolo si hay error
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(datos_tecnicos)

# Función para aplicar color a las celdas
def colorear_tabla(val):
    if isinstance(val, (int, float)):
        if val > 70:  # RSI alto o % alto
            return 'background-color: #ffcccc'  # Rojo claro
        elif val < 30:  # RSI bajo o % bajo  
            return 'background-color: #ccffcc'  # Verde claro
        elif val > 0:
            return 'background-color: #e6ffe6'  # Verde muy claro
        elif val < 0:
            return 'background-color: #ffe6e6'  # Rojo muy claro
    return ''

# Filtrar acciones si hay filtro
if filtro_texto:
    acciones_filtradas = [acc for acc in ACCIONES if filtro_texto.upper() in acc.upper()]
else:
    acciones_filtradas = ACCIONES

# Mostrar número de acciones
st.info(f"📊 Monitoreando {len(acciones_filtradas)} acciones")

# Botón de actualización manual
if st.sidebar.button("🔄 Actualizar Datos"):
    st.cache_data.clear()

# Placeholder para la tabla
placeholder = st.empty()

# Loop principal
while True:
    with placeholder.container():
        # Obtener datos técnicos
        if acciones_filtradas:
            df_datos = obtener_datos_tecnicos(acciones_filtradas)
            
            if not df_datos.empty:
                # Contar alertas de compra por tipo
                riesgo_bajo = len(df_datos[df_datos['Alerta Compra'] == "🟢 RIESGO BAJO"])
                riesgo_medio = len(df_datos[df_datos['Alerta Compra'] == "🟡 RIESGO MEDIO"])
                riesgo_alto = len(df_datos[df_datos['Alerta Compra'] == "🔴 RIESGO ALTO"])
                sin_senal = len(df_datos[df_datos['Alerta Compra'] == "⚫ SIN SEÑAL"])
                
                # Mostrar resumen de alertas de compra
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
                
                # Mostrar top alertas por categoría
                if riesgo_bajo > 0:
                    st.subheader("🟢 TOP OPORTUNIDADES - RIESGO BAJO")
                    top_bajo = df_datos[df_datos['Alerta Compra'] == "🟢 RIESGO BAJO"].head(10)
                    st.dataframe(top_bajo[['Símbolo', 'Precio', '% vs SMA 30', 'RSI']], use_container_width=True)
                
                # Preparar tabla para mostrar
                df_display = df_datos.copy()
                
                # Formatear columnas numéricas
                df_display['Precio'] = df_display['Precio'].apply(lambda x: f"${x:.2f}")
                df_display['SMA 20'] = df_display['SMA 20'].apply(lambda x: f"${x:.2f}")
                df_display['SMA 30'] = df_display['SMA 30'].apply(lambda x: f"${x:.2f}")
                df_display['% vs SMA 20'] = df_display['% vs SMA 20'].apply(lambda x: f"{x:+.1f}%")
                df_display['% vs SMA 30'] = df_display['% vs SMA 30'].apply(lambda x: f"{x:+.1f}%")
                df_display['RSI'] = df_display['RSI'].apply(lambda x: f"{x:.1f}")
                
                # Mostrar tabla principal
                st.subheader("📊 Análisis Técnico - Tabla Completa")
                
                # Configurar opciones de visualización
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    height=600,
                    column_config={
                        "Símbolo": st.column_config.TextColumn("Símbolo", width="small"),
                        "Precio": st.column_config.TextColumn("Precio Actual", width="small"),
                        "SMA 20": st.column_config.TextColumn("SMA 20", width="small"),
                        "SMA 30": st.column_config.TextColumn("SMA 30", width="small"),
                        "% vs SMA 20": st.column_config.TextColumn("% vs SMA 20", width="small"),
                        "% vs SMA 30": st.column_config.TextColumn("% vs SMA 30", width="small"),
                        "RSI": st.column_config.TextColumn("RSI", width="small"),
                        "Alerta Compra": st.column_config.TextColumn("🚦 Alerta Compra", width="medium")
                    }
                )
                
                # Estadísticas resumen
                st.subheader("📈 Estadísticas Técnicas")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    sobrecompra = len(df_datos[df_datos['RSI'] > 70])
                    st.metric("RSI > 70 (Sobrecompra)", sobrecompra)
                
                with col2:
                    sobreventa = len(df_datos[df_datos['RSI'] < 30])
                    st.metric("RSI < 30 (Sobreventa)", sobreventa)
                
                with col3:
                    arriba_sma20 = len(df_datos[df_datos['% vs SMA 20'] > 0])
                    st.metric("Arriba de SMA 20", arriba_sma20)
                
                with col4:
                    arriba_sma30 = len(df_datos[df_datos['% vs SMA 30'] > 0])
                    st.metric("Arriba de SMA 30", arriba_sma30)
                
                # Información de actualización
                st.info(f"🕒 Última actualización: {datetime.now().strftime('%H:%M:%S')} | Próxima actualización en {intervalo_actualizacion} segundos")
                
            else:
                st.error("❌ No se pudieron obtener datos. Verifica tu conexión a internet.")
        else:
            st.warning("⚠️ No hay acciones que coincidan con el filtro.")
    
    # Esperar antes de la próxima actualización
    time.sleep(intervalo_actualizacion)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>📊 Dashboard de Trading con Análisis Técnico | Datos: Yahoo Finance</p>
        <p><small>⚠️ SMA = Simple Moving Average | RSI = Relative Strength Index | Solo para fines educativos</small></p>
    </div>
    """, 
    unsafe_allow_html=True
)
