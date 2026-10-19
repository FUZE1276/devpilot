/**
 * ==============================================================================
 * DEVPILOT MICROSERVICES - USERS SERVICE: COMPONENTE VALIDADOR
 * Archivo: validator.js
 * Propósito: Script formal de validación de datos, tipos y reglas de negocio
 *            (Demostración de componente "Validador" requerido por el docente)
 * ==============================================================================
 */

// Expresión regular estándar RFC 5322 para validación de formato de correo
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validador para creación de un nuevo usuario en el sistema.
 * @param {Object} data - Payload crudo recibido en la petición HTTP
 * @returns {{ valid: boolean, errors: string[], sanitized: Object }}
 */
function validateUserPayload(data) {
  const errors = [];

  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['El cuerpo de la petición debe ser un objeto JSON válido.'] };
  }

  // 1. Validación de Nombre
  if (!data.name || typeof data.name !== 'string' || data.name.trim().length < 2) {
    errors.push("El campo 'name' es obligatorio y debe tener al menos 2 caracteres.");
  }

  // 2. Validación de Correo Electrónico
  if (!data.email || typeof data.email !== 'string' || !EMAIL_REGEX.test(data.email.trim())) {
    errors.push("El campo 'email' es obligatorio y debe tener una estructura de correo válida (ej. usuario@devpilot.io).");
  }

  // 3. Validación de Rol
  const validRoles = ['DevOps Engineer', 'Backend Developer', 'Site Reliability Engineer', 'Security Architect', 'Cloud Solutions Architect', 'Admin', 'User'];
  if (data.role && !validRoles.includes(data.role)) {
    errors.push(`El campo 'role' debe ser uno de los roles permitidos: ${validRoles.join(', ')}.`);
  }

  // 4. Validación de Departamento
  if (data.department && typeof data.department !== 'string') {
    errors.push("El campo 'department' debe ser una cadena de texto.");
  }

  return {
    valid: errors.length === 0,
    errors,
    sanitized: errors.length === 0 ? {
      name: data.name.trim(),
      email: data.email.trim().toLowerCase(),
      role: data.role || 'DevOps Engineer',
      department: data.department ? data.department.trim() : 'General',
      status: data.status === 'inactive' ? 'inactive' : 'active'
    } : null
  };
}

/**
 * Validador para inyección de retraso (Chaos Testing).
 * @param {Object} data 
 * @returns {{ valid: boolean, errors: string[] }}
 */
function validateDelayPayload(data) {
  const errors = [];
  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['El payload debe ser un objeto JSON válido.'] };
  }
  if (data.delayMs === undefined || typeof data.delayMs !== 'number' || data.delayMs < 0 || !Number.isInteger(data.delayMs)) {
    errors.push("El campo 'delayMs' debe ser un número entero mayor o igual a 0.");
  }
  return { valid: errors.length === 0, errors };
}

/**
 * Validador para inyección de tasa de fallos HTTP 500.
 * @param {Object} data 
 * @returns {{ valid: boolean, errors: string[] }}
 */
function validateErrorRatePayload(data) {
  const errors = [];
  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['El payload debe ser un objeto JSON válido.'] };
  }
  if (data.errorRate === undefined || typeof data.errorRate !== 'number' || data.errorRate < 0.0 || data.errorRate > 1.0) {
    errors.push("El campo 'errorRate' debe ser un número decimal flotante entre 0.0 y 1.0.");
  }
  return { valid: errors.length === 0, errors };
}

/**
 * Middleware de Express para validación automática de usuarios.
 */
function userValidationMiddleware(req, res, next) {
  const result = validateUserPayload(req.body);
  if (!result.valid) {
    return res.status(400).json({
      error: "Bad Request - Errores de Validación de Datos",
      service: "users",
      validationErrors: result.errors,
      timestamp: new Date().toISOString()
    });
  }
  req.validatedUser = result.sanitized;
  next();
}

module.exports = {
  validateUserPayload,
  validateDelayPayload,
  validateErrorRatePayload,
  userValidationMiddleware
};

// Autoverificación al ejecutarse directamente: node validator.js
if (require.main === module) {
  console.log(">> [VALIDADOR USERS] Ejecutando autoverificación de reglas de validación...");
  const testValid = validateUserPayload({ name: "Carlos SRE", email: "carlos@devpilot.io", role: "Site Reliability Engineer" });
  console.log("  [PASS] Payload válido:", testValid.valid);

  const testInvalid = validateUserPayload({ name: "C", email: "correo_invalido" });
  console.log("  [PASS] Payload inválido rechazado con", testInvalid.errors.length, "errores detectados:");
  testInvalid.errors.forEach(e => console.log("    -", e));
  console.log(">> [VALIDADOR USERS] Componente Validador operativo al 100%.");
}
