import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(filename, slides_data, main_title_color=RGBColor(6, 182, 212)):
    prs = pptx.Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    bg_color = RGBColor(15, 23, 42)       # Slate 900
    card_bg = RGBColor(30, 41, 59)        # Slate 800
    card_border = RGBColor(51, 65, 85)    # Slate 700
    text_white = RGBColor(248, 250, 252)  # Slate 50
    text_muted = RGBColor(148, 163, 184)  # Slate 400
    text_accent = main_title_color        # Cyan or Emerald
    text_green = RGBColor(16, 185, 129)   # Emerald 500
    text_yellow = RGBColor(245, 158, 11)  # Amber 500

    for s_idx, sdata in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)

        # Background fill
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = bg_color
        bg.line.fill.background()

        if sdata.get("is_cover"):
            # Cover Slide Layout
            top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(11.733), Inches(0.08))
            top_bar.fill.solid()
            top_bar.fill.fore_color.rgb = text_accent
            top_bar.line.fill.background()

            tb = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(2.2))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = sdata["category"].upper()
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = text_accent

            p2 = tf.add_paragraph()
            p2.text = sdata["title"]
            p2.font.size = Pt(36)
            p2.font.bold = True
            p2.font.color.rgb = text_white

            p3 = tf.add_paragraph()
            p3.text = sdata["subtitle"]
            p3.font.size = Pt(20)
            p3.font.color.rgb = text_muted

            # Details card
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.8), Inches(11.733), Inches(2.8))
            card.fill.solid()
            card.fill.fore_color.rgb = card_bg
            card.line.color.rgb = card_border
            card.line.width = Pt(1)

            ctb = slide.shapes.add_textbox(Inches(1.2), Inches(4.0), Inches(10.9), Inches(2.4))
            ctf = ctb.text_frame
            ctf.word_wrap = True
            for item in sdata["bullets"]:
                cp = ctf.add_paragraph()
                cp.text = "• " + item
                cp.font.size = Pt(16)
                cp.font.color.rgb = text_white

        else:
            # Content Slide Layout
            # Header
            hb = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.1))
            htf = hb.text_frame
            htf.word_wrap = True
            p = htf.paragraphs[0]
            p.text = sdata["category"].upper()
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = text_accent

            p2 = htf.add_paragraph()
            p2.text = sdata["title"]
            p2.font.size = Pt(26)
            p2.font.bold = True
            p2.font.color.rgb = text_white

            cards = sdata.get("cards", [])
            if len(cards) == 2:
                col_w = Inches(5.7)
                gap = Inches(0.33)
                top_y = Inches(1.8)
                h = Inches(5.0)

                for c_i, card_info in enumerate(cards):
                    x = Inches(0.8) + c_i * (col_w + gap)
                    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, col_w, h)
                    box.fill.solid()
                    box.fill.fore_color.rgb = card_bg
                    box.line.color.rgb = card_border
                    box.line.width = Pt(1)

                    tb = slide.shapes.add_textbox(x + Inches(0.25), top_y + Inches(0.25), col_w - Inches(0.5), h - Inches(0.5))
                    tf = tb.text_frame
                    tf.word_wrap = True
                    hp = tf.paragraphs[0]
                    hp.text = card_info["heading"]
                    hp.font.size = Pt(18)
                    hp.font.bold = True
                    hp.font.color.rgb = card_info.get("color", text_accent)

                    for b in card_info["bullets"]:
                        bp = tf.add_paragraph()
                        bp.text = "• " + b
                        bp.font.size = Pt(13)
                        bp.font.color.rgb = text_white

            elif len(cards) == 3:
                col_w = Inches(3.7)
                gap = Inches(0.31)
                top_y = Inches(1.8)
                h = Inches(5.0)

                for c_i, card_info in enumerate(cards):
                    x = Inches(0.8) + c_i * (col_w + gap)
                    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, col_w, h)
                    box.fill.solid()
                    box.fill.fore_color.rgb = card_bg
                    box.line.color.rgb = card_border
                    box.line.width = Pt(1)

                    tb = slide.shapes.add_textbox(x + Inches(0.2), top_y + Inches(0.2), col_w - Inches(0.4), h - Inches(0.4))
                    tf = tb.text_frame
                    tf.word_wrap = True
                    hp = tf.paragraphs[0]
                    hp.text = card_info["heading"]
                    hp.font.size = Pt(17)
                    hp.font.bold = True
                    hp.font.color.rgb = card_info.get("color", text_accent)

                    for b in card_info["bullets"]:
                        bp = tf.add_paragraph()
                        bp.text = "• " + b
                        bp.font.size = Pt(12)
                        bp.font.color.rgb = text_white

            else:
                # 1 large card
                box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
                box.fill.solid()
                box.fill.fore_color.rgb = card_bg
                box.line.color.rgb = card_border

                tb = slide.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(4.5))
                tf = tb.text_frame
                tf.word_wrap = True
                first = True
                for b in sdata.get("bullets", []):
                    p = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    p.text = "• " + b
                    p.font.size = Pt(15)
                    p.font.color.rgb = text_white

    prs.save(filename)
    print(f"Presentation saved to: {filename}")

# ==============================================================================
# DATA 1: BUILD STAGE EXPOSITION (30%)
# ==============================================================================
cyan = RGBColor(6, 182, 212)
emerald = RGBColor(16, 185, 129)
yellow = RGBColor(245, 158, 11)

slides_build = [
    {
        "is_cover": True,
        "category": "DevPilot SRE Platform • Exposición del 30%",
        "title": "Arquitectura y Quality Gate de la Etapa de Build",
        "subtitle": "Automatización en la Nube con GitHub Actions, Compiladores AST y Verificación de Software Puro",
        "bullets": [
            "Enfoque Técnico Obligatorio: Cero teoría abstracta. Demostración 100% de herramientas prácticas.",
            "Herramientas Evaluadas: GitHub Actions (CI en Nube), py_compile y node --check (Compiladores AST locales).",
            "Calidad de Build: Script oficial verify-build.ps1 con 37 comprobaciones superadas (0 fallos).",
            "Microservicios Nativos: Demostración de Orders y Users como software puro (Validador + Endpoints + Runner)."
        ]
    },
    {
        "category": "Flujo de Integración Continua",
        "title": "El Pipeline de Build Automatizado (Quality Gate en 4 Fases)",
        "cards": [
            {
                "heading": "Fase 1 & 2: Linting y Aislamiento",
                "color": cyan,
                "bullets": [
                    "Fase 1: Análisis Estático y AST Linting de todo el backend Python y servidor Node.js.",
                    "Validación sintáctica en memoria de los 14 módulos frontend JavaScript del patrón MVVM.",
                    "Fase 2: Auditoría de Manifiestos de Exclusión (.dockerignore) para evitar fugas de contexto.",
                    "Verificación estricta de credenciales secretas protegidas (.env)."
                ]
            },
            {
                "heading": "Fase 3 & 4: Pruebas y Aprobación",
                "color": emerald,
                "bullets": [
                    "Fase 3: Ejecución de 12 pruebas unitarias Pytest (Auth JWT, TOTP, SQLite ACID y Contratos).",
                    "5 pruebas unitarias nativas con Node:Test Runner para microservicio Users.",
                    "Fase 4: Verificación de sintaxis de infraestructura y contratos de servicio.",
                    "Quality Gate Aprobado: 37/37 verificaciones superadas garantizando entrega confiable."
                ]
            }
        ]
    },
    {
        "category": "Herramienta 1 de Build: CI en la Nube",
        "title": "GitHub Actions — Orquestador de Integración Continua",
        "cards": [
            {
                "heading": "1. Instalación y Configuración",
                "color": cyan,
                "bullets": [
                    "Instalación: No requiere infraestructura física; corre sobre GitHub-hosted Runners (Ubuntu Latest).",
                    "Configuración: Archivo declarativo .github/workflows/build-validation.yml.",
                    "Disparadores (Triggers): Eventos push y pull_request en ramas main, master y develop.",
                    "Entornos: Configuración de setup-python@v5 (Python 3.11) y setup-node@v4 (Node.js 20)."
                ]
            },
            {
                "heading": "2. Aplicación y Verificación en Vivo",
                "color": emerald,
                "bullets": [
                    "Job 1: lint-and-syntax compila todos los scripts Python y valida el AST de JavaScript.",
                    "Job 2: unit-and-contract-tests instala dependencias y corre Pytest y Node:Test.",
                    "Job 3: docker-build valida la construcción de artefactos sin fallos.",
                    "Principio Fail-Fast: Si un archivo tiene un error sintáctico, el pipeline bloquea el commit en segundos.",
                    "EVIDENCIA: Pestaña 'Actions' de GitHub mostrando el workflow completado en verde."
                ]
            }
        ]
    },
    {
        "category": "Herramienta 2 de Build: Compiladores Locales",
        "title": "Compiladores Sintácticos AST (py_compile & node --check)",
        "cards": [
            {
                "heading": "Python AST Compiler (py_compile)",
                "color": yellow,
                "bullets": [
                    "Propósito: Compila el código fuente a bytecode binario .pyc validando la gramática abstracta.",
                    "Cómo se ejecuta: py -m py_compile devpilot_core/*.py microservices/*/*.py",
                    "Ventaja técnica: Detección instantánea de errores tipográficos, imports corruptos o fallos de indentación sin arrancar el servidor.",
                    "Archivos auditados: 10 scripts Python críticos (Core, Orders, Products, Payments y Validadores)."
                ]
            },
            {
                "heading": "Node.js Syntax Checker (node --check)",
                "color": emerald,
                "bullets": [
                    "Propósito: Analizador del motor V8 que parsea scripts JavaScript verificando sintaxis sin ejecutarlos.",
                    "Cómo se ejecuta: node --check microservices/users/server.js microservices/users/validator.js",
                    "Frontend MVVM: Valida en batch los 14 archivos JavaScript de models/, controllers/, views/ y js/.",
                    "Cero dependencias: Validación en tiempo cero sin instalar linters externos pesados."
                ]
            }
        ]
    },
    {
        "category": "Microservicio 1 como Software Puro",
        "title": "Microservicio de Órdenes (Python FastAPI) — 3 Partes",
        "cards": [
            {
                "heading": "1. El Validador (validator.py)",
                "color": cyan,
                "bullets": [
                    "Ubicación: microservices/orders/validator.py",
                    "Tecnología: Pydantic v2 (CreateOrderSchema, OrderItemSchema, DelayRequestSchema).",
                    "Reglas de negocio: Rechaza cantidades <= 0, precios negativos y productos duplicados.",
                    "Autoverificación en vivo: py validator.py muestra [PASS] aceptando válidos y rechazando inválidos."
                ]
            },
            {
                "heading": "2. Endpoints y Microservicio",
                "color": emerald,
                "bullets": [
                    "Ubicación: microservices/orders/main.py",
                    "Endpoints: GET /health, GET /orders, POST /orders, GET /metrics y /fault/*.",
                    "Ejecución Nativa: Bloque if __name__ == '__main__': uvicorn.run('main:app', port=3003).",
                    "Verificación en vivo: py main.py arranca directamente en http://127.0.0.1:3003 sin Docker."
                ]
            }
        ]
    },
    {
        "category": "Microservicio 2 como Software Puro",
        "title": "Microservicio de Usuarios (Node.js Express) — 3 Partes",
        "cards": [
            {
                "heading": "1. El Validador (validator.js)",
                "color": cyan,
                "bullets": [
                    "Ubicación: microservices/users/validator.js",
                    "Reglas estrictas: Expresión regular RFC 5322 para correos válidos, nombres >= 2 caracteres y roles válidos.",
                    "Middleware Express: userValidationMiddleware intercepta peticiones rechazando datos corruptos con HTTP 400.",
                    "Autoverificación en vivo: node validator.js verifica esquemas y muestra [PASS]."
                ]
            },
            {
                "heading": "2. Endpoints y Microservicio",
                "color": emerald,
                "bullets": [
                    "Ubicación: microservices/users/server.js",
                    "Endpoints: GET /health, GET /users, POST /users, DELETE /users/:id y /fault/delay.",
                    "Ejecución Nativa: node server.js arranca el servidor Express directamente en el puerto 3001.",
                    "Verificación en vivo: curl http://localhost:3001/health responde { status: 'UP' }."
                ]
            }
        ]
    },
    {
        "category": "Herramienta 3 de Build: Quality Gate Local",
        "title": "Script Oficial de Verificación (verify-build.ps1)",
        "cards": [
            {
                "heading": "Estructura del Script",
                "color": yellow,
                "bullets": [
                    "Propósito: Orquestar el Quality Gate local de 37 verificaciones con un solo comando.",
                    "1. Compilación Python AST (10 módulos) y Node.js V8 (16 módulos).",
                    "2. Auditoría de dependencias y contextos de construcción (.dockerignore).",
                    "3. Ejecución automática de suites Pytest y Node:Test.",
                    "4. Validación de esquemas de infraestructura y topología de red."
                ]
            },
            {
                "heading": "Salida y Evidencia Oficial",
                "color": emerald,
                "bullets": [
                    "Comando de ejecución: .\\verify-build.ps1",
                    "Total de Pruebas: 37 | Aprobadas: 37 | Fallos: 0",
                    "ESTADO FINAL: [OK] BUILD EXITOSO (El proyecto cumple con el Quality Gate)",
                    "El software está certificado y listo para pasar a la etapa de empaquetado y despliegue.",
                    "EVIDENCIA: Captura de pantalla de la terminal con las 37 líneas verdes."
                ]
            }
        ]
    },
    {
        "category": "Conclusiones y Calidad de Software",
        "title": "Resumen de la Etapa de Build y Lecciones Aprendidas",
        "cards": [
            {
                "heading": "Garantías del Quality Gate",
                "color": cyan,
                "bullets": [
                    "Cero Errores en Runtime: El análisis estático AST previene caídas por sintaxis antes de despliegue.",
                    "Contratos de API Blindados: Los validadores rechazan anomalías en el límite de entrada.",
                    "Seguridad Auditada: Criptografía JWT HMAC-SHA256 y TOTP verificadas matemáticamente.",
                    "Reproducibilidad Total: El build compila igual en local (Windows/Linux) y en CI (GitHub)."
                ]
            },
            {
                "heading": "Demostración en Vivo Lista",
                "color": emerald,
                "bullets": [
                    "1. Ejecución de .\\verify-build.ps1 ante el jurado/docente.",
                    "2. Prueba de validadores standalone: py validator.py y node validator.js.",
                    "3. Arranque de los microservicios como software nativo con .\\start-local.ps1.",
                    "4. Comprobación de endpoints en vivo con curl o navegador web."
                ]
            }
        ]
    }
]

create_deck("docs/DevPilot_Exposicion_Build_30.pptx", slides_build, main_title_color=cyan)

# ==============================================================================
# DATA 2: DEVOPS LIFECYCLE PARCIAL EXAM
# ==============================================================================
slides_parcial = [
    {
        "is_cover": True,
        "category": "DevPilot SRE Platform • Examen Parcial DevOps",
        "title": "Ciclo de Vida DevOps Integral: De la Prueba a la Observabilidad",
        "subtitle": "Sustentación Técnica de las 5 Etapas Evaluadas: Test, Release, Deploy, Operate y Monitor",
        "bullets": [
            "Reglas del Parcial: Ni Plan ni Code ni Build se evalúan en esta sesión.",
            "Cobertura Total: Las 5 etapas evaluadas están 100% implementadas con herramientas reales.",
            "Estrategia de Mesa: Demostración en vivo de comandos, configuración y funcionamiento inmediato.",
            "Stack Tecnológico: Pytest, Docker Buildx, Docker Compose, Docker SDK, TOTP RFC 6238 y DevPilot Core."
        ]
    },
    {
        "category": "Mapa General del Parcial",
        "title": "Matriz de Herramientas del Ciclo de Vida DevOps Evaluado",
        "cards": [
            {
                "heading": "Etapas 1, 2 y 3: Construcción y Entrega",
                "color": cyan,
                "bullets": [
                    "TEST: Pytest (Python 12 tests) + Node:Test Runner (Node.js 5 tests). Pruebas unitarias y de contrato.",
                    "RELEASE / PACKAGE: Docker Buildx y Versionado Semántico (v1.0.0). Imágenes inmutables multicapa.",
                    "DEPLOY: Docker Compose orquestando 5 contenedores sobre red bridge aislada devpilot_net."
                ]
            },
            {
                "heading": "Etapas 4 y 5: Operación y Resiliencia",
                "color": emerald,
                "bullets": [
                    "OPERATE: Docker Engine SDK (docker_manager.py) con Step-Up TOTP (RFC 6238) y auditoría forense.",
                    "MONITOR: DevPilot Core Engine (monitor.py) con sondeo cada 5s, SLAs y Chaos Studio.",
                    "Cero Imprevistos: Cualquier etapa que pregunte el docente se demuestra en menos de 1 minuto."
                ]
            }
        ]
    },
    {
        "category": "Etapa 1 del Parcial: TEST",
        "title": "Pruebas Automatizadas Unitarias y de Contrato (Pytest & Node)",
        "cards": [
            {
                "heading": "Configuración y Pruebas Backend",
                "color": cyan,
                "bullets": [
                    "Framework: Pytest con plugin Starlette TestClient para simulación HTTP en memoria.",
                    "test_auth_and_security.py: Pruebas de tokens JWT HS256, expiración, tampering y códigos TOTP.",
                    "test_database.py: Inicialización de esquemas SQLite ACID, transacciones y bitácora forense.",
                    "test_microservices_contracts.py: Validación de contratos /health y catálogos de negocio."
                ]
            },
            {
                "heading": "Demostración en Vivo ante el Docente",
                "color": emerald,
                "bullets": [
                    "Comando Pytest: py -m pytest tests/ -v (Muestra 12 pruebas PASSED en < 1 segundo).",
                    "Comando Node.js: cd microservices/users ; npm test (Muestra 5 pruebas nativas PASSED).",
                    "Contratos de Caos: Valida que los endpoints /fault/delay y /fault/reset respondan nominalmente.",
                    "EVIDENCIA: Terminal con el reporte detallado de 17 pruebas unitarias superadas."
                ]
            }
        ]
    },
    {
        "category": "Etapa 2 del Parcial: RELEASE",
        "title": "Empaquetado y Versionado Semántico (Docker Buildx)",
        "cards": [
            {
                "heading": "Estrategia de Empaquetado Inmutable",
                "color": yellow,
                "bullets": [
                    "Herramienta: Docker Buildx generando artefactos reproducibles a partir de Dockerfiles.",
                    "Optimización Multicapa: Imágenes base ligeras (python:3.11-slim y node:20-alpine).",
                    "Caché Eficiente: Copia de requirements.txt / package.json antes del código fuente.",
                    "Aislamiento Estricto: Manifiestos .dockerignore eliminan dependencias locales infladas."
                ]
            },
            {
                "heading": "Demostración en Vivo ante el Docente",
                "color": emerald,
                "bullets": [
                    "Comando de Build: docker compose build",
                    "Comando de Inspección: docker images | Select-String 'devpilot'",
                    "Versionado Semántico: Artefactos etiquetados formalmente con versión v1.0.0.",
                    "EVIDENCIA: Listado de imágenes Docker inmutables listas para despliegue en staging o producción."
                ]
            }
        ]
    },
    {
        "category": "Etapa 3 del Parcial: DEPLOY",
        "title": "Despliegue y Orquestación de Microservicios (Docker Compose)",
        "cards": [
            {
                "heading": "Topología de Infraestructura declarativa",
                "color": cyan,
                "bullets": [
                    "Manifiesto: docker-compose.yml estándar de Compose Specification.",
                    "Servicios Orquestados (5): devpilot_core (:8000), users (:3001), products (:3002), orders (:3003), payments (:3004).",
                    "Red Aislada: devpilot_net (Bridge driver) con resolución DNS automática por nombre de servicio.",
                    "Persistencia de Datos: Volumen nombrado devpilot_data para la base de datos devpilot.db.",
                    "Healthchecks Nativos: Directivas healthcheck garantizan secuencia de encendido controlada."
                ]
            },
            {
                "heading": "Demostración en Vivo ante el Docente",
                "color": emerald,
                "bullets": [
                    "Comando de Despliegue: docker compose up -d",
                    "Comando de Verificación: docker compose ps",
                    "Salida esperada: Los 5 contenedores en estado Up (healthy) con sus puertos expuestos.",
                    "EVIDENCIA: Terminal con el estado de los contenedores y acceso inmediato en navegador a http://localhost:8000."
                ]
            }
        ]
    },
    {
        "category": "Etapa 4 del Parcial: OPERATE",
        "title": "Operación, Resiliencia y Step-Up Auth TOTP (Docker SDK)",
        "cards": [
            {
                "heading": "Módulo docker_manager.py y Seguridad",
                "color": yellow,
                "bullets": [
                    "Docker Engine SDK: Comunicación directa con el socket /var/run/docker.sock.",
                    "Auto-Recovery: Reinicio programático de contenedores ante anomalías o caídas.",
                    "Auto-Discovery: Función discover_candidate_services() escanea la red e incorpora nuevos servicios en caliente (ej: payments).",
                    "Seguridad Operacional: Step-Up Authentication con TOTP (RFC 6238) para acciones destructivas."
                ]
            },
            {
                "heading": "Demostración en Vivo ante el Docente",
                "color": emerald,
                "bullets": [
                    "1. En el Dashboard web (http://localhost:8000), solicitar reinicio de contenedor.",
                    "2. El sistema bloquea la acción y exige código TOTP de 6 dígitos (Demo: JBSWY3DPEHPK3PXP).",
                    "3. Una vez validado, Docker Engine ejecuta el reinicio en caliente.",
                    "4. En la pestaña 'Auditoría Forense', mostrar el registro inmutable con usuario, fecha, método y resultado.",
                    "EVIDENCIA: Modal TOTP y bitácora de auditoría en SQLite."
                ]
            }
        ]
    },
    {
        "category": "Etapa 5 del Parcial: MONITOR",
        "title": "Monitoreo Continuo, SLAs y Chaos Testing (DevPilot Engine)",
        "cards": [
            {
                "heading": "Motor de Observabilidad (monitor.py)",
                "color": cyan,
                "bullets": [
                    "Sondeo Asíncrono: Consulta concurrente cada 5 segundos al endpoint /health de cada microservicio.",
                    "Métricas Clave: Latencia RTT media, tasa de errores HTTP 5xx y cumplimiento de SLAs (%).",
                    "Frontend SPA MVVM: Gráficas de series temporales en vivo con Chart.js en http://localhost:8000.",
                    "Copiloto SRE con IA: Análisis de causa raíz (RCA) automático ante anomalías detectadas."
                ]
            },
            {
                "heading": "Demostración en Vivo con Chaos Studio",
                "color": emerald,
                "bullets": [
                    "1. Abrir http://localhost:8000 mostrando tarjetas en verde (HEALTHY).",
                    "2. Ir a Chaos Studio, seleccionar el servicio 'orders' e inyectar 2500 ms de latencia o 50% de error.",
                    "3. En menos de 5 segundos la tarjeta cambia a rojo/ámbar y se genera un incidente automático.",
                    "4. Pulsar 'Reset Fallos' y ver cómo el monitor auto-recupera el semáforo verde.",
                    "EVIDENCIA: Dashboard alterándose en tiempo real ante la inyección de fallos."
                ]
            }
        ]
    },
    {
        "category": "Resumen de Sustentación en Mesa",
        "title": "Acordeón Rápido de Comandos para el Parcial",
        "cards": [
            {
                "heading": "Si el docente te pregunta...",
                "color": yellow,
                "bullets": [
                    "TEST ➔ 'Implementamos Pytest y Node:Test para contratos y criptografía'.",
                    "RELEASE ➔ 'Usamos Docker Buildx para imágenes multicapa inmutables v1.0.0'.",
                    "DEPLOY ➔ 'Usamos Docker Compose con red bridge aislada devpilot_net y volúmenes'.",
                    "OPERATE ➔ 'Usamos Docker SDK con aprobación TOTP RFC 6238 y auditoría forense'.",
                    "MONITOR ➔ 'Usamos DevPilot Core con sondeo asíncrono cada 5s y Chaos Studio'."
                ]
            },
            {
                "heading": "Comando Rápido a Ejecutar",
                "color": emerald,
                "bullets": [
                    "TEST ➔ py -m pytest tests/ -v",
                    "RELEASE ➔ docker compose build",
                    "DEPLOY ➔ docker compose up -d && docker compose ps",
                    "OPERATE ➔ http://localhost:8000 (Modal TOTP y Auditoría)",
                    "MONITOR ➔ http://localhost:8000 (Chaos Studio inyectando fallos)"
                ]
            }
        ]
    }
]

create_deck("docs/DevPilot_Examen_Parcial_DevOps.pptx", slides_parcial, main_title_color=emerald)
