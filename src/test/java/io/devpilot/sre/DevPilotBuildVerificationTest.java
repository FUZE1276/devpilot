package io.devpilot.sre;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import java.io.File;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * ==============================================================================
 * DevPilot SRE Platform - JUnit 5 Automated Verification Suite
 * Cumplimiento de la Etapa 4: Ensayo (Pruebas) - Diapositiva 8 (JUnit)
 * ==============================================================================
 */
public class DevPilotBuildVerificationTest {

    @Test
    @DisplayName("JUnit Test 1: Verificar existencia del microservicio Orders (Python)")
    public void testOrdersMicroserviceStructure() {
        File validator = new File("microservices/orders/validator.py");
        File mainPy = new File("microservices/orders/main.py");
        assertTrue(validator.exists(), "El archivo validator.py de Orders debe existir");
        assertTrue(mainPy.exists(), "El archivo main.py de Orders debe existir");
    }

    @Test
    @DisplayName("JUnit Test 2: Verificar existencia del microservicio Users (Node.js)")
    public void testUsersMicroserviceStructure() {
        File validator = new File("microservices/users/validator.js");
        File serverJs = new File("microservices/users/server.js");
        assertTrue(validator.exists(), "El archivo validator.js de Users debe existir");
        assertTrue(serverJs.exists(), "El archivo server.js de Users debe existir");
    }

    @Test
    @DisplayName("JUnit Test 3: Verificar artefactos de Infraestructura y Quality Gate")
    public void testQualityGateAndInfraArtifacts() {
        File qualityGate = new File("verify-build.ps1");
        File dockerCompose = new File("docker-compose.yml");
        File buildGradle = new File("build.gradle");
        File pomXml = new File("pom.xml");

        assertTrue(qualityGate.exists(), "El script verify-build.ps1 debe existir");
        assertTrue(dockerCompose.exists(), "El manifiesto docker-compose.yml debe existir");
        assertTrue(buildGradle.exists(), "El archivo build.gradle debe existir");
        assertTrue(pomXml.exists(), "El archivo pom.xml de Maven debe existir");
    }

    @Test
    @DisplayName("JUnit Test 4: Verificar Entorno JVM y Runtime de Pruebas")
    public void testJavaRuntimeEnvironment() {
        String javaVersion = System.getProperty("java.version");
        assertNotNull(javaVersion, "La version de Java no debe ser nula");
        assertTrue(javaVersion.startsWith("11") || javaVersion.startsWith("17") || javaVersion.startsWith("21"), 
            "Java Runtime debe ser compatible (Java 11+)");
    }
}
