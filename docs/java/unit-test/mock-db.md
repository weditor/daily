# Mock Http/中间件

## Mock Http

```kotlin
// build.gradle.kts
testImplementation("com.squareup.okhttp3:mockwebserver:4.9.3")
```

```java
MockWebServer server = new MockWebServer();
MockResponse response = new MockResponse()
        .addHeader("Content-Type", "application/json; charset=utf-8")
        .setBody("{\"ip\": \"127.0.0.1\"}");
server.enqueue(response);
server.start();
// ... ...
server.shutdown();
```

## Mock Redis

```kotlin
// build.gradle.kts
testImplementation("com.example.aime:aime-mock")
```

```java
var redisServer = RedisServerBuilder().port(6793).build()
redisServer.start()
// ... ...
redisServer.stop()
```

## Mock Mongo

```kotlin
// build.gradle.kts
testImplementation("com.example.aime:aime-mock")
```

```java
var mongodbServer = MongodbServerBuilder().port(27017).build()
mongodbServer.start()
// ... ...
mongodbServer.stop()
```
