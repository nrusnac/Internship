plugins {
    // Auto-provisions the JDK required by the toolchain if the build machine lacks it
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

rootProject.name = "demo-backend"
