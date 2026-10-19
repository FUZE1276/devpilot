/**
 * DevPilot Users Microservice - Pruebas Unitarias y de Integración (Build Stage)
 * Utiliza el ejecutor nativo node:test sin dependencias pesadas.
 */

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert');
const http = require('node:http');
const app = require('../server.js');

describe('Users Service - Test Suite de Build', () => {
  let server;
  let baseUrl;

  before(async () => {
    return new Promise((resolve) => {
      server = http.createServer(app);
      server.listen(0, '127.0.0.1', () => {
        const port = server.address().port;
        baseUrl = `http://127.0.0.1:${port}`;
        resolve();
      });
    });
  });

  after(async () => {
    return new Promise((resolve) => {
      if (server) server.close(resolve);
      else resolve();
    });
  });

  test('GET /health - Debe retornar 200 OK y estructura de telemetría nominal', async () => {
    const res = await fetch(`${baseUrl}/health`);
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.strictEqual(body.status, 'UP');
    assert.strictEqual(body.service, 'users');
    assert.ok(typeof body.uptimeSeconds === 'number');
    assert.ok(body.faultStatus !== undefined);
  });

  test('GET /users - Debe retornar la lista inicial de usuarios simulados', async () => {
    const res = await fetch(`${baseUrl}/users`);
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    assert.ok(Array.isArray(body.data));
    assert.ok(body.data.length >= 5);
    assert.ok(body.data[0].email.includes('@devpilot.io'));
  });

  test('POST /fault/delay - Debe inyectar latencia controlada', async () => {
    const res = await fetch(`${baseUrl}/fault/delay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ delayMs: 150 })
    });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    const state = body.faultState || body.faultStatus;
    assert.strictEqual(state.delayMs, 150);
  });

  test('POST /fault/reset - Debe restaurar los fallos a 0 (estado nominal)', async () => {
    const res = await fetch(`${baseUrl}/fault/reset`, { method: 'POST' });
    assert.strictEqual(res.status, 200);
    const body = await res.json();
    const state = body.faultState || body.faultStatus;
    assert.strictEqual(state.delayMs, 0);
    assert.strictEqual(state.errorRate, 0);
    assert.strictEqual(state.isCrashed, false);
  });

  test('GET /endpoint-inexistente - Debe responder con 404', async () => {
    const res = await fetch(`${baseUrl}/ruta-inexistente-404`);
    assert.strictEqual(res.status, 404);
  });
});
