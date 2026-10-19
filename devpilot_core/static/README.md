# 🏛️ Arquitectura MVVM (Model-View-ViewModel / Controller) de DevPilot

Este directorio contiene la implementación del frontend reactivo Single Page Application (SPA) de **DevPilot**, estructurado formalmente bajo el patrón arquitectónico **MVVM (Modelo - Vista - Controlador / Vista-Modelo)** separado nítidamente por carpetas:

```
devpilot_core/static/
│
├── 📁 models/                  # CAPA MODELO (MODEL)
│   ├── apiClient.js            # Cliente HTTP asíncrono con inyección Bearer JWT e interceptores
│   ├── authModel.js            # Autenticación (Contraseñas, MFA Email-OTP, SSO OIDC, RBAC)
│   ├── telemetryModel.js       # Sondeo de telemetría de clúster, métricas y resolución de anomalías
│   ├── chaosModel.js           # Inyección controlada de caos (latencia, error rate 500, crash)
│   ├── remediationModel.js     # Propuestas de auto-remediación asistida por IA y ejecución TOTP
│   ├── servicesModel.js        # Catálogo, auto-discovery Docker SDK y calibración de SLAs
│   ├── logsModel.js            # Extracción de secuencias de logs en vivo de contenedores
│   ├── chatModel.js            # Diálogos causales con Copiloto SRE IA (Claude / Heurístico)
│   └── model.js                # Consolidación y exportación de window.DevPilot.Model
│
├── 📁 controllers/             # CAPA CONTROLADOR / VISTA-MODELO (CONTROLLER / VIEWMODEL)
│   ├── appController.js        # Estado observable (State Store), propiedades computadas,
│   │                           # despacho de comandos (Command Pattern) y bus de eventos (Observer)
│   └── controller.js           # Alias complementario que expone window.DevPilot.Controller
│
├── 📁 views/                   # CAPA VISTA (VIEW)
│   └── view.js                 # Renderizado declarativo del DOM, enlace bidireccional reactivo,
│                               # gráficos de latencia (Chart.js), modales y Lucide Icons
│
├── 📁 js/                      # PUENTES Y BOOTSTRAP
│   ├── eventBridges.js         # Funciones puente para eventos HTML (onclick, onsubmit, onchange)
│   └── app.js                  # Orquestador del ciclo de vida y arranque en DOMContentLoaded
│
└── 📄 index.html               # Estructura semántica HTML5, Tailwind CSS y carga modular de capas
```

---

## 🎯 Separación de Responsabilidades

| Capa | Carpeta | Responsabilidad Técnica |
| :--- | :--- | :--- |
| **Modelo (Model)** | `models/` | Acceso a datos, llamadas REST a la API de FastAPI, DTOs, manejo del token JWT y almacenamiento en sesión. No tiene conocimiento del DOM ni de la interfaz visual. |
| **Controlador (Controller / ViewModel)** | `controllers/` | Mantiene el estado observable global (`currentUser`, `services`, `incidents`, `proposals`), calcula propiedades derivadas (`avgLatency`, `clusterStatus`, `isChaosAllowed`), despacha comandos asíncronos y notifica eventos a los suscriptores. |
| **Vista (View)** | `views/` | Renderiza el árbol DOM en respuesta a notificaciones del controlador sin recargas de página (*Data Binding* reactivo), inicializa y actualiza las series de tiempo en Chart.js y sincroniza modales. |
| **Punto de Entrada (SPA)** | `index.html` | Estructura HTML pura y modular, vinculando de forma secuencial cada capa del sistema. |
