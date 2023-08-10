# jackson 使用文档

## 引入 jackson

在 gradle 中引入 jackson

::::{tab-set}
:::{tab-item} java

```java
implementation("com.fasterxml.jackson.core:jackson-core:2.14.3")
implementation("com.fasterxml.jackson.core:jackson-annotations:2.14.3")
implementation("com.fasterxml.jackson.core:jackson-databind:2.14.3")
```

:::
:::{tab-item} kotlin

```java
implementation("com.fasterxml.jackson.core:jackson-core:2.14.3")
implementation("com.fasterxml.jackson.core:jackson-annotations:2.14.3")
implementation("com.fasterxml.jackson.core:jackson-databind:2.14.3")
implementation("com.fasterxml.jackson.core:jackson-module-kotlin:2.14.3")
```

:::
::::

## jackson 配置

```java
ObjectMapper objectMapper = new ObjectMapper();
// 设置为蛇形命名风格，即 {"user_age": "tom"} => User(userAge="tom")
objectMapper.setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);
// 反序列化时，遇到额外不识别字段，不会导致失败
objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
```

## jackson 的 spring 配置

大部分情况下，spring 默认会生成一个 jackson 的 ObjectMapper Bean.
可以在 _application.properties_ 中通过 `spring.jackson.*` 系列配置完成 jackson 的设置。
例如设置命名风格:

```ini
spring.jackson.propertyNamingStrategy = SNAKE_CASE
```

所有可用配置项见 `org.springframework.boot.autoconfigure.jackson.JacksonProperties`。

## 常用对象转换

```java
// String userText = "{\"name\": \"jack\", \"age\": 10}";
// User user = new User("jack", 10);
ObjectMapper objectMapper = new ObjectMapper();

// 字符串转对象
User user = objectMapper.readValue(userText, User.class);
User user = objectMapper.readValue(userText, new TypeReference<User>() {});

// 字符串转 map
Map<String, Object> map = objectMapper.readValue(userText, new TypeReference<Map<String, Object>>() {});

// map 转对象
User user = objectMapper.convertValue(userMap, User.class);
User user = objectMapper.convertValue(userMap, new TypeReference<Map<String, Object>>() {});

// 对象、map 转字符串
String text = objectMapper.writeValueAsString(user);
```

## 配置字段名称

`@JsonProperty` 针对单个字段配置

```java
public class User {
  // 将 json 中的 "user-name" 字段反序列化为 User::name 字段
  // 而非 "name".
  @JsonProperty("user-name")
  private String name;
}
```

`@JsonNaming` 配置单个类的命名风格

```java
// 设置为蛇形命名，则序列化、反序列化的目标为 {"user_name": ..., "user_age": ...}
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class User {
  private String userName;
  private Integer userAge;
}
```

## 处理 enum

通过 `@JsonValue` 指定序列化、反序列化的目标属性。

```java
// objectMapper.writeValueAsString(Color.RED) => "red"
// objectMapper.readValue("red", Color.class) => Color.RED
public enum Color {
    RED("red"),
    GREEN("green"),
    BLUE("blue");

    @JsonValue
    private final String name;

    Color(String name) {
        this.name = name
    }
}
```

## 处理第三方库的 class

假设第三方库中存在:

```java
public class User {
  private String userName;
  private Integer userAge;
}
```

但是我们要把 `{"secret-name": "jack", "secret-age": 10}` 反序列化为这个对象。
由于无法更改源码，没办法给 User 加上 `@JsonProperty`, 这种情况可以借助 Mixin 实现

```java
public class MixinForUser {
  @JsonProperty("secret-name")
  private String userName;

  @JsonProperty("secret-age")
  private Integer userAge;
}

objectMapper.addMixIn(User.class, MixinForUser.class);
User user = objectMapper.readValue("{\"secret-name\": \"jack\", \"secret-age\": 10}", User.class)
```

## 处理复杂 class 的反序列化

```java
public abstract class Event {
  public final String type;

  protected Event(String type) {
    this.type = type;
  }
}

public class UpdateEvent {
  public final UpdateInfo updateInfo;

  public UpdateEvent(UpdateInfo updateInfo) {
    super("update");
    this.updateInfo = updateInfo;
  }
}

public class DeleteEvent {
  public final DeleteInfo deleteInfo;

  public DeleteEvent(DeleteInfo deleteInfo) {
    super("delete");
    this.deleteInfo = deleteInfo;
  }
}
```

上面一个基类 Event, 派生出两个子类 UpdateEvent/DeleteEvent.
我们的目标是，让下面的代码能自动选择序列化为其中某一个具体的 Event：

```java
Event event = objectMapper.readValue("{\"type\": \"update\", \"updateInfo\": {...}}", Event.class);
// event => UpdateEvent(...)
```

这种情况就需要自定义反序列化逻辑.

第一步实现 `StdDeserializer`

```java
public class EventDeserializer extends StdDeserializer<Event> {

  public EventDeserializer() {
    this(null);
  }

  public EventDeserializer(Class<?> vc) {
    super(vc);
  }

  @Override
  public Item deserialize(JsonParser jp, DeserializationContext ctxt)
    throws IOException, JsonProcessingException {
    JsonNode node = jp.getCodec().readTree(jp);
    String type = node.get("type").asText();
    if ("update".equals(type)) {
      UpdateInfo updateInfo = ctxt.readTreeAsValue(
        node.get("updateInfo"),
        UpdateInfo.class
      );
      return new UpdateEvent(updateInfo);
    } else if ("delete".equals(type)) {
      DeleteInfo deleteInfo = ctxt.readTreeAsValue(
        node.get("deleteInfo"),
        deleteInfo.class
      );
      return new DeleteEvent(deleteInfo);
    }
    throw JsonProcessingException("unknown type: " + type);
  }
}
```

第二步，将自定义反序列化逻辑绑定到类上

```java
@JsonDeserialize(using = EventDeserializer.class)
public class Event {
    ...
}
```
