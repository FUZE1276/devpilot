# 🎓 Guía Maestra de Sustentación: Exposición de Build (30%) y Parcial de Ciclo DevOps

Este documento contiene el **guión paso a paso, los comandos exactos y la justificación técnica** para obtener la máxima calificación en tus dos evaluaciones:
1. **La Exposición del 30%:** Demostración práctica de la etapa de **BUILD** mediante herramientas sin depender de Docker.
2. **Los 2 Microservicios Nativos:** Demostración de software puro con sus 3 componentes (**Validador**, **Endpoint** y **Microservicio**).
3. **El Parcial en Mesa:** Demostración de **TODAS** las etapas del ciclo DevOps (**Test**, **Package/Release**, **Deploy**, **Operate**, **Monitor**) mediante herramientas reales.

---

## 📌 PARTE 1: La Exposición de la Etapa de BUILD (Tu 30%)

El docente indicó: *"No quiero que nos vuelvan a mostrar para qué sirve la etapa de Build, sino la herramienta que utilizaron: cómo se instaló, cómo se configuró y cómo se aplica"*.

### Herramientas que vas a presentar para el Build:
1. **GitHub Actions (CI Automation & Quality Gate Cloud):** Orquestador de Integración Continua.
2. **Compiladores y Linters Sintácticos Nativos (`py_compile` y `node --check`):** Verificación de sintaxis de código y árboles abstractos (AST) en tiempo de compilación.
3. **Script de Calidad de Build (`verify-build.ps1` / `verify-build.sh`):** Calificador integral del Quality Gate del proyecto.

---

### 🎙️ Guión de Exposición (Paso a Paso)

#### Paso 1: Introducción Rápida (30 segundos)
> *"Buenas tardes profesor. Para nuestra entrega del 30% nos correspondió la etapa de **BUILD**. En arquitecturas de software modernas, la etapa de Build no es únicamente compilar un binario; es el **Quality Gate** que garantiza que el código fuente es sintácticamente válido, que sus dependencias son seguras y reproducibles, y que supera las pruebas de integración antes de empaquetarse. Para demostrar esto, implementamos dos herramientas principales: **GitHub Actions** para la automatización en la nube y **Compiladores Sintácticos AST con un Script de Quality Gate** para ejecución local."*

#### Paso 2: Herramienta 1 — GitHub Actions (1 minuto)
* **1. Cómo se instaló/activó:**
  > *"GitHub Actions no requiere servidores físicos dedicados. Se activa mediante Runners en la nube provistos por GitHub configurando el entorno de ejecución (Ubuntu Latest con matrices de Python 3.11 y Node.js 20)."*
* **2. Cómo se configuró:**
  > *"Muestras el archivo [`.github/workflows/build-validation.yml`](file:///.github/workflows/build-validation.yml). Explicas que está estructurado en 3 fases mediante Jobs declarativos YAML:
  > - **Job 1 (Linting & Static Code Analysis):** Valida la compilación sintáctica de todos los módulos Python de backend y JavaScript de frontend con Node.
  > - **Job 2 (Automated Testing):** Instala dependencias y corre las suites de pruebas unitarias y de contrato.
  > - **Job 3 (Container Build & Validation):** Valida la sintaxis de infraestructura y empaquetado."*
* **3. Cómo se aplica en vivo:**
  > *"Muestras que cada `push` o `pull request` en el repositorio dispara automáticamente el pipeline, garantizando que código con errores sintácticos sea rechazado antes de integrarse."*

#### Paso 3: Herramienta 2 — Compiladores AST y Script de Calidad Local (1.5 minutos)
* **1. Cómo se instaló:**
  > *"Utiliza los compiladores nativos del entorno: `py_compile` integrado en la biblioteca estándar de Python y el analizador de sintaxis V8 de Node.js (`node --check`), sin dependencias externas pesadas."*
* **2. Cómo se configuró:**
  > *"Diseñamos el script de verificación formal [`verify-build.ps1`](file:///verify-build.ps1) (o [`verify-build.sh`](file:///verify-build.sh)) que automatiza la auditoría de 36 puntos de control."*
* **3. Cómo se aplica (Demostración en vivo):**
  > Abres una terminal de PowerShell y ejecutas:
  > ```powershell
  > .\verify-build.ps1
  > ```
  > Muestras en pantalla cómo valida:
  > - 10 archivos Python compilados sin errores de sintaxis AST.
  > - Los scripts del servidor Node.js y el validador.
  > - Los 14 módulos de frontend del patrón MVVM.
  > - La auditoría de archivos `.dockerignore` y dependencias.
  > - 12 pruebas unitarias Pytest y 5 pruebas nativas Node:Test.
  > - El estado final: **`ESTADO: [OK] BUILD EXITOSO (Quality Gate Aprobado)`**.

---

## 📌 PARTE 2: Los 2 Microservicios de Software Puro (NO como Docker)

El docente requirió explícitamente: *"Crear dos microservicios no como docker... hay que hacerlo como software... el script del endpoint, el script del validador y el script del microservicio"*.

### Microservicio 1: Órdenes de Compra (Python / FastAPI)
* **Ubicación:** Carpeta [`microservices/orders/`](file:///microservices/orders)
* **Tecnología:** Python 3.11+, FastAPI, Pydantic v2.

| Componente Pedido por el Docente | Archivo | Qué hace / Qué mostrarle |
| :--- | :--- | :--- |
| **1. El Script del Validador** | [`microservices/orders/validator.py`](file:///microservices/orders/validator.py) | Define esquemas de datos estrictos (`CreateOrderSchema`, `OrderItemSchema`, `DelayRequestSchema`). Aplica reglas de negocio: rechaza cantidades negativas, precios menores a cero y productos duplicados. Ejecútalo solo con: `py validator.py` para mostrar su autoverificación en consola. |
| **2. El Script del Endpoint** | [`microservices/orders/main.py`](file:///microservices/orders/main.py) | Define los endpoints REST: `GET /health`, `GET /orders`, `POST /orders`, `GET /orders/{id}`, `DELETE /orders/{id}`, `GET /metrics` y los endpoints de caos (`/fault/*`). |
| **3. El Script del Microservicio** | [`microservices/orders/main.py`](file:///microservices/orders/main.py) | Al final contiene el bloque ejecutable `if __name__ == '__main__': uvicorn.run(...)`. Se levanta como software nativo ejecutando: `py main.py`. |

#### Cómo demostrarlo en vivo:
1. En una terminal, corre el validador:
   ```powershell
   cd microservices\orders
   py validator.py
   ```
   *(Mostrarás que valida payloads correctos y rechaza datos inválidos).*
2. Enciende el microservicio:
   ```powershell
   py main.py
   ```
   *(El servicio arranca en `http://127.0.0.1:3003` sin Docker).*
3. Abre en el navegador o con curl:
   - `http://127.0.0.1:3003/health`
   - `http://127.0.0.1:3003/orders`

---

### Microservicio 2: Gestión de Usuarios (Node.js / Express)
* **Ubicación:** Carpeta [`microservices/users/`](file:///microservices/users)
* **Tecnología:** Node.js v20+, Express v4.

| Componente Pedido por el Docente | Archivo | Qué hace / Qué mostrarle |
| :--- | :--- | :--- |
| **1. El Script del Validador** | [`microservices/users/validator.js`](file:///microservices/users/validator.js) | Valida estructura de objetos, expresión regular de correo RFC 5322, nombres con longitud mínima y tipos válidos (`validateUserPayload`, `validateDelayPayload`). Ejecútalo con: `node validator.js`. |
| **2. El Script del Endpoint** | [`microservices/users/server.js`](file:///microservices/users/server.js) | Define las rutas `GET /health`, `GET /users`, `POST /users`, `DELETE /users/:id` y `/fault/*`. |
| **3. El Script del Microservicio** | [`microservices/users/server.js`](file:///microservices/users/server.js) | El servidor Express nativo que escucha en el puerto `3001` con `node server.js`. |

#### Cómo demostrarlo en vivo:
1. En una terminal, corre el validador:
   ```powershell
   cd microservices\users
   node validator.js
   ```
2. Enciende el microservicio:
   ```powershell
   node server.js
   ```
3. Abre en el navegador o con curl:
   - `http://localhost:3001/health`
   - `http://localhost:3001/users`

---

## 📌 PARTE 3: El Parcial en Mesa (Todas las Etapas del Ciclo DevOps)

El docente dijo: *"De las etapas que no son ni Plan ni Code... el que expuso una no se la vuelvo a preguntar... la idea es que hagan todas y si les pregunto una y no la tienen, pues pierden"*.

Aquí tienes la respuesta exacta y la herramienta configurada para **CADA ETAPA**:

---

### 🧪 1. Etapa de TEST (Pruebas Automatizadas)
* **Herramientas:** **Pytest** (Python) y **Node:Test Runner** (Node.js).
* **Cómo se configuró:**
  - Archivos en [`tests/`](file:///tests):
    - `test_auth_and_security.py`: Pruebas de seguridad JWT HS256, expiración, firmas manipuladas, TOTP RFC 6238 y jerarquía RBAC.
    - `test_database.py`: Pruebas de inicialización de esquemas SQLite ACID, transacciones y bitácora forense.
    - `test_microservices_contracts.py`: Pruebas de contrato HTTP contra los microservicios.
  - En Node.js: `microservices/users/test/users.test.js` (5 pruebas nativas de endpoints y simulación de fallos).
* **Cómo se demuestra al profesor:**
  Ejecutas en consola:
  ```powershell
  py -m pytest tests/ -v
  ```
  *(12 pruebas pasando en menos de 1 segundo)*
  Y en Node.js:
  ```powershell
  cd microservices\users
  npm test
  ```
  *(5 pruebas pasando)*

---

### 📦 2. Etapa de RELEASE / PACKAGE (Empaquetado y Versionado)
* **Herramientas:** **Docker Buildx** y **Manifiestos de Empaquetado Semántico**.
* **Cómo se configuró:**
  - Cada microservicio posee su [`Dockerfile`](file:///microservices/orders/Dockerfile) con imagen base ligera (`python:3.11-slim` o `node:20-alpine`), copia selectiva con dependencias en caché y metadata de versión.
  - Versionado formal semántico (`version: "1.0.0"`) en endpoints `/health` y `package.json`.
* **Cómo se demuestra al profesor:**
  Ejecutas en consola:
  ```powershell
  docker compose build
  ```
  *(Muestras cómo Docker Buildx empaqueta los artefactos de software en imágenes inmutables etiquetadas y listas para distribución).*

---

### 🚀 3. Etapa de DEPLOY (Despliegue y Orquestación)
* **Herramientas:** **Docker & Docker Compose**.
* **Cómo se configuró:**
  - Archivo [`docker-compose.yml`](file:///docker-compose.yml).
  - Define una topología de **5 servicios**: `devpilot_core`, `users_service`, `products_service`, `orders_service`, `payments_service`.
  - Configura la red privada bridge **`devpilot_net`** con resolución DNS interna por nombre de servicio.
  - Configura el volumen persistente **`devpilot_data`** para la base de datos SQLite.
  - Define directivas **`healthcheck`** nativas con intervalos y reintentos para orquestar el orden de encendido.
* **Cómo se demuestra al profesor:**
  Ejecutas en consola:
  ```powershell
  docker compose up -d
  docker compose ps
  ```
  *(Muestras los 5 contenedores activos, sus puertos expuestos y sus healthchecks en estado healthy).*

---

### 🛠️ 4. Etapa de OPERATE (Operación, Mantenimiento y Recuperación)
* **Herramientas:** **Docker Engine SDK** + **DevPilot Orchestrator** + **Step-Up TOTP (RFC 6238)**.
* **Cómo se configuró:**
  - Módulo [`devpilot_core/docker_manager.py`](file:///devpilot_core/docker_manager.py) conectado al Docker Socket (`/var/run/docker.sock`).
  - Funciones operativas:
    1. **Reinicio y Auto-Recovery de Contenedores:** `restart_service_container()`.
    2. **Auto-Discovery de Servicios:** `discover_candidate_services()` escanea contenedores no registrados en la red (ej. detecta `payments_service` en caliente).
    3. **Seguridad Operacional (Step-Up TOTP):** En [`devpilot_core/auth.py`](file:///devpilot_core/auth.py), acciones destructivas de operación exigen código TOTP de 6 dígitos.
    4. **Auditoría Forense:** Cada operación queda registrada en la tabla `remediation_logs` con fecha, operador y resultado.
* **Cómo se demuestra al profesor:**
  1. Abres el Dashboard en `http://localhost:8000`.
  2. En la sección de **Incidentes**, apruebas una remediación de reinicio ingresando el código TOTP demo (`JBSWY3DPEHPK3PXP`).
  3. Muestras en la terminal cómo Docker Engine reinicia el contenedor y en el panel cómo se registra la entrada en la **Bitácora de Auditoría Forense**.

---

### 📊 5. Etapa de MONITOR (Monitoreo y Observabilidad)
* **Herramientas:** **DevPilot Core Observability Engine** + **Chart.js Dashboard SPA**.
* **Cómo se configuró:**
  - Módulo [`devpilot_core/monitor.py`](file:///devpilot_core/monitor.py).
  - Hilo asíncrono no invasivo que sondea cada **5 segundos** el endpoint `/health` de todos los microservicios registrados.
  - Calcula en tiempo real:
    - **Latencia RTT (Round Trip Time)** en milisegundos.
    - **Tasa de Errores HTTP 5xx**.
    - **Disponibilidad y Cumplimiento de SLA** (Ventana móvil).
  - Interfaz web reactiva en [`devpilot_core/static/`](file:///devpilot_core/static) construida con patrón **MVVM** (Model-View-ViewModel) y gráficos en tiempo real con Chart.js.
  - **Chaos Studio:** Panel integrado para inyectar latencia forzada o tasas de error y observar cómo el monitor detecta el fallo en segundos.
* **Cómo se demuestra al profesor:**
  1. Abres `http://localhost:8000`.
  2. Muestras las tarjetas de los microservicios en verde con sus gráficos de latencia RTT.
  3. Vas a **Chaos Studio**, seleccionas `orders`, e inyectas un retardo de `2500 ms`.
  4. Muestras cómo en el siguiente ciclo de sondeo (5s) la tarjeta cambia de color a rojo/ámbar, se genera un incidente automático y el motor de observabilidad calcula la degradación del SLA.

---

## 🕹️ Comandos Rápidos de Referencia para el Día de la Presentación

| Objetivo | Comando |
| :--- | :--- |
| **Demostrar el Build completo (30%)** | `.\verify-build.ps1` |
| **Probar los Microservicios Nativos (Sin Docker)** | `.\start-local.ps1` (enciende todo en local) <br> `.\stop-local.ps1` (apaga todo) |
| **Probar el Validador de Orders** | `cd microservices\orders && py validator.py` |
| **Probar el Validador de Users** | `cd microservices\users && node validator.js` |
| **Ejecutar Pruebas Unitarias (Test Stage)** | `py -m pytest tests/ -v` |
| **Desplegar en Contenedores (Deploy Stage)** | `docker compose up -d` |
| **Ver Estado de Contenedores** | `docker compose ps` |
| **Detener Contenedores** | `docker compose down` |
| **Acceder al Dashboard de Monitoreo** | [http://localhost:8000](http://localhost:8000) (Admin: `admin` / `AdminPass2026*`) |
