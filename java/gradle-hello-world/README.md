# Gradle hello world

Project created with `gradle init --type java-application`

Plugin:

- google java formatter
- owasp dependency-check

Tasks

- list tasks `./gradlew tasks`
- list dependencies `./gradlew dependencies`
- list dependencies on runtime `gradle  dependencies   --configuration runtimeClasspath | grep -v "(*)"`
- build uber jar `./gradlew jar`
- run jar `java -jar build/libs/gradle-hello-world.jar`

Todo:

- Add Junit 5 test