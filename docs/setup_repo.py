import subprocess
import urllib.request
import json
import sys

# 1. Obtener credenciales de Git Credential Manager limpiamente
p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
stdout, _ = p.communicate('protocol=https\nhost=github.com\n\n')

creds = {}
for line in stdout.splitlines():
    if '=' in line:
        k, v = line.split('=', 1)
        creds[k.strip()] = v.strip()

token = creds.get('password')
username = creds.get('username', 'FUZE1276')

if not token:
    print("ERROR: No se encontró token en Git Credential Manager.")
    sys.exit(1)

print(f">> Autenticado en Git Credential Manager como: {username}")

# 2. Verificar o crear el repositorio 'devpilot' en GitHub
repo_name = "devpilot"
check_req = urllib.request.Request(f"https://api.github.com/repos/{username}/{repo_name}", headers={
    'Authorization': f'Bearer {token}',
    'User-Agent': 'DevPilot-Automation',
    'Accept': 'application/vnd.github.v3+json'
})

repo_exists = False
try:
    with urllib.request.urlopen(check_req) as resp:
        if resp.status == 200:
            repo_exists = True
            print(f">> El repositorio '{username}/{repo_name}' ya existe en tu cuenta de GitHub.")
except Exception:
    repo_exists = False

if not repo_exists:
    print(f">> Creando repositorio '{username}/{repo_name}' en tu cuenta de GitHub...")
    create_req = urllib.request.Request("https://api.github.com/user/repos", data=json.dumps({
        "name": repo_name,
        "description": "DevPilot SRE Platform - Autonomous Observability, Chaos Testing & Quality Gate Engine",
        "private": False
    }).encode('utf-8'), headers={
        'Authorization': f'Bearer {token}',
        'User-Agent': 'DevPilot-Automation',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    })
    try:
        with urllib.request.urlopen(create_req) as resp:
            data = json.loads(resp.read().decode())
            print(f">> Repositorio creado exitosamente: {data.get('html_url')}")
    except Exception as e:
        print(f"Nota sobre creación de repo vía API: {e}")
        pass

# 3. Inicializar Git localmente y subir el código
print(">> Preparando git local...")
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "branch", "-M", "main"], check=True)
subprocess.run(["git", "add", "."], check=True)

# Commit
res_commit = subprocess.run(["git", "commit", "-m", "feat: DevPilot SRE Platform - Build Quality Gate and Native Microservices"])

# Configurar remote
remote_url = f"https://github.com/{username}/{repo_name}.git"
subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

print(f">> Subiendo código a {remote_url}...")
res_push = subprocess.run(["git", "push", "-u", "origin", "main"])
if res_push.returncode == 0:
    print("\n" + "=" * 70)
    print(f"  ✅ PROYECTO SUBIDO EXITOSAMENTE A TU GITHUB:")
    print(f"  🌐 https://github.com/{username}/{repo_name}")
    print(f"  🚀 Pestaña Actions: https://github.com/{username}/{repo_name}/actions")
    print("=" * 70)
else:
    print(f">> Código de salida de push: {res_push.returncode}")
