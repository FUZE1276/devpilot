# 🚀 DevPilot — Autonomous Observability & Chaos Remediation Engine
> **Guía Técnica Integral del Código y Manual de Presentación del Proyecto**

DevPilot es una plataforma integral de **observabilidad proactiva, ingeniería de caos (Chaos Testing) y auto-remediación asistida por Inteligencia Artificial (Human-in-the-Loop)** para arquitecturas distribuidas de microservicios sobre Docker.

Este documento detalla la **arquitectura técnica, el funcionamiento interno de cada módulo de código**, las decisiones de diseño y el **guión paso a paso para realizar una presentación técnica o sustentación** del proyecto.

---

## 📑 Tabla de Contenidos
1. [Arquitectura General del Sistema](#-1-arquitectura-general-del-sistema)
2. [Estructura del Proyecto](#-2-estructura-del-proyecto)
3. [Desglose Detallado del Código Fuente](#-3-desglose-detallado-del-código-fuente)
   - [3.1 DevPilot Core (`devpilot_core/`)](#31-devpilot-core-motor-central)
     - [`main.py` — API REST y Orquestador de Ciclo de Vida](#311-mainpy--api-rest-y-orquestador-del-ciclo-de-vida)
     - [`auth.py` — Seguridad Criptográfica, JWT, TOTP y RBAC](#312-authpy--seguridad-criptográfica-jwt-totp-y-rbac)
     - [`email_otp.py` — Doble Factor de Autenticación por Correo (MFA)](#313-email_otppy--doble-factor-por-correo-electrónico-mfa)
     - [`database.py` — Capa de Persistencia y Migraciones SQLite](#314-databasepy--capa-de-persistencia-y-migraciones-sqlite)
     - [`monitor.py` — Motor Autónomo de Sondeo y Detección de Anomalías](#315-monitorpy--motor-autónomo-de-sondeo-y-anomalías)
     - [`docker_manager.py` — Integración Docker Engine SDK](#316-docker_managerpy--integración-con-docker-engine-sdk)
     - [`ai_agent.py` — Copiloto SRE con IA & Fallback Heurístico](#317-ai_agentpy--copiloto-sre-con-ia-y-motor-heurístico)
     - [`static/index.html` — Frontend SPA Reactivo (Patrón MVVM)](#318-staticindexhtml--frontend-spa-reactivo-patrón-mvvm)
   - [3.2 Microservicios de Aplicación (`microservices/`)](#32-microservicios-de-aplicación-microservices)
   - [3.3 Infraestructura como Código (`docker-compose.yml`)](#33-infraestructura-como-código-docker-composeyml)
4. [Flujos de Seguridad y Autenticación](#-4-flujos-de-seguridad-y-autenticación)
5. [Guión Paso a Paso para Presentar el Proyecto](#-5-guión-paso-a-paso-para-presentar-el-proyecto)
6. [Credenciales Oficiales de Demostración](#-6-credenciales-oficiales-de-demostración)

---

## 🏛️ 1. Arquitectura General del Sistema

DevPilot opera bajo el principio de **Observabilidad Externa No Invasiva**: no requiere la inyección de agentes pesados ni la alteración del código de los microservicios.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          NAVEGADOR WEB (CLIENTE)                       │
│  SPA Reactiva (MVVM) • Tailwind CSS • Chart.js • Lucide Icons • WebSockets  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST + Bearer JWT
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DEVPILOT CORE (FastAPI :8000)                      │
│                                                                        │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐   │
│  │   Auth & RBAC   │   │ Health Monitor  │   │   Docker Manager    │   │
│  │ (JWT/TOTP/Email)│   │  (Loop cada 5s) │   │ (Logs / Restarts)   │   │
│  └────────┬────────┘   └────────┬────────┘   └──────────┬──────────┘   │
│           │                     │                       │              │
│           ▼                     ▼                       │              │
│  ┌─────────────────┐   ┌─────────────────┐              │              │
│  │ Base de Datos   │   │ AI SRE Copilot  │              │              │
│  │  (SQLite ACID)  │   │(Claude/Heuristic│              │              │
│  └─────────────────┘   └─────────────────┘              │              │
└─────────────────────────────────┬───────────────────────┼──────────────┘
                                  │ Red Docker (devpilot_net)
                                  │ /var/run/docker.sock  │
        ┌─────────────────────────┼───────────────────────┼──────────┐
        ▼                         ▼                       ▼          ▼
┌───────────────┐         ┌───────────────┐       ┌───────────────┐ ┌───────────────┐
│ Users Service │         │Products Serv. │       │Orders Service │ │Payments Serv. │
│(Node.js :3001)│         │(FastAPI :3002)│       │(FastAPI :3003)│ │(FastAPI :3004)│
└───────────────┘         └───────────────┘       └───────────────┘ └───────────────┘
```

---

## 📂 2. Estructura del Proyecto

```
devpilot/
├── docker-compose.yml              # Orquestación de contenedores, redes y docker.sock
├── .env                            # Parámetros de entorno (JWT, SMTP, expiración)
├── README.md                       # Documentación maestra y manual de presentación
├── docs/
│   └── DevPilot_SRS_IEEE830.md     # Especificación Formal de Requisitos (IEEE 830-1998)
├── devpilot_core/                  # Motor central de observabilidad y remediación
│   ├── main.py                     # API REST FastAPI y control de ciclo de vida
│   ├── auth.py                     # Criptografía JWT (HS256), TOTP (RFC 6238) y RBAC
│   ├── email_otp.py                # Servicio MFA con envío de código por Gmail SMTP
│   ├── database.py                 # Esquema SQLite, migraciones y transacciones ACID
│   ├── monitor.py                  # Sondeo concurrente /health, ventanas móviles y SLAs
│   ├── docker_manager.py           # Docker Engine API: logs, reinicios y Auto-Discovery
│   ├── ai_agent.py                 # Agente SRE Claude 3.5 Sonnet y fallback heurístico
│   ├── Dockerfile                  # Empaquetado del servicio Core
│   ├── requirements.txt            # Dependencias Python del Core
│   └── static/
│       └── index.html              # SPA Dashboard MVVM (~3500 líneas, sin dependencias Node)
└── microservices/                  # Microservicios monitoreados
    ├── users/                      # Node.js / Express (Puerto 3001)
    ├── products/                   # Python / FastAPI (Puerto 3002)
    ├── orders/                     # Python / FastAPI (Puerto 3003)
    └── payments/                   # Python / FastAPI (Puerto 3004) - Auto-Discovery candidato
```

---

## 🔍 3. Desglose Detallado del Código Fuente

### 3.1 DevPilot Core (Motor Central)

#### 3.1.1 `main.py` — API REST y Orquestador del Ciclo de Vida
* **Ruta:** [`devpilot_core/main.py`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/main.py)
* **Propósito:** Expone los endpoints HTTP para el frontend y orquesta el inicio de tareas asíncronas en segundo plano.
* **Componentes y Funciones Clave:**
  * **`@asynccontextmanager lifespan(app)`**: Gestiona el ciclo de vida de la aplicación. Al arrancar ejecuta `init_db()` para inicializar tablas y siembra de datos, y levanta el bucle de sondeo continuo con `monitor.start()`. Al detener la aplicación, cierra limpiamente el pool HTTP.
  * **Middleware CORS (`CORSMiddleware`)**: Permite la comunicación segura y consumo de API desde cualquier origen o puerto.
  * **Endpoints de Autenticación (`/api/auth/*`)**:
    * `POST /api/auth/login`: Autenticación con contraseña + inicio del flujo MFA (solicitud o verificación de código de 6 dígitos).
    * `POST /api/auth/sso/login`: Autenticación federada simulada OIDC para emisión inmediata de JWT.
    * `POST /api/auth/verify-totp`: Verificación del segundo factor en acciones de riesgo.
    * `GET /api/auth/demo-totp`: Sincronización en vivo del código TOTP actual para pruebas y sustentaciones.
  * **Endpoints de Servicios y Auto-Discovery (`/api/services/*`)**:
    * `GET /api/services/discover`: Escanea la red de Docker, detecta contenedores no registrados y comprueba su salud HTTP.
    * `POST /api/services`: Registra un nuevo servicio con umbrales personalizados de SLA.
    * `PUT /api/services/{name}/thresholds`: Calibra en caliente los SLAs de latencia y tasa de error.
  * **Proxy de Caos (`POST /api/fault/inject`)**: Valida el permiso RBAC `chaos:inject` y reenvía peticiones de latencia, error 500 o caída al microservicio correspondiente.
  * **Copiloto de IA (`POST /api/ai/chat`)**: Canal de comunicación con el agente SRE para análisis forense y diagnóstico.
  * **Servidor de la SPA (`@app.get("/")`)**: Sirve el archivo estático `static/index.html` deshabilitando la caché del navegador (`no-cache`) para garantizar que el cliente siempre tenga la versión más reciente.

---

#### 3.1.2 `auth.py` — Seguridad Criptográfica, JWT, TOTP y RBAC
* **Ruta:** [`devpilot_core/auth.py`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/auth.py)
* **Propósito:** Garantiza el cumplimiento de los requerimientos **RF07 (Autenticación)** y **RF08 (Autorización RBAC)** de la norma IEEE 830.
* **Componentes y Funciones Clave:**
  * **Motor JWT Nativo (RFC 7519)**:
    * `create_jwt_token(payload)`: Construye un token firmado con HMAC-SHA256 codificado en Base64 URL-safe, incorporando expiración temporal (`exp`) y claims del usuario.
    * `verify_jwt_token(token)`: Valida la firma criptográfica con `hmac.compare_digest` para prevenir ataques de temporización (timing attacks).
  * **Algoritmo TOTP Nativo (RFC 6238 / RFC 4226)**:
    * `generate_current_totp(secret, time_step=30)`: Implementa HOTP basado en tiempo: calcula la ventana `T = unix_time // 30`, computa `HMAC-SHA1(secret, T)` y extrae dinámicamente el código de 6 dígitos.
    * `verify_totp_code(code, secret, window=1)`: Valida el código permitiendo deriva temporal de ±1 intervalo (±30 segundos).
  * **Matriz de Control de Acceso Basado en Roles (RBAC)**:
    * `ROLE_PERMISSIONS`: Define los permisos granulares para cada perfil:
      * **`Super_Administrador`**: Control absoluto (12 permisos: gobernanza de usuarios, calibración de SLAs, remediación, caos, configuración del sistema).
      * **`Administrador`**: Operación SRE (9 permisos: inspección de logs, Chaos Studio, auto-remediación con Step-Up TOTP).
      * **`Cliente`**: Consulta de disponibilidad (3 permisos: telemetría, lectura de incidentes y chat informativo).
  * **Guards de Seguridad para FastAPI**:
    * `require_permission(perm_id)`: Dependencia que inspecciona el token JWT en el encabezado `Authorization: Bearer <token>` y aborta con `HTTP 403 Forbidden` si el usuario no posee el permiso requerido.

---

#### 3.1.3 `email_otp.py` — Doble Factor por Correo Electrónico (MFA)
* **Ruta:** [`devpilot_core/email_otp.py`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/email_otp.py)
* **Propósito:** Añade una capa de seguridad física de dos factores enviando un código numérico temporal al correo del usuario antes de emitir el token de sesión.
* **Componentes y Funciones Clave:**
  * `generate_otp_code()`: Genera un código criptográficamente seguro de 6 dígitos mediante `secrets.randbelow(1000000)`.
  * `request_email_otp(email, recipient_name)`: Almacena el código generado en la tabla `email_otp_codes` con una validez de 5 minutos y dispara el envío SMTP asíncrono en un hilo secundario para no bloquear el bucle de eventos de FastAPI.
  * `_send_smtp_email()`: Establece conexión TLS con `smtp.gmail.com:587`, se autentica con App Password y despacha un correo con formato visual HTML responsive.
  * **Modo Desarrollo (`EMAIL_OTP_DEV_MODE`)**: Si se activa, devuelve el código generado directamente en la respuesta JSON de la API, ideal para laboratorios donde no haya conexión a Internet.

---

#### 3.1.4 `database.py` — Capa de Persistencia y Migraciones SQLite
* **Ruta:** [`devpilot_core/database.py`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/database.py)
* **Propósito:** Maneja el almacenamiento relacional de métricas de telemetría, incidentes operacionales, auditorías forenses y credenciales de usuario.
* **Tablas Principales y Funciones:**
  * **`services`**: Catálogo de microservicios con sus URLs, contenedores asociados, estado en tiempo real y umbrales SLA de latencia y error.
  * **`health_metrics`**: Registro de series de tiempo de cada sondeo (código HTTP, latencia en ms, booleano de error, timestamp ISO-8601).
  * **`incidents`**: Historial de incidentes generados, tipo de severidad (`HIGH`, `CRITICAL`), explicación simplificada para clientes y recomendaciones técnicas de IA.
  * **`remediation_proposals`**: Propuestas de reparación generadas automáticamente en espera de decisión humana (`PENDING_APPROVAL`, `APPROVED`, `REJECTED`).
  * **`remediation_logs`**: Pista de auditoría inmutable que registra quién autorizó la acción, método de autenticación usado y resultado del contenedor.
  * **Migraciones Automáticas**: `init_db()` verifica la existencia de columnas mediante `PRAGMA table_info` ejecutando sentencias `ALTER TABLE` si la base de datos proviene de versiones anteriores, evitando pérdida de datos.

---

#### 3.1.5 `monitor.py` — Motor Autónomo de Sondeo y Anomalías
* **Ruta:** [`devpilot_core/monitor.py`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/monitor.py)
* **Propósito:** Ejecuta el ciclo proactivo de observabilidad en segundo plano cada 5 segundos.
* **Mecanismos de Operación:**
  * **Persistent HTTP Pool**: Emplea `httpx.AsyncClient` con límites de conexiones reutilizables (`keepalive`) para realizar peticiones concurrentes mediante `asyncio.gather`.
  * **Cálculo de Ventana Móvil (`ROLLING_WINDOW_SIZE = 10`)**: Evalúa los últimos 10 sondeos de cada microservicio para calcular:
    1. Latencia promedio móvil ($RTT_{avg}$).
    2. Tasa porcentual de error ($ErrorRate = \frac{Errores}{Muestras}$).
  * **Disparadores de Incidentes**:
    * **Latencia Excedida**: Si $RTT_{avg} > LatencyThreshold$ (por defecto 2000 ms).
    * **Tasa de Fallo Elevada**: Si $ErrorRate > ErrorThreshold$ (por defecto 20%).
    * **Caída Total (Outage)**: Si el servicio no responde, devuelve `503/504` o falla de forma consecutiva.
  * **Auto-Resolución**: Cuando el microservicio retorna a sus parámetros nominales de salud por 2 sondeos consecutivos, el monitor cierra automáticamente el incidente abierto en la base de datos.

---

#### 3.1.6 `docker_manager.py` — Integración con Docker Engine SDK
* **Ruta:** [`devpilot_core/docker_manager.py`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/docker_manager.py)
* **Propósito:** Interactúa directamente con el demonio de Docker a través de `/var/run/docker.sock` para labores de diagnóstico forense y auto-remediación.
* **Capacidades:**
  * `is_docker_connected()`: Comprueba la disponibilidad del Docker Engine mediante caché de 10 segundos para no saturar el socket.
  * `get_container_logs(service_name, tail=100)`: Lee en tiempo real las últimas $N$ líneas de log emitidas por el contenedor para alimentar el prompt del agente de IA.
  * `restart_service_container(service_name)`: Ejecuta el reinicio en caliente del contenedor con `container.restart(timeout=5)`.
  * `discover_candidate_services()`: Inspecciona todos los contenedores activos en la red `devpilot_net`, detecta sus alias de red y puertos expuestos, y sugiere su incorporación dinámica a DevPilot.

---

#### 3.1.7 `ai_agent.py` — Copiloto SRE con IA y Motor Heurístico
* **Ruta:** [`devpilot_core/ai_agent.py`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/ai_agent.py)
* **Propósito:** Provee análisis de causa raíz (RCA) y recomendaciones de remediación técnica en lenguaje natural.
* **Estrategia Dual (Híbrida):**
  1. **Modo Cloud (LLM Avanzado)**: Si existe una variable `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` o `GEMINI_API_KEY`, formula un prompt estructurado enviando telemetría reciente, incidentes y logs de Docker para generar un diagnóstico profundo.
  2. **Modo Local (Fallback Heurístico Inteligente)**: Si no hay clave de API o no hay conexión a internet, un motor determinístico analiza los patrones de error (códigos de salida, excepciones en logs, picos de latencia) y genera diagnósticos precisos en español junto con propuestas de remediación estructuradas.

---

#### 3.1.8 `devpilot_core/static/` — Frontend SPA Reactivo Modular (Patrón MVVM Separado por Carpetas)
* **Ruta:** [`devpilot_core/static/`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/devpilot_core/static/)
* **Propósito:** Interfaz de usuario interactiva moderna de alta fidelidad, organizada formalmente por carpetas según las responsabilidades del patrón **MVVM / MVC**:
* **Estructura Modular por Carpetas:**
  * **Carpeta Modelo (`devpilot_core/static/models/`)**:
    * `apiClient.js`: Cliente HTTP asíncrono con inyección automática de token JWT (`Authorization: Bearer`).
    * Submodelos especializados: `authModel.js`, `servicesModel.js`, `telemetryModel.js`, `chaosModel.js`, `remediationModel.js`, `logsModel.js`, `chatModel.js` y `model.js`.
  * **Carpeta Controlador / Vista-Modelo (`devpilot_core/static/controllers/`)**:
    * `appController.js` y `controller.js`: Almacena el estado global observable (`currentUser`, `services`, `incidents`, `proposals`), propiedades computadas (`clusterStatus`, `avgLatency`), bus de eventos observador (`subscribe`, `notify`) y comandos ejecutables (`pollTelemetryCommand`, `loginWithCredentialsCommand`, `injectChaosCommand`, `requestProposalApprovalCommand`). Expuesto como `window.DevPilot.Controller` y `window.DevPilot.ViewModel`.
  * **Carpeta Vista (`devpilot_core/static/views/`)**:
    * `view.js`: Renderizado declarativo del DOM sin recargas de página (*Data Binding* reactivo), gráficos de series temporales con **Chart.js**, actualización de **Lucide Icons** y modales interactivos.
  * **Puentes y Arranque (`devpilot_core/static/js/` y `index.html`)**:
    * `eventBridges.js`: Conexión de eventos DOM (`onclick`, `onchange`) con el controlador.
    * `app.js`: Orquestador de inicio en `DOMContentLoaded`.
    * `index.html`: Estructura HTML5 limpia vinculada modularmente a cada carpeta.

---

### 3.2 Microservicios de Aplicación (`microservices/`)

Cada microservicio representa una pieza desacoplada de la arquitectura de comercio electrónico:

| Microservicio | Carpeta | Puerto | Tecnología | Responsabilidad |
| :--- | :--- | :--- | :--- | :--- |
| **Users** | `microservices/users/` | `3001` | Node.js (Express) | Gestión de cuentas y autenticación de clientes |
| **Products** | `microservices/products/` | `3002` | Python (FastAPI) | Catálogo e inventario de productos |
| **Orders** | `microservices/orders/` | `3003` | Python (FastAPI) | Procesamiento y trazabilidad de órdenes de compra |
| **Payments** | `microservices/payments/` | `3004` | Python (FastAPI) | Pasarela y validación de transacciones de pago |

#### 🩺 El Contrato de Microservicio de DevPilot
Para que cualquier microservicio sea compatible con el monitoreo e inyección de caos de DevPilot, implementa los siguientes endpoints estándar:
* `GET /health`: Retorna `{ "status": "UP", "uptimeSeconds": ..., "faultStatus": { ... } }`.
* `POST /fault/delay`: Inyecta un retardo forzado artificial en milisegundos (`delayMs`).
* `POST /fault/error`: Inyecta una tasa probabilística de fallos HTTP 500 (`errorRate`).
* `POST /fault/crash`: Simula una caída del servicio o terminación abrupta del proceso.
* `POST /fault/reset`: Restaura todas las variables de fallo a su estado nominal óptimo.

---

### 3.3 Infraestructura como Código (`docker-compose.yml`)

El archivo [`docker-compose.yml`](file:///c:/Users/fuze1/OneDrive/Documents/devpilot/docker-compose.yml) orquesta la topología distribuida del sistema:
* **Red Aislada (`devpilot_net`)**: Red interna tipo bridge que permite la resolución DNS automática por nombre de contenedor (ej: `http://users_service:3001`).
* **Montaje del Docker Socket (`/var/run/docker.sock`)**: Permite al contenedor `devpilot_core` comunicarse con el daemon del host para monitorear y reiniciar contenedores hermanos.
* **Persistencia de Datos (`devpilot_data`)**: Volumen local donde se aloja el archivo de base de datos SQLite `devpilot.db`, garantizando que métricas y auditorías persistan tras reinicios.
* **Healthchecks Nativos**: Cada contenedor define su directiva `healthcheck` de Docker para garantizar orden en la secuencia de arranque.

---

## 🔐 4. Flujos de Seguridad y Autenticación

```
[ Usuario ] ──( 1. Usuario + Password )──► [ API /api/auth/login ]
                                                    │
                                            ¿Credenciales válidas?
                                                    │ SÍ
                                                    ▼
[ Correo Gmail ] ◄──( 2. Código 6 dígitos )─── [ Módulo Email OTP ]
      │
[ Usuario ingresa código ] ──( 3. Verifica OTP )──► [ Emite Token JWT ]
                                                           │
                                                           ▼
[ Acceso al Dashboard con Rol RBAC (SuperAdmin / Admin / Cliente) ]
```

### Flujo de Step-Up Authentication con TOTP (RFC 6238)
Para prevenir errores operativos o ataques, acciones destructivas como **aprobar la remediación de un incidente** o **reiniciar contenedores** exigen un paso adicional:
1. El usuario hace clic en *"Aprobar Remediación"*.
2. Se despliega el modal de confirmación solicitando el código TOTP de 6 dígitos.
3. El backend valida el código contra el secreto del usuario (`auth.verify_totp_code`).
4. Solo si es válido, Docker Engine ejecuta la orden de reinicio y se asienta el evento en la bitácora inmutable de auditoría.

---

## 🎬 5. Guión Paso a Paso para Presentar el Proyecto

Utiliza este recorrido para realizar una demostración exitosa ante jurados, profesores o evaluadores técnicos:

### Paso 1: Introducción y Contexto (1 minuto)
* Presenta DevPilot como una plataforma de ingeniería de resiliencia y observabilidad autónoma basada en microservicios y Docker.
* Menciona que cumple con la especificación formal de requisitos **IEEE 830-1998**.

### Paso 2: Autenticación Segura y RBAC (2 minutos)
1. Abre el navegador en [http://localhost:8000](http://localhost:8000).
2. Muestra el selector de perfiles o inicia sesión como **`admin`** (Contraseña: `AdminPass2026*`).
3. Explica el flujo **MFA por Correo**: muestra cómo se envía el código OTP de 6 dígitos a la bandeja de correo.
4. Muestra la interfaz con tema oscuro y destaca el badge del rol en la barra superior.

### Paso 3: Telemetría en Vivo y Sondeo Autónomo (1 minuto)
* Muestra la cuadrícula de microservicios (`users`, `products`, `orders`).
* Explica que el monitor en segundo plano consulta `/health` cada 5 segundos de forma asíncrona y no invasiva.
* Señala las gráficas en tiempo real de latencia RTT construidas con Chart.js.

### Paso 4: Auto-Discovery de Microservicios (2 minutos)
1. Haz clic en el botón **"+ Registrar Microservicio"**.
2. Pulsa **"Escanear Red"**: DevPilot inspeccionará el Docker Engine y detectará el contenedor `devpilot_payments` que está en la red pero no registrado.
3. Al seleccionarlo, muestra cómo se autocompletan los parámetros técnicos y ajusta los umbrales de SLA (Latencia máx. y Error máx.).
4. Haz clic en **Registrar** y demuestra cómo el nuevo servicio se incorpora inmediatamente al ciclo de monitoreo.

### Paso 5: Ingeniería de Caos (Chaos Studio) (2 minutos)
1. Despliega la pestaña o panel de **Chaos Studio**.
2. Selecciona el servicio `orders`.
3. Inyecta una anomalía de **Latencia Crítica** (ej: 2500 ms) o **Tasa de Error 500** (ej: 50%).
4. Observa cómo, en cuestión de segundos, la tarjeta de `orders` cambia de color a rojo/ámbar y el sistema dispara una alerta sonora o visual.

### Paso 6: Detección de Incidentes y Diagnóstico con IA (2 minutos)
1. Dirígete a la sección de **Incidentes Operacionales**.
2. Muestra el incidente recién generado con su análisis de causa raíz.
3. Señala la **Explicación Simple** (diseñada para clientes no técnicos) y la **Recomendación Técnica del Copiloto IA** (para el equipo SRE).

### Paso 7: Remediación Human-in-the-Loop con Step-Up TOTP (2 minutos)
1. Localiza la propuesta de remediación sugerida (ej: `RESTART_CONTAINER` o `RESET_FAULT_STATE`).
2. Haz clic en **"Aprobar"**.
3. Muestra cómo el sistema bloquea la acción destructiva solicitando el código **TOTP de 6 dígitos (RFC 6238)**.
4. Ingresa el código (puedes consultar el código demo en vivo en la barra superior o en la API).
5. Observa cómo el contenedor es reiniciado en Docker, los errores cesan, y el monitor **auto-resuelve el incidente** devolviendo las métricas a estado verde (`HEALTHY`).
6. Muestra la pestaña de **Auditoría Forense** donde quedó registrado el operador, la hora exacta, el método de autenticación y el resultado.

---

## 🔑 6. Credenciales Oficiales de Demostración

| Rol | Usuario | Contraseña | Correo Electrónico | Capacidades Principales |
| :--- | :--- | :--- | :--- | :--- |
| 👑 **Super Administrador** | `superadmin` | `SuperAdmin2026*` | `superadmin@devpilot.io` | Gobernanza total, gestión de usuarios RBAC y configuración global |
| 🛠️ **Administrador** | `admin` | `AdminPass2026*` | `admin@devpilot.io` | SRE, inyección de caos, calibración de SLAs y remediación TOTP |
| 👁️ **Cliente** | `cliente` | `Cliente2026*` | `cliente@devpilot.io` | Vista de disponibilidad, métricas de SLAs y chat informativo |

* **Secreto TOTP Demo (RFC 6238):** `JBSWY3DPEHPK3PXP` (El dashboard incluye un botón para consultar el código actual de 6 dígitos en tiempo real).
* **Dirección de Recepción OTP Email:** `fuze1276@gmail.com` (Configurada en `.env`).

---

*Desarrollado para la gestión y resiliencia de arquitecturas cloud nativas modernas.*
