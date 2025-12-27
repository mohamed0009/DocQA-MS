# Multi-stage build for Eureka Server
# Stage 1: Build the application
FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /app

# Copy pom.xml first for better layer caching
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code and build
COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 eureka && \
    adduser -D -u 1001 -G eureka eureka

# Copy JAR from build stage
COPY --from=build /app/target/eureka-server-1.0.0.jar /app/eureka-server.jar

# Change ownership
RUN chown -R eureka:eureka /app

# Switch to non-root user
USER eureka

# Expose Eureka Server port
EXPOSE 8761

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8761/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "eureka-server.jar"]
