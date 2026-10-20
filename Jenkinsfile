pipeline {
    agent any

    environment {
        DEVPILOT_ENV = 'production'
        VERSION = '1.0.0'
    }

    stages {
        stage('1. Checkout & Workspace Setup') {
            steps {
                echo "Clonando repositorio y preparando espacio de trabajo para DevPilot v${env.VERSION}..."
            }
        }

        stage('2. Build & AST Compilation') {
            parallel {
                stage('Python AST Compilation') {
                    steps {
                        echo "Ejecutando py_compile en devpilot_core y microservicios..."
                        powershell 'Get-ChildItem devpilot_core/*.py, microservices/*/*.py -Recurse | ForEach-Object { py -m py_compile $_.FullName }'
                    }
                }
                stage('Node.js V8 Syntax Check') {
                    steps {
                        echo "Validando sintaxis V8 en microservicios/users..."
                        powershell 'Get-ChildItem microservices/users/*.js -Recurse | ForEach-Object { node --check $_.FullName }'
                    }
                }
            }
        }

        stage('3. Automated Testing (JUnit & Pytest)') {
            parallel {
                stage('JUnit 5 Tests') {
                    steps {
                        echo "Ejecutando suite JUnit 5 con Maven..."
                        powershell 'mvn test -B'
                    }
                }
                stage('Pytest & Contract Tests') {
                    steps {
                        echo "Ejecutando suite Pytest (12 tests)..."
                        powershell 'py -m pytest tests/ -v'
                    }
                }
                stage('Node:Test Unit Tests') {
                    steps {
                        echo "Ejecutando pruebas nativas de Node..."
                        powershell 'cd microservices/users; npm test'
                    }
                }
            }
        }

        stage('4. Quality Gate Verification') {
            steps {
                echo "Ejecutando orquestador oficial verify-build.ps1 (37 comprobaciones)..."
                powershell -ExecutionPolicy Bypass -File ./verify-build.ps1
            }
        }

        stage('5. Release & Artifact Packaging') {
            steps {
                echo "Construyendo artefactos inmutables de Docker para Release..."
                powershell 'docker compose build'
            }
        }
    }

    post {
        success {
            echo "=========================================================================="
            echo ">> PIPELINE DE LANZAMIENTO EXITOSO: DevPilot v${env.VERSION} listo para despliegue!"
            echo "=========================================================================="
        }
        failure {
            echo ">> PIPELINE FALLIDO: El Quality Gate rechazo el release."
        }
    }
}
