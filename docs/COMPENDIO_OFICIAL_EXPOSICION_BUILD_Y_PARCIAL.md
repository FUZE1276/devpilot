# 📘 DEV_PILOT SRE: COMPENDIO MAESTRO DE SUSTENTACIÓN
## Guía Completa de la Exposición de Build (30%) y Examen Parcial de DevOps

**Proyecto:** DevPilot SRE Platform  
**Repositorio Oficial:** [github.com/FUZE1276/devpilot](https://github.com/FUZE1276/devpilot)  
**Rama:** `main` | **Fecha:** Octubre 2026  
**Autor:** FUZE1276  

---

# 📑 TABLA DE CONTENIDO
1. [Resumen Ejecutivo y Reglas del Juego](#1-resumen-ejecutivo-y-reglas-del-juego)
2. [PARTE 1: Exposición del 30% - Etapa de BUILD](#2-parte-1-exposición-del-30---etapa-de-build)
   - [Regla de Oro del Profesor](#regla-de-oro-del-profesor)
   - [Guion Diapositiva por Diapositiva (Slides 1 a 8)](#guion-diapositiva-por-diapositiva-slides-1-a-8)
   - [Los 2 Microservicios en Software Puro (Sin Docker)](#los-2-microservicios-en-software-puro-sin-docker)
   - [El Script de Quality Gate (verify-build.ps1)](#el-script-de-quality-gate-verify-buildps1)
3. [PARTE 2: Examen Parcial en Mesa - Las 5 Etapas del Ciclo DevOps](#3-parte-2-examen-parcial-en-mesa---las-5-etapas-del-ciclo-devops)
   - [1. Etapa de TEST (Pruebas Automatizadas)](#1-etapa-de-test-pruebas-automatizadas)
   - [2. Etapa de RELEASE / PACKAGE (Empaquetado)](#2-etapa-de-release--package-empaquetado)
   - [3. Etapa de DEPLOY (Despliegue y Orquestación)](#3-etapa-de-deploy-despliegue-y-orquestación)
   - [4. Etapa de OPERATE (Operación y Remediación)](#4-etapa-de-operate-operación-y-remediación)
   - [5. Etapa de MONITOR (Monitoreo y Observabilidad)](#5-etapa-de-monitor-monitoreo-y-observabilidad)
4. [PARTE 3: Banco de Preguntas Trampa del Docente y Respuestas](#4-parte-3-banco-de-preguntas-trampa-del-docente-y-respuestas)
5. [PARTE 4: Cheat Sheet de Comandos Rápidos de Emergencia](#5-parte-4-cheat-sheet-de-comandos-rápidos-de-emergencia)

---

# 1. Resumen Ejecutivo y Reglas del Juego

Tienes dos evaluaciones basadas en la misma plataforma:
1. **La Exposición del 30% (Etapa de BUILD):**
   - Presentación de diapositivas con diapositivas reales y terminales reales.
   - Demostración de herramientas de Build: **GitHub Actions**, **Compiladores AST (`py_compile`, `node --check`)** y **Script de Quality Gate (`verify-build.ps1`)**.
   - Demostración de **2 microservicios nativos como software puro** (Orders y Users), mostrando sus 3 elementos: Validador, Endpoint y Microservicio ejecutable sin Docker.
2. **El Examen Parcial (En Mesa Cara a Cara):**
   - El profesor pregunta por sorteo o criterio propio cualquiera de las etapas del ciclo de vida DevOps, **exceptuando Plan, Code y Build**.
   - Las 5 etapas preparadas al 100% son: **TEST**, **RELEASE**, **DEPLOY**, **OPERATE**, **MONITOR**.

---

# 2. PARTE 1: Exposición del 30% - Etapa de BUILD

### Regla de Oro del Profesor
> *"No quiero que nos vuelvan a mostrar para qué sirve la etapa de Build, sino la herramienta que utilizaron: cómo se instaló, cómo se configuró y cómo se aplica."*  
> *"Crear dos microservicios no como docker... hay que hacerlo como software... el script del endpoint, el script del validador y el script del microservicio."*

---

## Guion Diapositiva por Diapositiva (Slides 1 a 8)

### 📌 Diapositiva 1: Portada y Declaración de Calidad
* **Título en Diapositiva:** Arquitectura y Quality Gate de la Etapa de Build
* **Subtítulo:** Automatización en la Nube con GitHub Actions, Compiladores AST y Verificación de Software Puro
* **Elementos en pantalla:**
  1. *Herramientas reales de build:* GitHub Actions, py_compile y node --check.
  2. *Microservicios nativos:* Orders (Python) y Users (Node.js) sin contenedores.
  3. *37/37 pruebas aprobadas:* Script oficial verify-build.ps1, 0 fallos.
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"Buenas tardes profesor y compañeros. Hoy presentamos la sustentación de la etapa de **BUILD** aplicada a nuestra plataforma **DevPilot SRE Platform**.  
  > En la ingeniería de software moderna, la etapa de Build no se limita a empaquetar un archivo; es el **Quality Gate** que certifica que el código fuente es sintácticamente impecable, que sus contratos de datos están blindados y que los módulos se integran sin romper el sistema antes de generar cualquier artefacto.  
  > Hoy no venimos a dar teoría de qué es Build, sino a demostrar con herramientas reales cómo se configuró y ejecutó: en la nube mediante **GitHub Actions**, en local con **Compiladores Sintácticos AST**, y en software puro con dos microservicios nativos en Python y Node.js respaldados por una batería de 37 verificaciones con 0 fallos."*

---

### 📌 Diapositiva 2: El Pipeline de Build en 4 Fases (Quality Gate)
* **Título en Diapositiva:** El Pipeline de Build en 4 Fases (Quality Gate)
* **Elementos en pantalla:**
  - Diagrama de flujo: Fase 1 (Linting estático) ➔ Fase 2 (Aislamiento de contexto) ➔ Fase 3 (Pruebas automatizadas) ➔ Fase 4 (Quality Gate).
  - Métricas: 14 módulos MVVM, 2 parsers AST, 4 fases | 12 Pytest, 5 Node:Test, 37 aprobadas.
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"Para estructurar la construcción de DevPilot, dividimos el proceso de Build en un pipeline formal de cuatro fases secuenciales:  
  > 1. **Fase 1: Linting estático y compilación sintáctica:** Pasamos el código por los árboles sintácticos (AST) de Python y el motor V8 de Node.js, verificando también los 14 módulos del frontend MVVM.  
  > 2. **Fase 2: Aislamiento de contexto y auditoría:** Verificamos que los manifiestos `.dockerignore` y las dependencias excluyan carpetas innecesarias o archivos sensibles para garantizar builds limpios e higiénicos.  
  > 3. **Fase 3: Pruebas automatizadas unitarias y de contratos:** Ejecutamos 12 pruebas de Pytest (seguridad JWT, autenticación multifactor TOTP, integridad SQLite) y 5 pruebas nativas de Node:Test.  
  > 4. **Fase 4: Evaluación final del Quality Gate:** Si una sola prueba o coma falla, el build se aborta con código de salida 1 (Fail-Fast); si todo pasa, se autoriza con código de salida 0."*

---

### 📌 Diapositiva 3: Herramienta 1: GitHub Actions (CI en la Nube)
* **Título en Diapositiva:** GitHub Actions: CI en la Nube
* **Elementos en pantalla:**
  - Columna 1 (Instalación y Configuración): Fragmento YAML (`on: [push, pull_request]`, matrix de Python 3.11 y Node 20).
  - Columna 2 (Aplicación y Verificación): Captura del pipeline en verde en GitHub con sus 3 jobs (`1. Linting & Static Code Analysis`, `2. Automated Testing Suite`, `3. Container Images Build`).
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"Nuestra primera herramienta de build es **GitHub Actions**, que resuelve la integración continua y la reproducibilidad en la nube.  
  > - **Instalación:** No requiere servidores dedicados locales; se aprovisiona automáticamente en Runners virtuales `ubuntu-latest` en la infraestructura de GitHub.  
  > - **Configuración:** Creamos el archivo de flujo de trabajo `.github/workflows/build-validation.yml`. Allí definimos una matriz de compatibilidad con Python 3.11 y Node.js 20, configurando triggers automáticos ante eventos de `push` o `pull_request`.  
  > - **Aplicación y Verificación:** Como se observa en la captura de pantalla real de nuestro repositorio, cada commit dispara un pipeline de tres jobs: primero el análisis estático, luego las suites de pruebas y finalmente la validación de empaquetado. Si un desarrollador introduce un error sintáctico, GitHub Actions bloquea el pipeline de inmediato bajo la política Fail-Fast."*

---

### 📌 Diapositiva 4: Herramienta 2: Compiladores Sintácticos AST Locales
* **Título en Diapositiva:** Compiladores Sintácticos AST Locales
* **Elementos en pantalla:**
  - Columna 1: `py_compile` (AST de Python) con captura de terminal en verde (`Compilación AST exitosa: 0 errores sintácticos`).
  - Columna 2: `node --check` (Parser V8 de Node.js) con captura de terminal en verde validando `server.js`, `validator.js` y los 14 archivos frontend.
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"Como segunda herramienta de Build, implementamos **compiladores sintácticos locales basados en AST (Abstract Syntax Tree)**. Esto permite validar la integridad del código sin necesidad de levantar los servicios ni depender de Docker.  
  > - **Para Python:** Utilizamos el módulo estándar `py_compile`. Como ven en la captura izquierda, este comando compila el código a bytecode `.pyc` en memoria. Si existe un error de indentación o un carácter mal ubicado, el compilador genera un `SyntaxError` con la línea exacta y detiene el build.  
  > - **Para JavaScript/Node.js:** Utilizamos la bandera nativa del motor V8 `node --check`. Como muestra la captura derecha, este analizador examina el backend de Node y los 14 módulos de nuestro frontend MVVM, asegurando que no existan errores de sintaxis antes de ejecutarse."*

---

### 📌 Diapositiva 5: Microservicio 1 (Software Puro): Orders en Python FastAPI
* **Título en Diapositiva:** Orders: Python FastAPI (Microservicio 1 · Software Puro)
* **Elementos en pantalla:**
  - Columna 1: El Validador (`validator.py`) con captura mostrando la ejecución de autoverificación y rechazo de datos corruptos.
  - Columna 2: Endpoints y Microservicio (`main.py`) con captura mostrando Uvicorn arrancado nativo en el puerto `3003` y la respuesta JSON de `GET /health`.
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"Cumpliendo con el requerimiento de presentar microservicios como software puro y no como contenedores, aquí tenemos el microservicio de **Orders** desarrollado en Python con FastAPI.  
  > - **1. El Validador (`validator.py`):** Construido con esquemas estrictos de Pydantic v2 (`CreateOrderSchema`, `OrderItemSchema`). Contiene reglas de negocio que rechazan cantidades menores o iguales a cero, precios negativos y productos duplicados. Como ven en la captura, al correr `py validator.py` se ejecuta su suite de autoverificación, demostrando cómo rechaza un dato corrupto y aprueba un payload válido.  
  > - **2 y 3. El Endpoint y el Microservicio (`main.py`):** Define rutas REST como `/health`, `/orders` y `/metrics`. En su bloque final contiene el ejecutable de Uvicorn. Como muestra la terminal, se inicia con `py main.py`, corriendo de forma nativa en el puerto 3003 sin tocar Docker y respondiendo inmediatamente a la consulta HTTP."*

---

### 📌 Diapositiva 6: Microservicio 2 (Software Puro): Users en Node.js Express
* **Título en Diapositiva:** Users: Node.js Express (Microservicio 2 · Software Puro)
* **Elementos en pantalla:**
  - Columna 1: El Validador (`validator.js`) con captura de autoverificación en consola rechazando correos y nombres inválidos.
  - Columna 2: Endpoints y Microservicio (`server.js`) con captura mostrando el servidor nativo en el puerto `3001` y la respuesta JSON de `GET /health`.
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"El segundo microservicio en software puro es **Users**, desarrollado en Node.js con Express.  
  > - **1. El Validador (`validator.js`):** Implementa la función `validateUserPayload` que utiliza una expresión regular estricta bajo el estándar RFC 5322 para correos electrónicos y exige nombres válidos de al menos dos caracteres. Al ejecutar `node validator.js`, la autoverificación integrada demuestra en consola cómo detecta y rechaza datos inválidos con código 400.  
  > - **2 y 3. El Endpoint y el Microservicio (`server.js`):** Implementa los controladores para `/users`, `/health` y los endpoints de inyección de fallos. Como se observa en la terminal, se arranca como un proceso nativo mediante `node server.js` en el puerto 3001, verificando su disponibilidad instantánea mediante `GET /health`."*

---

### 📌 Diapositiva 7: Herramienta 3: Script Oficial de Quality Gate (verify-build.ps1)
* **Título en Diapositiva:** Script Oficial de Quality Gate: verify-build.ps1
* **Elementos en pantalla:**
  - Columna 1: Estructura del Script (Orquestador en PowerShell con 37 verificaciones, 4 fases, 0 fallos, Exit code 0/1).
  - Columna 2: Salida oficial en terminal terminando en banner verde con resumen: `Pruebas y Verificaciones Ejecutadas: 37 | Aprobadas con Éxito: 37 | Fallos Detectados: 0`.
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"Para unificar todas las comprobaciones de Build en un único comando reproducible, diseñamos la tercera herramienta: nuestro script oficial de Quality Gate, `verify-build.ps1`.  
  > - **Estructura:** Este orquestador automatiza las cuatro fases del pipeline: compila sintácticamente el backend y frontend, audita los archivos de configuración, verifica el aislamiento de dependencias y ejecuta las pruebas unitarias.  
  > - **Criterio de aprobación:** Aplica una lógica booleana estricta: ante cualquier fallo devuelve código de salida 1; si todas las pruebas pasan, devuelve 0. Como ven en la captura real de nuestra terminal, el script ejecuta las 37 verificaciones con 0 fallos, otorgando el sello de calidad: **BUILD EXITOSO (Quality Gate Aprobado)**."*

---

### 📌 Diapositiva 8: Conclusiones y Demostración en Vivo
* **Título en Diapositiva:** Conclusiones y Demostración en Vivo
* **Elementos en pantalla:**
  - Resumen de garantías: Cero errores en runtime, Contratos blindados, Reproducibilidad total entre local y CI.
  - Tabla de comandos rápidos: `.\verify-build.ps1`, `py validator.py`, `node validator.js`.
* **🎙️ Cómo debes exponerla (Script verbal):**
  > *"En conclusión, la etapa de Build en DevPilot nos otorga tres garantías críticas:  
  > 1. **Cero fallos en tiempo de ejecución:** Cualquier error sintáctico o gramatical se atrapa en la compilación AST antes de que el código llegue a producción.  
  > 2. **Contratos de API inmutables:** Los validadores formales impiden la inyección de datos corruptos entre microservicios.  
  > 3. **Paridad total:** El mismo estándar de calidad que evalúa GitHub Actions en la nube se ejecuta de manera idéntica en local con nuestro script de Quality Gate.  
  > Con esto demostramos las herramientas de Build y quedamos listos para realizar cualquier demostración en vivo que el docente solicite."*

---

## Los 2 Microservicios en Software Puro (Sin Docker)

Para responder inmediatamente si el profesor pide ejecutarlos en vivo en la terminal:

### Microservicio 1: Orders (Python FastAPI)
* **Ubicación:** `microservices/orders/`
* **Validador (`validator.py`):**
  ```powershell
  cd "c:\Users\fuze1\OneDrive\Documents\devpilot\microservices\orders"
  py validator.py
  ```
* **Servicio (`main.py` en puerto 3003):**
  ```powershell
  py main.py
  ```
* **Comprobación en otra pestaña:**
  ```powershell
  curl http://127.0.0.1:3003/health
  ```

### Microservicio 2: Users (Node.js Express)
* **Ubicación:** `microservices/users/`
* **Validador (`validator.js`):**
  ```powershell
  cd "c:\Users\fuze1\OneDrive\Documents\devpilot\microservices\users"
  node validator.js
  ```
* **Servicio (`server.js` en puerto 3001):**
  ```powershell
  node server.js
  ```
* **Comprobación en otra pestaña:**
  ```powershell
  curl http://localhost:3001/health
  ```

---

## El Script de Quality Gate (verify-build.ps1)
Ejecutable desde la raíz del proyecto:
```powershell
cd "c:\Users\fuze1\OneDrive\Documents\devpilot"
.\verify-build.ps1
```
* **Puntos de auditoría (Total: 37):**
  - 10 módulos Python compilados con `py_compile`.
  - 2 scripts backend Node.js analizados con `node --check`.
  - 14 módulos de frontend MVVM validados con `node --check`.
  - 3 comprobaciones de aislamiento (`.dockerignore`, `package.json`, `requirements.txt`).
  - 8 verificaciones de pruebas unitarias y contratos (Pytest y Node:Test).

---

# 🎯 ALINEACIÓN TOTAL CON LAS DIAPOSITIVAS DEL ING. CARLOS PINEDA

El docente presentó las diapositivas oficiales: **"Aplicación del Ciclo de Vida del Software - Proyecto Empresarial Web con Herramientas Open Source"**.  
Para garantizar un 5.0 (100%) tanto en la exposición del 30% como en el parcial, **DevPilot tiene implementada y probada al menos una herramienta real de sus diapositivas para CADA ETAPA**:

| Diapositiva del Docente | Etapa DevOps | Herramienta Oficial Implementada | Archivo de Configuración | Comando de Prueba en Terminal | Estado y Resultado Verificado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Slide 6 & 7** | **Etapa 3: Construir (BUILD)** | **Gradle** & **Apache Maven** | [`build.gradle`](file:///build.gradle) <br> [`pom.xml`](file:///pom.xml) | `gradle build` <br> o `mvn compile` | `BUILD SUCCESSFUL` (Compila AST Python, parser V8 Node y 37 checks). |
| **Slide 8** | **Etapa 4: Ensayo (TEST)** | **JUnit 5 (Jupiter)** | [`src/test/java/.../DevPilotBuildVerificationTest.java`](file:///src/test/java/io/devpilot/sre/DevPilotBuildVerificationTest.java) | `mvn test` | `Tests run: 4, Failures: 0, Errors: 0` (Pruebas unitarias formales en Java). |
| **Slide 10 & 11** | **Etapa 5: Lanzamiento (RELEASE)** | **Jenkins** & **GitLab CI/CD** | [`Jenkinsfile`](file:///Jenkinsfile) <br> [`.gitlab-ci.yml`](file:///.gitlab-ci.yml) | Mostrar archivo y correr `docker compose build` | Pipeline declarativo con 5 fases automáticas y empaquetado inmutable. |
| **Slide 12** | **Etapa 6: Desplegar (DEPLOY)** | **Docker & Compose** | [`docker-compose.yml`](file:///docker-compose.yml) | `docker compose up -d` <br> `docker compose ps` | 5 microservicios levantados, red bridge `devpilot_net` y `healthy`. |
| **Slide 14** | **Etapa 7: Operar (OPERATE)** | **Nginx** | [`nginx/nginx.conf`](file:///nginx/nginx.conf) | `docker compose up -d nginx_proxy` | Nginx actúa como Reverse Proxy y API Gateway ruteando tráfico a los microservicios. |
| **Slide 17** | **Etapa 8: Monitor (MONITOR)** | **Prometheus** | [`prometheus/prometheus.yml`](file:///prometheus/prometheus.yml) | `docker compose up -d prometheus` o ver `/metrics` | Motor de observabilidad que scrapea telemetría y métricas cada 5 segundos. |

---

# 3. PARTE 2: Examen Parcial en Mesa - Las 5 Etapas del Ciclo DevOps

El docente evalúa el ciclo DevOps seleccionando **cualquiera de las etapas restantes**:
> *"De las etapas que no son ni Plan ni Code... el que expuso una no se la vuelvo a preguntar... la idea es que hagan todas y si les pregunto una y no la tienen, pues pierden."*

A continuación tienes la ficha técnica, herramienta, configuración y comandos para cada una de las 5 etapas:

---

## 1. Etapa de TEST (Pruebas Automatizadas)

* **Objetivo de la etapa:** Validar la lógica de negocio, la seguridad criptográfica, las transacciones ACID y los contratos entre servicios antes del empaquetado.
* **Herramientas utilizadas:**
  1. **Pytest (Python):** Framework de testing automatizado con aserciones declarativas.
  2. **Node:Test (Node.js):** Runner de pruebas nativo integrado en Node.js v20+ sin dependencias externas.
* **Cómo se configuró:**
  - `tests/test_auth_and_security.py`: Pruebas de tokens JWT (HS256, expiración, firmas manipuladas), generación y verificación de códigos TOTP RFC 6238, y permisos RBAC (`admin`, `sre_lead`, `operator`).
  - `tests/test_database.py`: Pruebas de inicialización de tablas SQLite, persistencia ACID, aislamiento transaccional y bitácora de auditoría.
  - `tests/test_microservices_contracts.py`: Pruebas de contrato HTTP sobre los payloads de los microservicios.
  - `microservices/users/test/users.test.js`: Pruebas nativas de integración y rutas sobre el microservicio de usuarios.
* **🎙️ Qué decirle al profesor:**
  > *"Para la etapa de TEST implementamos dos suites de pruebas automatizadas: Pytest para el backend central y Node:Test para los microservicios en JavaScript. Evaluamos seguridad criptográfica JWT, doble factor TOTP, consistencia transaccional SQLite y contratos de API."*
* **💻 Comandos para demostrar en vivo:**
  ```powershell
  # 1. Pruebas de Python (12 pruebas unitarias y de integración)
  py -m pytest tests/ -v

  # 2. Pruebas de Node.js (5 pruebas nativas)
  cd microservices\users ; npm test ; cd ..\..
  ```
* **Resultado esperado:** 12 tests en verde en menos de 1 segundo en Pytest y 5 tests pasando en Node.

---

## 2. Etapa de RELEASE / PACKAGE (Empaquetado)

* **Objetivo de la etapa:** Generar artefactos de software inmutables, versionados semánticamente y listos para distribución en cualquier entorno.
* **Herramientas utilizadas:**
  - **Docker Buildx:** Motor de construcción de imágenes de contenedores.
  - **Semantic Versioning (SemVer 2.0.0):** Versionado formal en manifiestos y metadatos.
* **Cómo se configuró:**
  - Cada microservicio cuenta con su propio `Dockerfile`:
    - `microservices/orders/Dockerfile`: Imagen base ligera `python:3.11-slim`, usuario no privilegiado, copia de `requirements.txt` en capas de caché.
    - `microservices/users/Dockerfile`: Imagen base `node:20-alpine`, instalación limpia con `npm ci --only=production`.
  - Manifiestos `.dockerignore` configurados en cada carpeta para excluir `__pycache__`, `.git`, `.env` y pruebas, asegurando imágenes livianas.
  - Etiquetado de versión semántica formal `version: "1.0.0"` expuesto en los metadatos de `/health`.
* **🎙️ Qué decirle al profesor:**
  > *"En la etapa de RELEASE convertimos el código probado en artefactos inmutables mediante Docker Buildx. Cada componente cuenta con Dockerfiles optimizados multi-capa con imágenes base ultraligeras (Alpine y Slim) y manifiestos .dockerignore para asegurar higiene y mínimo tamaño."*
* **💻 Comandos para demostrar en vivo:**
  ```powershell
  # Construir las imágenes del sistema
  docker compose build

  # Listar los artefactos generados y su versionado
  docker images | Select-String "devpilot"
  ```
* **Resultado esperado:** 5 imágenes Docker creadas con nombres estandarizados y etiquetas de versión.

---

## 3. Etapa de DEPLOY (Despliegue y Orquestación)

* **Objetivo de la etapa:** Poner en funcionamiento los artefactos empaquetados en un entorno de ejecución orquestado con redes y almacenamiento configurados.
* **Herramientas utilizadas:**
  - **Docker Compose:** Orquestador declarativo multi-contenedor.
* **Cómo se configuró:**
  - Archivo `docker-compose.yml` en la raíz del proyecto.
  - Orquesta **5 servicios independientes**:
    1. `devpilot_core`: Orquestador y Dashboard principal (puerto `8000`).
    2. `users_service`: Gestión de usuarios (puerto `3001`).
    3. `products_service`: Catálogo de productos (puerto `3002`).
    4. `orders_service`: Órdenes de compra (puerto `3003`).
    5. `payments_service`: Pasarela de pagos (puerto `3004`).
  - Red privada bridge: `devpilot_net` que permite comunicación interna por DNS (`http://users_service:3001`).
  - Volumen persistente: `devpilot_data` para proteger la base de datos SQLite ante reinicios.
  - Mecanismo de **Healthcheck** nativo en cada contenedor con reintentos e intervalos de chequeo.
* **🎙️ Qué decirle al profesor:**
  > *"Para el DEPLOY utilizamos Docker Compose como orquestador declarativo. Configuramos una topología distribuida de cinco microservicios intercomunicados por una red interna bridge llamada devpilot_net, con persistencia de datos mediante volúmenes y políticas de auto-reinicio y healthcheck activas."*
* **💻 Comandos para demostrar en vivo:**
  ```powershell
  # Desplegar los 5 contenedores en background
  docker compose up -d

  # Verificar estado, puertos y healthcheck
  docker compose ps
  ```
* **Resultado esperado:** 5 contenedores en estado `Up` y `healthy`.

---

## 4. Etapa de OPERATE (Operación y Remediación)

* **Objetivo de la etapa:** Administrar el ciclo de vida de los servicios en producción, ejecutar acciones correctivas, descubrimiento dinámico de componentes y registro de auditoría.
* **Herramientas utilizadas:**
  - **Docker Engine SDK (Python):** Conexión con el socket `/var/run/docker.sock` para control de contenedores.
  - **Mecanismo de Seguridad Step-Up TOTP (RFC 6238):** Doble factor de autenticación para operaciones de alto riesgo.
  - **DevPilot Orchestrator (`devpilot_core/docker_manager.py`):** Módulo de control operacional.
  - **Bitácora Forense SQLite:** Tabla `remediation_logs` para trazabilidad de incidentes.
* **Cómo se configuró:**
  - `devpilot_core/docker_manager.py` implementa:
    1. `restart_service_container()`: Reinicio controlado de contenedores caídos.
    2. `discover_candidate_services()`: Auto-descubrimiento en caliente de nuevos microservicios conectados a la red Docker.
  - `devpilot_core/auth.py` exige un código TOTP de 6 dígitos antes de aprobar cualquier acción de remediación que afecte la disponibilidad.
* **🎙️ Qué decirle al profesor:**
  > *"En la etapa de OPERATE demostramos gestión de incidentes y mantenimiento seguro. Nuestra plataforma se comunica directamente con la API de Docker Engine. Para evitar errores humanos o ataques, cualquier remediación operativa (como reiniciar un servicio caído) exige autenticación de doble factor TOTP bajo estándar RFC 6238 y queda asentada en la bitácora forense de auditoría."*
* **💻 Demostración en vivo paso a paso:**
  1. Abre el navegador en `http://localhost:8000` (Usuario: `admin` / Clave: `AdminPass2026*`).
  2. Ve a la pestaña **Incidentes y Remediación**.
  3. Selecciona un incidente o servicio para reiniciar.
  4. En el modal de confirmación, ingresa la semilla/código TOTP demo: **`JBSWY3DPEHPK3PXP`** (o genera el código de 6 dígitos).
  5. Muestra cómo el servicio se reinicia y se genera el registro inmutable en la tabla de **Bitácora de Auditoría**.

---

## 5. Etapa de MONITOR (Monitoreo y Observabilidad)

* **Objetivo de la etapa:** Recolectar telemetría en tiempo real, calcular SLAs, detectar anomalías e inyectar ingeniería del caos para validar la resiliencia del sistema.
* **Herramientas utilizadas:**
  - **DevPilot Observability Engine (`devpilot_core/monitor.py`):** Motor de monitoreo asíncrono.
  - **SPA Dashboard con Chart.js:** Visualización reactiva en tiempo real bajo patrón MVVM.
  - **Chaos Studio:** Herramienta integrada de inyección de caos y latencia controlada.
* **Cómo se configuró:**
  - Sondeo asíncrono no invasivo cada **5 segundos** a los endpoints `/health` de todos los microservicios.
  - Cálculo en tiempo real de:
    - **Latencia RTT (Round Trip Time):** Medida en milisegundos con historial gráfico en Chart.js.
    - **Tasa de error HTTP 5xx:** Porcentaje de fallos por ventana de tiempo.
    - **Cumplimiento de SLA:** Porcentaje de disponibilidad (objetivo 99.9%).
  - Detección automática de incidentes: si un servicio responde > 1000 ms o devuelve error, se genera una alerta inmediata.
  - Endpoints de fallo en cada microservicio (`/fault/delay`, `/fault/crash`) para pruebas de resiliencia.
* **🎙️ Qué decirle al profesor:**
  > *"En la etapa de MONITOR implementamos observabilidad proactiva. Un motor en segundo plano sondea los microservicios cada 5 segundos midiendo latencia RTT y cumplimiento de SLA en tiempo real. Además, contamos con un 'Chaos Studio' que permite inyectar fallos controlados para demostrar en vivo cómo el sistema detecta la degradación en segundos."*
* **💻 Demostración en vivo paso a paso:**
  1. En el Dashboard `http://localhost:8000`, muestra las tarjetas de servicios con métricas y gráficas en verde.
  2. Dirígete a la sección **Chaos Studio**.
  3. Selecciona el servicio `orders` e inyecta una latencia de `2500 ms`.
  4. Observa y muestra al profesor cómo en el siguiente ciclo (5 segundos) la tarjeta se torna ámbar/roja, se grafica el pico de latencia y se registra un incidente automático.

---

# 4. PARTE 3: Banco de Preguntas Trampa del Docente y Respuestas

### ❓ Pregunta 1: *"¿Por qué en la etapa de Build no usaron Docker para compilar?"*
* **Respuesta Correcta:**  
  *"Porque Docker es una herramienta de empaquetado y aislamiento para las etapas de **Release** y **Deploy**. Incluir Docker en el Build genera lentitud innecesaria y oculta errores del lenguaje. El Build debe ser rápido y liviano (Fail-Fast), por lo que usamos compiladores sintácticos directos (`py_compile` y `node --check`) que validan la gramática en milisegundos antes de gastar recursos empaquetando."*

### ❓ Pregunta 2: *"¿Qué es un AST y por qué es una herramienta de Build?"*
* **Respuesta Correcta:**  
  *"AST significa **Abstract Syntax Tree** (Árbol de Sintaxis Abstracta). Es la representación en memoria que hace el compilador del código fuente para validar su estructura gramatical. `py_compile` y el parser V8 de Node son herramientas de build porque convierten el código en ese árbol y luego a bytecode; si hay un solo error léxico o sintáctico, la compilación falla antes de que el código llegue a ejecutarse."*

### ❓ Pregunta 3: *"¿Cómo se comunican los microservicios si se ejecutan como software puro sin Docker?"*
* **Respuesta Correcta:**  
  *"Se comunican por loopback en `127.0.0.1` usando puertos diferenciados (Core: 8000, Users: 3001, Products: 3002, Orders: 3003, Payments: 3004). En nuestro código implementamos la función `normalize_service_url()` en `database.py`, la cual detecta si estamos corriendo nativos o en Docker y traduce los nombres de host automáticamente."*

### ❓ Pregunta 4: *"¿Qué diferencia hay entre la etapa de Test y el Quality Gate del Build?"*
* **Respuesta Correcta:**  
  *"La etapa de Test ejecuta la lógica interna y las aserciones funcionales (Pytest, Node:Test). El Quality Gate del Build es el árbitro que evalúa todo el conjunto: linting sintáctico, manifiestos, higiene de dependencias y los resultados de los tests. Si el Quality Gate no da código 0, la entrega se rechaza completamente."*

---

# 5. PARTE 4: Cheat Sheet de Comandos Rápidos de Emergencia

Todos estos comandos están probados y listos para ejecutarse en **PowerShell** en Windows:

| Objetivo | Comando |
| :--- | :--- |
| **Ejecutar Quality Gate Oficial de Build (37 checks)** | `.\verify-build.ps1` |
| **Probar Validador de Orders (Python)** | `cd microservices\orders ; py validator.py ; cd ..\..` |
| **Arrancar Microservicio Orders (Software Puro, Puerto 3003)** | `cd microservices\orders ; py main.py` |
| **Probar Validador de Users (Node.js)** | `cd microservices\users ; node validator.js ; cd ..\..` |
| **Arrancar Microservicio Users (Software Puro, Puerto 3001)** | `cd microservices\users ; node server.js` |
| **Levantar TODOS los microservicios en Software Puro (Local)** | `.\start-local.ps1` |
| **Apagar TODOS los microservicios en Software Puro** | `.\stop-local.ps1` |
| **Ejecutar Pruebas Pytest (Etapa TEST)** | `py -m pytest tests/ -v` |
| **Ejecutar Pruebas Node:Test (Etapa TEST)** | `cd microservices\users ; npm test ; cd ..\..` |
| **Compilar imágenes de contenedores (Etapa RELEASE)** | `docker compose build` |
| **Desplegar arquitectura completa en Docker (Etapa DEPLOY)** | `docker compose up -d` |
| **Ver estado y healthchecks de contenedores** | `docker compose ps` |
| **Detener contenedores Docker** | `docker compose down` |
| **URL del Dashboard Principal** | [http://localhost:8000](http://localhost:8000) (Admin / `AdminPass2026*`) |
| **Semilla TOTP Demo para Acciones Operativas** | `JBSWY3DPEHPK3PXP` |

---
*Fin del Compendio Oficial de Sustentación — DevPilot SRE Platform.*
