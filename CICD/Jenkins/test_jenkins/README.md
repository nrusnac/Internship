# test_jenkins

Demo full-stack app for testing Jenkins pipelines.

| Part | Stack | Build tool |
|------|-------|-----------|
| `backend/` | Java 25, zero-dependency HTTP server, JUnit 6 | Gradle 9.6.1 (wrapper) |
| `frontend/` | React 19, Vite 8, Vitest 4 | Yarn 4.17.0 (pinned in-repo) / npm |
| `Jenkinsfile` | Declarative pipeline: build + test both parts, JUnit reports, archived artifacts | — |

## Backend

```sh
cd backend
./gradlew build      # compile + run JUnit tests + assemble jar
./gradlew run        # serve http://localhost:8081/api/hello (PORT env var overrides)
```

The Gradle wrapper downloads Gradle 9.6.1 automatically; the foojay toolchain
resolver auto-provisions JDK 25 if the machine doesn't have one (a JDK 17+ is
still needed to launch Gradle itself).

Try it: `curl 'http://localhost:8081/api/hello?name=Jenkins'` → `{"message":"Hello, Jenkins!"}`

Note: the backend defaults to port **8081** because Jenkins itself usually
occupies 8080.

## Frontend

```sh
cd frontend
yarn install         # Yarn 4.17.0 is committed in .yarn/releases — any yarn launcher delegates to it
yarn test            # Vitest unit tests
yarn build           # production bundle in dist/
yarn dev             # dev server; fetches the greeting from the backend
```

npm works too (`npm install && npm test && npm run build`) — but stick to one
lockfile; the repo commits `yarn.lock`.