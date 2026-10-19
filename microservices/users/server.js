const express = require('express');
const cors = require('cors');
const { validateUserPayload, validateDelayPayload, validateErrorRatePayload } = require('./validator');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Estado de inyección de fallos
const faultState = {
  delayMs: 0,
  errorRate: 0, // 0.0 a 1.0 (ej. 0.3 = 30% de fallos)
  isCrashed: false,
  crashReason: null
};

// Contadores internos de métricas
const internalMetrics = {
  totalRequests: 0,
  successRequests: 0,
  errorRequests: 0,
  startTime: Date.now()
};

// Base de datos simulada de usuarios
const mockUsers = [
  { id: 1, name: "Alice Johnson", email: "alice.johnson@devpilot.io", role: "DevOps Engineer", department: "Infrastructure", status: "active" },
  { id: 2, name: "Bob Martinez", email: "bob.martinez@devpilot.io", role: "Backend Developer", department: "Core Services", status: "active" },
  { id: 3, name: "Carlos Rossi", email: "carlos.rossi@devpilot.io", role: "Site Reliability Engineer", department: "Operations", status: "active" },
  { id: 4, name: "Diana Prince", email: "diana.prince@devpilot.io", role: "Security Architect", department: "SecOps", status: "active" },
  { id: 5, name: "Evan Wright", email: "evan.wright@devpilot.io", role: "Cloud Solutions Architect", department: "Infrastructure", status: "inactive" }
];
let nextUserId = 6;

// Middleware contador de requests
app.use((req, res, next) => {
  internalMetrics.totalRequests++;
  res.on('finish', () => {
    if (res.statusCode >= 200 && res.statusCode < 400) internalMetrics.successRequests++;
    else internalMetrics.errorRequests++;
  });
  next();
});

// Middleware para simular fallos (latencia, crash, error)
async function applyFaultSimulation(req, res, next) {
  // 1. Simulación de servicio caído
  if (faultState.isCrashed) {
    return res.status(503).json({
      error: "Service Unavailable",
      details: faultState.crashReason || "Service has crashed or stopped responding",
      service: "users",
      timestamp: new Date().toISOString()
    });
  }

  // 2. Simulación de retraso / latencia alta
  if (faultState.delayMs > 0) {
    await new Promise(resolve => setTimeout(resolve, faultState.delayMs));
  }

  // 3. Simulación de tasa de errores 500
  if (faultState.errorRate > 0) {
    const random = Math.random();
    if (random < faultState.errorRate) {
      return res.status(500).json({
        error: "Internal Server Error",
        details: "Simulated chaotic error injection in Users Service",
        service: "users",
        errorRateConfigured: faultState.errorRate,
        timestamp: new Date().toISOString()
      });
    }
  }

  next();
}

app.use(applyFaultSimulation);

// ==========================================
// ENDPOINTS DE NEGOCIO Y SALUD
// ==========================================

// Health Check Endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: "UP",
    service: "users",
    version: "1.0.0",
    uptimeSeconds: Math.floor(process.uptime()),
    timestamp: new Date().toISOString(),
    faultStatus: {
      delayMs: faultState.delayMs,
      errorRate: faultState.errorRate,
      isCrashed: faultState.isCrashed
    }
  });
});

// Listar Usuarios (con filtros opcionales)
app.get('/users', (req, res) => {
  const { status, department } = req.query;
  let result = [...mockUsers];
  if (status) result = result.filter(u => u.status === status);
  if (department) result = result.filter(u => u.department.toLowerCase() === department.toLowerCase());
  res.status(200).json({
    success: true,
    count: result.length,
    data: result
  });
});

// Obtener Usuario por ID
app.get('/users/:id', (req, res) => {
  const userId = parseInt(req.params.id, 10);
  const user = mockUsers.find(u => u.id === userId);

  if (!user) {
    return res.status(404).json({
      success: false,
      error: "User not found",
      userId: userId
    });
  }

  res.status(200).json({
    success: true,
    data: user
  });
});

// Crear nuevo usuario con validación estricta de esquema
app.post('/users', (req, res) => {
  const validation = validateUserPayload(req.body);
  if (!validation.valid) {
    return res.status(400).json({ success: false, error: validation.errors.join("; "), validationErrors: validation.errors });
  }
  const { name, email, role, department } = validation.sanitized;
  if (mockUsers.find(u => u.email.toLowerCase() === email.toLowerCase())) {
    return res.status(409).json({ success: false, error: `El email '${email}' ya existe.` });
  }
  const newUser = {
    id: nextUserId++,
    name,
    email,
    role: role || "Developer",
    department: department || "General",
    status: "active",
    createdAt: new Date().toISOString()
  };
  mockUsers.push(newUser);
  console.log(`[Users Service] New user created: ${email}`);
  res.status(201).json({ success: true, message: "Usuario creado exitosamente.", data: newUser });
});

// Eliminar usuario por ID
app.delete('/users/:id', (req, res) => {
  const userId = parseInt(req.params.id, 10);
  const index = mockUsers.findIndex(u => u.id === userId);
  if (index === -1) {
    return res.status(404).json({ success: false, error: "Usuario no encontrado.", userId });
  }
  const deleted = mockUsers.splice(index, 1)[0];
  console.log(`[Users Service] User deleted: ${deleted.email}`);
  res.status(200).json({ success: true, message: `Usuario '${deleted.name}' eliminado.`, data: deleted });
});

// ==========================================
// ENDPOINTS DE INYECCIÓN DE FALLOS (CHAOS)
// ==========================================

// Inyectar Latencia
app.post('/fault/delay', (req, res) => {
  const { delayMs } = req.body;
  const parsedDelay = parseInt(delayMs, 10);

  if (isNaN(parsedDelay) || parsedDelay < 0) {
    return res.status(400).json({ error: "Invalid delayMs value. Must be a non-negative integer." });
  }

  faultState.delayMs = parsedDelay;
  console.log(`[FAULT INJECTED] Users service delay set to ${parsedDelay}ms`);

  res.status(200).json({
    message: `Delay fault configured to ${parsedDelay}ms`,
    faultState
  });
});

// Inyectar Tasa de Error
app.post('/fault/error', (req, res) => {
  const { errorRate } = req.body;
  const parsedRate = parseFloat(errorRate);

  if (isNaN(parsedRate) || parsedRate < 0 || parsedRate > 1) {
    return res.status(400).json({ error: "Invalid errorRate value. Must be between 0.0 and 1.0." });
  }

  faultState.errorRate = parsedRate;
  console.log(`[FAULT INJECTED] Users service error rate set to ${(parsedRate * 100).toFixed(0)}%`);

  res.status(200).json({
    message: `Error rate configured to ${(parsedRate * 100).toFixed(0)}%`,
    faultState
  });
});

// Simular Caída / Crash
app.post('/fault/crash', (req, res) => {
  const { hardKill, reason } = req.body || {};

  console.warn(`[FAULT INJECTED] Users service crash triggered. HardKill: ${!!hardKill}`);

  if (hardKill) {
    res.status(500).json({ message: "Crashing process immediately (hard kill)..." });
    setTimeout(() => {
      process.exit(1);
    }, 200);
    return;
  }

  faultState.isCrashed = true;
  faultState.crashReason = reason || "Simulated unhandled exception / out of memory condition";

  res.status(200).json({
    message: "Service marked as CRASHED (returning 503 on subsequent requests)",
    faultState
  });
});

// Endpoint /simular-fallo para compatibilidad con el documento IEEE 830
app.all('/simular-fallo', (req, res) => {
  const type = req.query.type || (req.body && req.body.type) || 'delay';
  if (type === 'delay') {
    faultState.delayMs = 2500;
  } else if (type === 'error') {
    faultState.errorRate = 0.5;
  } else if (type === 'crash') {
    faultState.isCrashed = true;
    faultState.crashReason = "Fallo simulado vía /simular-fallo";
  } else if (type === 'reset') {
    faultState.delayMs = 0;
    faultState.errorRate = 0;
    faultState.isCrashed = false;
  }
  res.status(200).json({
    message: `Fallo '${type}' configurado correctamente en Users Service`,
    faultState
  });
});

// Resetear Fallos
app.post('/fault/reset', (req, res) => {
  faultState.delayMs = 0;
  faultState.errorRate = 0;
  faultState.isCrashed = false;
  faultState.crashReason = null;

  console.log("[FAULT RESET] Users service returned to normal healthy state");

  res.status(200).json({
    message: "All faults cleared. Users service is healthy.",
    faultState
  });
});

// Estado actual de fallos
app.get('/fault/status', (req, res) => {
  res.status(200).json(faultState);
});

// ==========================================
// ENDPOINT DE MÉTRICAS INTERNAS
// ==========================================

app.get('/metrics', (req, res) => {
  const uptimeSec = Math.floor(process.uptime());
  const departments = [...new Set(mockUsers.map(u => u.department))];
  const activeCount = mockUsers.filter(u => u.status === 'active').length;
  res.status(200).json({
    service: 'users',
    version: '1.0.0',
    uptimeSeconds: uptimeSec,
    uptimeHuman: `${Math.floor(uptimeSec / 3600)}h ${Math.floor((uptimeSec % 3600) / 60)}m ${uptimeSec % 60}s`,
    requests: {
      total: internalMetrics.totalRequests,
      success: internalMetrics.successRequests,
      errors: internalMetrics.errorRequests,
      errorRate: internalMetrics.totalRequests > 0
        ? (internalMetrics.errorRequests / internalMetrics.totalRequests).toFixed(4)
        : "0.0000"
    },
    users: {
      total: mockUsers.length,
      active: activeCount,
      inactive: mockUsers.length - activeCount,
      departments
    },
    faultStatus: faultState,
    timestamp: new Date().toISOString()
  });
});

// Iniciar servidor solo si se ejecuta directamente
if (require.main === module) {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[Users Service] Running on port ${PORT}`);
  });
}

module.exports = app;
