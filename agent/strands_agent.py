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
    # Simulated data for PoC demo
    return (
        "Estado de cuenta de María García:\n"
        "- Saldo actual: $4,850.00 MXN\n"
        "- Límite de crédito: $12,000.00 MXN\n"
        "- Crédito disponible: $7,150.00 MXN\n"
        "- Fecha de corte: 15 de cada mes\n"
        "- Fecha límite de pago: 5 de cada mes\n"
        "- Pago mínimo: $485.00 MXN\n"
        "- Pago para no generar intereses: $4,850.00 MXN\n"
        "- Próximo pago vence: 5 de julio de 2025\n"
        "- Tasa de interés anual: 59.9%\n"
        "- Días restantes para pagar: 12 días"
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
        "Historial crediticio de María García:\n"
        "- Score Buró de Crédito: 620 (Regular - en mejora)\n"
        "- Score hace 6 meses: 580\n"
        "- Mejora: +40 puntos en 6 meses\n"
        "- Meses consecutivos pagando a tiempo: 5\n"
        "- Pagos atrasados últimos 12 meses: 1 (hace 7 meses)\n"
        "- Utilización de crédito: 40% (recomendado: menos de 30%)\n"
        "- Antigüedad de cuenta: 8 meses\n"
        "- Siguiente meta: 650 puntos (buen historial)\n"
        "- Consejo: Pagar más del mínimo y mantener utilización bajo 30% "
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
        "Recompensas de María García:\n"
        "- Cashback acumulado este mes: $127.50 MXN\n"
        "- Cashback total histórico: $890.00 MXN\n"
        "- Categorías activas con cashback:\n"
        "  • Supermercados: 5% (hasta $200 de cashback)\n"
        "  • Gasolina: 3% (hasta $150 de cashback)\n"
        "  • Compras en línea: 2% (sin límite)\n"
        "- Categoría estrella esta semana: Farmacias 10% (válido hasta domingo)\n"
        "- Próximo depósito de cashback: 16 de julio\n"
        "- Tip: Usa tu Stori en farmacias esta semana para aprovechar el 10%."
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
            "Simulación - Pago mínimo ($485 MXN):\n"
            "- Saldo restante: $4,365.00 MXN\n"
            "- Intereses que se generarán: $217.50 MXN\n"
            "- Nuevo saldo siguiente mes: $4,582.50 MXN\n"
            "- Tiempo para liquidar (pagando solo mínimo): 14 meses\n"
            "- Total que pagarías: $6,790.00 MXN (39% más)\n"
            "- Impacto en score: Neutral (no sube ni baja)\n\n"
            "⚠️ Recomendación: Si puedes pagar aunque sea $1,500, "
            "reducirías los intereses a $133 y liquidarías en 4 meses."
        )
    elif monto == "total" or monto == "4850":
        return (
            "Simulación - Pago total ($4,850 MXN):\n"
            "- Saldo restante: $0.00 MXN\n"
            "- Intereses que se generarán: $0.00 MXN\n"
            "- Crédito disponible: $12,000.00 MXN\n"
            "- Impacto en score: Positivo (+5 a +10 puntos)\n"
            "- Utilización de crédito: 0% (excelente)\n\n"
            "✅ ¡Excelente decisión! Pagar el total es la mejor forma "
            "de construir historial sin pagar intereses."
        )
    else:
        return (
            f"Simulación - Pago de ${monto} MXN:\n"
            f"- Saldo restante: ${4850 - int(monto):.2f} MXN\n"
            f"- Intereses sobre saldo restante: ~${(4850 - int(monto)) * 0.05:.2f} MXN\n"
            "- Impacto en score: Ligeramente positivo\n"
            f"- Utilización después del pago: {((4850 - int(monto)) / 12000) * 100:.0f}%\n\n"
            "💡 Tip: Entre más pagues arriba del mínimo, menos intereses generas "
            "y más rápido crece tu score."
        )

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
            "Tips para mejorar tu historial crediticio:\n"
            "1. Paga siempre antes de la fecha límite (aunque sea el mínimo)\n"
            "2. Intenta no usar más del 30% de tu límite de crédito\n"
            "3. No solicites muchos créditos al mismo tiempo\n"
            "4. Revisa tu Buró de Crédito cada 6 meses (es gratis una vez al año)\n"
            "5. Si puedes, paga el total para evitar intereses\n\n"
            "Con tu Stori, cada pago a tiempo suma puntos a tu historial. "
            "En 12 meses de buen comportamiento puedes subir hasta 100 puntos."
        ),
        "ahorro": (
            "Tips para ahorrar con tu Stori:\n"
            "1. Activa tu Stori Cuenta+ y gana 8.20% anual sobre tu ahorro\n"
            "2. Usa las categorías de cashback para que tu dinero regrese\n"
            "3. Aprovecha los Meses Sin Intereses para compras grandes\n"
            "4. Establece un presupuesto: la regla 50/30/20\n"
            "   - 50% necesidades, 30% gustos, 20% ahorro\n"
            "5. Programa pagos automáticos para nunca pagar intereses por olvido\n\n"
            "Tu cashback acumulado este mes ($127.50) se deposita automáticamente. "
            "¡Es dinero extra sin esfuerzo!"
        ),
        "deudas": (
            "Estrategia para manejar deudas:\n"
            "1. Lista todas tus deudas de menor a mayor (método bola de nieve)\n"
            "2. Paga el mínimo en todas y el extra en la más pequeña\n"
            "3. Cuando liquides una, usa ese dinero para la siguiente\n"
            "4. Evita usar la tarjeta mientras pagas la deuda\n"
            "5. Si tienes emergencia, usa máximo 10% de tu límite\n\n"
            "Con tu saldo actual de $4,850, pagando $1,500 mensuales "
            "quedarías libre en solo 3.5 meses y pagarías solo $175 de intereses."
        ),
        "presupuesto": (
            "Cómo hacer un presupuesto efectivo:\n"
            "1. Anota todos tus ingresos del mes\n"
            "2. Separa gastos fijos (renta, servicios, transporte)\n"
            "3. Define un límite para gastos variables (comida, entretenimiento)\n"
            "4. Asigna mínimo 10% a ahorro (tu Stori Cuenta+ rinde 8.20%)\n"
            "5. Revisa cada semana si vas dentro del presupuesto\n\n"
            "Tip Stori: Revisa tus movimientos en la app cada semana. "
            "Ver tus gastos te ayuda a ser más consciente."
        ),
        "emergencias": (
            "Fondo de emergencia con Stori:\n"
            "1. Meta: 3 meses de gastos básicos en tu Stori Cuenta+\n"
            "2. Empieza con $500 al mes (lo importante es el hábito)\n"
            "3. Tu Cuenta+ te da 8.20% anual, tu dinero crece solo\n"
            "4. No toques este fondo para gastos normales\n"
            "5. Si surge una emergencia real, tienes respaldo sin endeudarte\n\n"
            "Con $500 mensuales, en 12 meses tendrás ~$6,250 "
            "(incluyendo rendimientos). ¡Es tu red de seguridad!"
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
        "Promociones activas para ti:\n\n"
        "🔥 ESTA SEMANA:\n"
        "• Farmacias: 10% cashback (hasta domingo)\n"
        "• Amazon: 6 MSI en compras mayores a $1,000\n\n"
        "📱 SIEMPRE DISPONIBLES:\n"
        "• Supermercados: 5% cashback\n"
        "• Gasolina: 3% cashback\n"
        "• Compras en línea: 2% cashback\n\n"
        "🎁 ESPECIAL DEL MES:\n"
        "• Paga tu total antes del día 5 y participa en sorteo de $5,000\n"
        "• Invita un amigo: ambos reciben $200 de cashback extra\n\n"
        "💡 Tip: Concentra tus compras de farmacia esta semana "
        "para maximizar tu cashback."
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

PERSONALIDAD:
- Hablas siempre en español mexicano, de forma cálida, cercana y motivadora
- Usas un tono amigable pero profesional, como un amigo que sabe de finanzas
- Celebras los logros del cliente ("¡Vas muy bien!", "¡Excelente decisión!")
- Nunca juzgas ni haces sentir mal al cliente por sus decisiones financieras
- Explicas conceptos financieros de forma simple, sin tecnicismos innecesarios
- Eres paciente y repites información si el cliente lo necesita

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

CONTEXTO DE STORI:
- Stori es una tarjeta de crédito para personas que están construyendo su historial crediticio en México
- Ofrece: tarjeta sin anualidad, cashback, Meses Sin Intereses, Stori Cuenta+ (ahorro al 8.20%)
- Más de 5 millones de mexicanos ya usan Stori
- La misión es dar acceso a crédito a quienes los bancos tradicionales rechazan

INICIO DE CONVERSACIÓN:
Cuando el cliente se conecte, salúdalo calidamente y pregunta en qué le puedes ayudar hoy. Ejemplo: "¡Hola! Soy tu Coach Financiero de Stori. ¿En qué te puedo ayudar hoy? Puedo revisar tu cuenta, darte tips para mejorar tu historial, o ayudarte a planear tus pagos."
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
    # Create a new agent instance for this connection
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
