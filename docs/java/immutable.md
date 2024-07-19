# Immutable 模式

## 可变数据

java 的 final 关键字可以将变量转换为不可变变量。

```java
String name = "one";
name = "two";
```

```java
final String name = "one";
name = "two"; // compile ERROR!!!
```

对象的可变性

```java
public class User {
    private String name;
    private Integer age;

    public User(String name, Integer age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {return name;}
    public void setName(String name) {this.name = name;}

    public Integer getAge() {return age;}
    public void setAge(Integer age) {this.age = age;}
}
```

final 只能维持 "浅" 不可变

```java
final User user = new User("Jerry", 2);
user = new User("Tom", 5);  // compile Error!!!
```

```java
user.name = "Tom"; // compile OK.
```

如何实现 Immutable class

```java
public class ReadOnlyUser {
    // 1. 成员添加 final 修饰
    private final String name;
    private final Integer age;

    public ReadOnlyUser(String name, Integer age) {
        this.name = name;
        this.age = age;
    }

    // 2. 删除 set 方法
    public String getName() {return name;}
    public Integer getAge() {return age;}
}
```


## Why


高并发

```java
void parallelFunc(User user) {
    if (user.age < 18) {
        return;
    }
    System.out.println(user.age); // => 20! 
}
```


可维护性

```java
ReadOnlyUser user = new ReadOnlyUser("Jerry", 2);
// createPermForUser 是一个黑盒, 
// 很难得知其对 User 会做什么变更
createPermForUser(user);
```

vs.

```java
ReadOnlyUser user = new ReadOnlyUser("Jerry", 2);
// createPermForUser 不会对 user 做任何修改，
// 其作用明确体现在返回值 perm
var perm = createPermForUser(user);
```


最小数据依赖

```java
NluResponse nulParse(NluRequest nluRequest) {
    preProcess(nluRequest);
    process(nluRequest);
    postProcess(nluRequest);
    formatLog(nluRequest);
    return collectResult(nluRequest);
}
```

vs.

```java
ReadonlyNluResponse nulParse(ReadonlyNluRequest nluRequest) {
    // preProcess 对 nluRequest 无法做出任何改变，没必要传入不需要的字段。
    // 即使传入了，由于 nluRequest 不可变，也便于后期精简
    var normedQuery = preProcess(nluRequest.getTraceId(), nluRequest.getQuery());
    var parseResult = process(normedQuery);
    var normedParseResult = postProcess(parseResult);
    var nluLog = formatLog(normedParseResult);
    return ReadonlyNluResponse(normedParseResult, nluLog);
}
```


## 哪些地方应具有不可变性

1. 变量定义: `final String name = ...;`
2. class 定义: `final class User {...}`
3. class: 只使用 Getter 方法，禁用 Setter 方法
4. collection: `ImmutableSet.of("red", "orange")`


## 一些惯用法


修改对象 = 销毁 + 创建

```java
User oldUser = new User("Jerry", 2);

// user.age = 3
User newUser = new User(oldUser.name, 3);
```


builder 模式

```java
User user = User.Builder()
    .setName("Jerry")
    .setAge(2)
    .build();
```

```java
User oldUser = new User("Jerry", 2);

User newUser = User.Builder(oldUser)
    .setName(3);
```


集中修改

::: .container {style="font-size: 36px"}
::: left

```java
void funcMain(NluRequest request) {
    funcA(request);
    funcB(request);
    funcC(request);
}
void funcA(NluRequest request) {
    request.a = ...;
    ...
}
void funcB(NluRequest request) {
    request.b = ...;
    ...
}
void funcC(NluRequest request) {
    request.c = ...;
    ...
}
```

:::
::: right

```java
void funcMain(NluRequest request) {
    var normedRequest = normalize(request);
    funcA(normedRequest);
    funcB(normedRequest);
    funcC(normedRequest);
}
NluRequest normalize(NluRequest request) {
    var a = ...;
    var b = ...;
    var c = ...;
    return new NluRequest(a, b, c, ...);
}

void funcA(NluRequest request) { ... }
void funcB(NluRequest request) { ... }
void funcC(NluRequest request) { ... }
```

:::
:::


## Immutable 的边界

::: .container

::: left .fragment

框架规范

```java {fragment}
@Document("user")
class UserTable {
    String id;
    // ...

    public String getId() {return this.id;}
    public void setId(String id) {this.id = id;}
}
```

:::

::: right .fragment

深层修改

```java
user.address.city.code = "310000"
```

:::

:::


### 全面使用 Immutable 数据是可行的


## 谢谢
