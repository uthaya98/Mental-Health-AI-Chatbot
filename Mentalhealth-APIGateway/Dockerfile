FROM eclipse-temurin:17-jdk AS build

WORKDIR /app

COPY pom.xml .

COPY .mvn .mvn

COPY mvnw .

COPY src src

RUN chmod +x mvnw && ./mvnw clean package -DskipTests
FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8083

ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD wget -q0- https://localhost:8080/actuator/health || exit 1

ENTRYPOINT [ "sh", "-c", "java $JAVA_OPTS -jar app.jar"]

