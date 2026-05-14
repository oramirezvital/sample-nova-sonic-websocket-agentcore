import os
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from strands.experimental.bidi import BidiAgent
from strands.experimental.bidi.models import BidiNovaSonicModel
from strands.experimental.bidi.tools import stop_conversation
from strands import tool

# Environment configuration
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-2-sonic-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
INPUT_SAMPLE_RATE = int(os.getenv("INPUT_SAMPLE_RATE", "16000"))
OUTPUT_SAMPLE_RATE = int(os.getenv("OUTPUT_SAMPLE_RATE", "16000"))
CHANNELS = int(os.getenv("CHANNELS", "1"))
FORMAT = os.getenv("FORMAT", "pcm")

# Create FastAPI app
app = FastAPI()

# ============================================================
# STORI FINANCIAL COACH TOOLS
# ============================================================

@tool
def consultar_saldo_y_pagos(cliente_id: str) -> str:
    """
    Consulta el saldo actual, fecha de corte y fecha límite de pago del cliente.
    
    Args:
        cliente_id: Identificador del cliente Stori
    
    Returns:
        Información del estado de cuenta del cliente
    """
    return (
        "Estado de cuenta de María García: "
        "Saldo actual: 4,850 pesos. "
        "Límite de crédito: 12,000 pesos. "
        "Crédito disponible: 7,150 pesos. "
        "Fecha de corte: 15 de cada mes. "
        "Fecha límite de pago: 5 de cada mes. "
        "Pago mínimo: 485 pesos. "
        "Pago para no generar intereses: 4,850 pesos. "
        "Próximo pago vence: 5 de julio de 2025. "
        "Tasa de interés anual: 59.9%. "
        "Días restantes para pagar: 12 días."
    )

@tool
def consultar_historial_crediticio(cliente_id: str) -> str:
    """
    Consulta el progreso del historial crediticio del cliente en Buró de Crédito.
    
    Args:
        cliente_id: Identificador del cliente Stori
    
    Returns:
        Resumen del historial crediticio y score
    """
    return (
        "Historial crediticio de María García: "
        "Score Buró de Crédito: 620 (Regular, en mejora). "
        "Score hace 6 meses: 580. "
        "Mejora: +40 puntos en 6 meses. "
        "Meses consecutivos pagando a tiempo: 5. "
        "Pagos atrasados últimos 12 meses: 1 (hace 7 meses). "
        "Utilización de crédito: 40% (recomendado: menos de 30%). "
        "Antigüedad de cuenta: 8 meses. "
        "Siguiente meta: 650 puntos (buen historial). "
        "Consejo: Pagar más del mínimo y mantener utilización bajo 30% "
        "te ayudará a llegar a 650 en aproximadamente 3 meses."
    )

@tool
def consultar_cashback_y_recompensas(cliente_id: str) -> str:
    """
    Consulta las recompensas de cashback acumuladas y categorías activas.
    
    Args:
        cliente_id: Identificador del cliente Stori
    
    Returns:
        Información de cashback y recompensas disponibles
    """
    return (
        "Recompensas de María García: "
        "Cashback acumulado este mes: 127.50 pesos. "
        "Cashback total histórico: 890 pesos. "
        "Categorías activas con cashback: "
        "Supermercados: 5% (hasta 200 pesos de cashback). "
        "Gasolina: 3% (hasta 150 pesos de cashback). "
        "Compras en línea: 2% (sin límite). "
        "Categoría estrella esta semana: Farmacias 10% (válido hasta domingo). "
        "Próximo depósito de cashback: 16 de julio. "
        "Tip: Usa tu Stori en farmacias esta semana para aprovechar el 10%."
    )

@tool
def simular_pago(monto: str, tipo_pago: str) -> str:
    """
    Simula el impacto de diferentes montos de pago en intereses y score crediticio.
    
    Args:
        monto: Monto a simular en pesos (ej: "1000", "pago_minimo", "total")
        tipo_pago: Tipo de simulación: "impacto_intereses" o "impacto_score"
    
    Returns:
        Simulación del impacto del pago
    """
    if monto == "pago_minimo" or monto == "485":
        return (
            "Simulación del pago mínimo de 485 pesos: "
            "Saldo restante: 4,365 pesos. "
            "Intereses que se generarán: 217.50 pesos. "
            "Nuevo saldo siguiente mes: 4,582.50 pesos. "
            "Tiempo para liquidar pagando solo mínimo: 14 meses. "
            "Total que pagarías: 6,790 pesos (39% más). "
            "Impacto en score: Neutral (no sube ni baja). "
            "Recomendación: Si puedes pagar 1,500 pesos, "
            "reducirías los intereses a 133 pesos y liquidarías en 4 meses."
        )
    elif monto == "total" or monto == "4850":
        return (
            "Simulación del pago total de 4,850 pesos: "
            "Saldo restante: 0 pesos. "
            "Intereses que se generarán: 0 pesos. "
            "Crédito disponible: 12,000 pesos. "
            "Impacto en score: Positivo (+5 a +10 puntos). "
            "Utilización de crédito: 0% (excelente). "
            "Excelente decisión! Pagar el total es la mejor forma "
            "de construir historial sin pagar intereses."
        )
    else:
        try:
            monto_num = int(monto)
            saldo_restante = 4850 - monto_num
            intereses = saldo_restante * 0.05
            utilizacion = (saldo_restante / 12000) * 100
            return (
                f"Simulación de un pago de {monto_num:,} pesos: "
                f"Saldo restante: {saldo_restante:,} pesos. "
                f"Intereses sobre saldo restante: aproximadamente {intereses:.0f} pesos. "
                "Impacto en score: Ligeramente positivo. "
                f"Utilización después del pago: {utilizacion:.0f}%. "
                "Tip: Entre más pagues arriba del mínimo, menos intereses generas "
                "y más rápido crece tu score."
            )
        except ValueError:
            return "No pude entender el monto. Puedes decirme cuántos pesos quieres simular?"

@tool
def obtener_tips_financieros(tema: str) -> str:
    """
    Proporciona consejos financieros personalizados sobre un tema específico.
    
    Args:
        tema: Tema del consejo: "ahorro", "credito", "deudas", "presupuesto", "emergencias"
    
    Returns:
        Consejos financieros personalizados
    """
    tips = {
        "credito": (
            "Tips para mejorar tu historial crediticio: "
            "Primero, paga siempre antes de la fecha límite, aunque sea el mínimo. "
            "Segundo, intenta no usar más del 30% de tu límite de crédito. "
            "Tercero, no solicites muchos créditos al mismo tiempo. "
            "Cuarto, revisa tu Buró de Crédito cada 6 meses, es gratis una vez al año. "
            "Quinto, si puedes, paga el total para evitar intereses. "
            "Con tu Stori, cada pago a tiempo suma puntos a tu historial. "
            "En 12 meses de buen comportamiento puedes subir hasta 100 puntos."
        ),
        "ahorro": (
            "Tips para ahorrar con tu Stori: "
            "Primero, activa tu Stori Cuenta+ y gana 8.20% anual sobre tu ahorro. "
            "Segundo, usa las categorías de cashback para que tu dinero regrese. "
            "Tercero, aprovecha los Meses Sin Intereses para compras grandes. "
            "Cuarto, establece un presupuesto con la regla 50/30/20: "
            "50% necesidades, 30% gustos, 20% ahorro. "
            "Quinto, programa pagos automáticos para nunca pagar intereses por olvido. "
            "Tu cashback acumulado este mes de 127.50 pesos se deposita automáticamente. "
            "Es dinero extra sin esfuerzo!"
        ),
        "deudas": (
            "Estrategia para manejar deudas: "
            "Primero, lista todas tus deudas de menor a mayor, es el método bola de nieve. "
            "Segundo, paga el mínimo en todas y el extra en la más pequeña. "
            "Tercero, cuando liquides una, usa ese dinero para la siguiente. "
            "Cuarto, evita usar la tarjeta mientras pagas la deuda. "
            "Quinto, si tienes emergencia, usa máximo 10% de tu límite. "
            "Con tu saldo actual de 4,850 pesos, pagando 1,500 pesos mensuales "
            "quedarías libre en solo 3.5 meses y pagarías solo 175 pesos de intereses."
        ),
        "presupuesto": (
            "Cómo hacer un presupuesto efectivo: "
            "Primero, anota todos tus ingresos del mes. "
            "Segundo, separa gastos fijos como renta, servicios y transporte. "
            "Tercero, define un límite para gastos variables como comida y entretenimiento. "
            "Cuarto, asigna mínimo 10% a ahorro. Tu Stori Cuenta+ rinde 8.20%. "
            "Quinto, revisa cada semana si vas dentro del presupuesto. "
            "Tip Stori: Revisa tus movimientos en la app cada semana. "
            "Ver tus gastos te ayuda a ser más consciente."
        ),
        "emergencias": (
            "Fondo de emergencia con Stori: "
            "Tu meta debe ser 3 meses de gastos básicos en tu Stori Cuenta+. "
            "Empieza con 500 pesos al mes, lo importante es el hábito. "
            "Tu Cuenta+ te da 8.20% anual, tu dinero crece solo. "
            "No toques este fondo para gastos normales. "
            "Si surge una emergencia real, tienes respaldo sin endeudarte. "
            "Con 500 pesos mensuales, en 12 meses tendrás aproximadamente 6,250 pesos "
            "incluyendo rendimientos. Es tu red de seguridad!"
        ),
    }
    return tips.get(tema, tips["credito"])

@tool
def consultar_promociones_activas() -> str:
    """
    Consulta las promociones y ofertas activas para el cliente.
    
    Returns:
        Lista de promociones vigentes
    """
    return (
        "Promociones activas para ti: "
        "Esta semana: Farmacias con 10% cashback, válido hasta el domingo. "
        "Amazon con 6 meses sin intereses en compras mayores a 1,000 pesos. "
        "Siempre disponibles: Supermercados 5% cashback. Gasolina 3% cashback. "
        "Compras en línea 2% cashback. "
        "Especial del mes: Paga tu total antes del día 5 y participa en sorteo de 5,000 pesos. "
        "Invita un amigo y ambos reciben 200 pesos de cashback extra. "
        "Tip: Concentra tus compras de farmacia esta semana para maximizar tu cashback."
    )

# Configure Nova Sonic model
sonic_model = BidiNovaSonicModel(
    model_id=MODEL_ID,
    provider_config={
        "audio": {
            "voice": "tiffany",  # Warm female voice for financial coaching
            "input_rate": INPUT_SAMPLE_RATE,
            "output_rate": OUTPUT_SAMPLE_RATE,
            "channels": CHANNELS,
            "format": FORMAT
        },
        "inference": {}
    },
    client_config={
        "region": BEDROCK_REGION
    },
)

# Stori Financial Coach system prompt
STORI_SYSTEM_PROMPT = """Eres el Coach Financiero de Stori, un asistente de voz inteligente y empático que ayuda a los clientes de Stori a manejar mejor sus finanzas y construir su historial crediticio.

IDIOMA Y LOCALIZACIÓN:
- Hablas SIEMPRE en español mexicano coloquial y amigable
- TODAS las cantidades de dinero son en PESOS MEXICANOS. NUNCA digas "dólares"
- La moneda es SIEMPRE pesos mexicanos
- Para porcentajes usa "por ciento"
- NUNCA uses la palabra "dollars" ni "dólares". Solo "pesos"

ESTILO DE HABLA MEXICANO:
- Usa expresiones mexicanas naturales: "órale", "ándale", "qué padre", "va que va", "sale", "híjole"
- Tutea al cliente, usa "tú" no "usted" (es una app para jóvenes y millennials)
- Usa muletillas mexicanas con moderación: "mira", "fíjate que", "la neta", "onda"
- Sé entusiasta pero no exagerado. Ejemplo: "¡Órale, vas súper bien!" en vez de "Excelente progreso"
- Usa diminutivos cuando sea natural: "tantito", "ratito", "poquito"
- Para motivar: "¡Échale ganas!", "¡Tú puedes!", "Va que va"
- Para empatizar: "Te entiendo perfecto", "No te preocupes", "Aquí andamos para ayudarte"
- Habla como un amigo de confianza que sabe de finanzas, no como un ejecutivo bancario
- Mantén un ritmo conversacional relajado, no robótico ni formal

PERSONALIDAD:
- Eres cálida, cercana, echada pa'delante y motivadora
- Usas un tono amigable como un cuate que sabe de finanzas
- Celebras los logros del cliente: "¡Órale, qué bien vas!", "¡Eso es, así se hace!"
- Nunca juzgas ni haces sentir mal al cliente por sus decisiones financieras
- Explicas conceptos financieros de forma simple, como se lo explicarías a un amigo
- Eres paciente y repites información si el cliente lo necesita
- Usas humor ligero cuando es apropiado para hacer la conversación más amena

CAPACIDADES:
- Consultar saldo, fechas de pago y estado de cuenta
- Explicar el impacto de diferentes montos de pago en intereses y score
- Dar consejos personalizados sobre crédito, ahorro y presupuesto
- Informar sobre cashback, recompensas y promociones activas
- Ayudar a entender el Buró de Crédito y cómo mejorarlo
- Simular escenarios de pago para que el cliente tome mejores decisiones

REGLAS IMPORTANTES:
- Siempre usa el ID de cliente "demo_maria" cuando consultes herramientas
- Mantén respuestas concisas para conversación de voz (máximo 3-4 oraciones por turno)
- Si el cliente pregunta algo fuera de finanzas, redirige amablemente
- Siempre termina con una pregunta o sugerencia accionable
- Menciona beneficios de Stori cuando sea relevante y natural
- Si el cliente suena preocupado por dinero, sé especialmente empático y ofrece soluciones concretas
- NUNCA uses asteriscos, markdown ni formato especial en tus respuestas. Solo texto plano.
- Usa números para cantidades: "4,850 pesos" no "cuatro mil ochocientos cincuenta pesos"
- REPITO: Todas las cantidades son en PESOS MEXICANOS. Nunca menciones dólares.

CONTEXTO DE STORI:
- Stori es una tarjeta de crédito para personas que están construyendo su historial crediticio en México
- Ofrece: tarjeta sin anualidad, cashback, Meses Sin Intereses, Stori Cuenta+ (ahorro al 8 punto 20 por ciento)
- Más de 5 millones de mexicanos ya usan Stori
- La misión es dar acceso a crédito a quienes los bancos tradicionales rechazan

INICIO DE CONVERSACIÓN:
Cuando el cliente se conecte, salúdalo con calidez mexicana y pregunta en qué le puedes echar la mano. Ejemplo: "¡Hola! ¿Qué onda? Soy tu Coach Financiero de Stori. ¿En qué te echo la mano hoy? Puedo checar tu cuenta, darte tips para mejorar tu historial, o ayudarte a planear tus pagos. Tú dime."
"""

# Health check endpoint
@app.get("/ping")
async def ping():
    """Health check endpoint for AgentCore Runtime"""
    return {"status": "Healthy", "time_of_last_update": int(datetime.now().timestamp())}

# WebSocket endpoint for bidirectional voice chat
@app.websocket("/ws")
async def voice_chat(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for Stori Financial Coach voice streaming.
    """
    voice_agent = BidiAgent(
        model=sonic_model,
        tools=[
            consultar_saldo_y_pagos,
            consultar_historial_crediticio,
            consultar_cashback_y_recompensas,
            simular_pago,
            obtener_tips_financieros,
            consultar_promociones_activas,
            stop_conversation,
        ],
        system_prompt=STORI_SYSTEM_PROMPT,
    )
    
    try:
        await websocket.accept()
        print("WebSocket connection accepted - Stori Financial Coach")
        
        await voice_agent.run(
            inputs=[websocket.receive_json],
            outputs=[websocket.send_json]
        )
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in voice chat: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await websocket.close()
            await voice_agent.stop()
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")

# For local development/testing
if __name__ == "__main__":
    import uvicorn
    print(f"🟢 Starting Stori Financial Coach on port 8080...")
    print(f"Model: {MODEL_ID}")
    print(f"Bedrock Region: {BEDROCK_REGION}")
    print(f"Audio: {INPUT_SAMPLE_RATE}Hz, {CHANNELS}ch, {FORMAT}")
    
    host = "0.0.0.0" if os.getenv("CONTAINER_ENV") else "127.0.0.1"
    uvicorn.run(app, host=host, port=8080)
