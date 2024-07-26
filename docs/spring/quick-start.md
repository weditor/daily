# Spring

## Bean 的声明

基于代码的 Bean 的声明主要有两种方式: `@Component` 注解以及 `Configuration`。

:::{note}
Spring 还支持 xml 方式配置 Bean, 不过目前主流偏向于使用注解式声明，所以不做介绍。
:::

### 基于 Component

```kotlin
@Component
class UserService {
    // ...
}
```

除了 `@Component` 注解外，还有其不同意语义的注解: `@Controller`, `@Service`, `@Repository`。
排除可读性的差异，从技术角度讲，它们功能都一样。

### 基于 Configuration

```kotlin
class UserService { /* ... */}

@Configuration
class AppConfiguration {
    @Bean
    fun userService(): UserService {
        return UserService()
    }
}
```

这种方式声明的 Bean 与 `@Component` Bean 并没有什么不同。

通常对于不方便修改代码的 class, 会使用这种方式创建为 Bean。
假设 `UserService` 是一个第三方库的代码，我们没法修改其代码添加 `@Component` 注解，
就可以使用 `@Configuration/@Bean` 注解创建 Bean。

## Bean 的注入

Bean 的声明与注入涉及到注解: `@Autowired`, 三种注入方式: _构造函数注入_，_setter 函数注入_，_属性注入_

:::{note}
Spring 对 Resource(JSR-250) 与 Inject(JSR-330) 也提供了兼容支持。
出于规范原因，不推荐使用。

尤其是 Resource 注解，按照 id 没有找到 Bean 的情况下，会回退为 `@Autowired` 一样的行为方式，
这种歧义可能会带来一些隐患。

当然，对于编写个人库，可以考虑使用 Inject/Resource，以便适配市面上大部分依赖注入框架。
:::

### 构造函数注入

这是推荐的方式。使用这种方式可以保证对象初始化后立即可用, 并且支持将字段声明为 final。

这种方式，只需要正常声明构造函数即可, 下面的例子，将 `UserRepository` 注入到 `UserService`:

```java
@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    // ...
}
```

### setter 函数注入

通过 setter 函数注入, 下面的代码与之前的 **构造函数注入** 代码等价:

```java
@Service
public class UserService {
    private UserRepository userRepository;

    public UserService() {}

    @Autowired
    public setUserRepository(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    // ...
}
```

这种方式 **几乎** 与 **构造函数注入** 等价，会在对象创建之后，立即执行 setter 函数。

不过对象创建和执行 setter 函数之间有一小段空窗期。
一般来说这段空窗期是不会插入其他代码的，但是在发生循环依赖时，会插入其他代码,
假设 A/B 两个 class 互相依赖:

```java
class A {
    @Autowired
    public setB(B b) {...}
}
class B {
    @Autowired
    public setA(A a) {...}
}
```

它们的初始化流程就会变化为:

```{mermaid}
graph LR;
    A.constructor --> B.constructor --> A.setter --> B.setter
```

注意，执行 `A.setter(B)` 时，B 的 setter 还没执行，处于为就绪状态，但并不是不能用，所以还是将他 set 给 A 了。
如果在 A::setB 里面看到的 B 其实是一个未就绪的对象，强行使用可能有风险。

因此，基于 setter 的注入也是一种绕过循环依赖的方法。不过，最佳做法还是从源头解决，修改不合理的代码结构，避免循环依赖。

因此一般情况下，还是推荐构造函数注入。

### 属性注入

**极不推荐** 的方式.

这种方式需要对属性施加 `@Autowired` 注解。

```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;

    public UserService() {}
}
```

这种注入方式会带来一个恶劣的影响: `UserService` 无法通过常规手段 new 出来，因为无法设置 `userRepository` 属性。
这对于单元测试很不利。

## 项目配置

定义配置

```kotlin
// ApplicationProperty.kt
@ConfigurationProperties("my.app")
class ApplicationProperty {
    var port: Int = 0
    var connectionPoolSize: Int = 200
    var log: LogProperty = LogProperty()

    class LogProperty {
        var path: String = ""
        var level: String = "WARNING"
    }
}
```

启用配置

```kotlin
@SpringBootApplication
@EnableConfigurationProperties(ApplicationProperty::class.java)
class MyApplication
```

配置文件:

```yaml
# application.yml
my:
  app:
    port: 8080
    connection-pool-size: 100
    log:
      path: /logs/user
      level: INFO
```

要在其它 Component 中使用配置，只需要作为普通 Component 注入即可

```kotlin
@Component
class SomeComponent(private val appProperty: ApplicationProperty) {
    /** ... ... */
}
```

也可以使用 SpEL 注入部分配置:

```kotlin
@Component
class SomeComponent(@Value("#{applicationProperty.port}") private val port: Int) {
    /** ... ... */
}
```

不好的做法 - 直接使用 `@Value` 引用未定义配置, 例如:

```yaml
executor:
  thread-num: 8
```

```kotlin
@Component
class TextSplitter(@Value("\${executor.thread-num}") private val threadNum: Int) {

}
```

## 目录组织

```text
com.example.auth/
├─ config/
├─ repository/
├─ service/
├─ controller/
└─ AuthApplication.kt
```

如上所示

- 启动入口必须位于顶层目录，且名称以 `Application` 结尾
- config 及其子目录存放所有 `@Configuration` `@ConfigurationProperties` 类, 以及其专用类。
  
  例如有一个类 `ApiMetricFilter`，在 `@Configuration` 中实例化为 `@Bean`, 除此之外不被任何其他地方引用，则这个类可以放在 config 目录下。

- repository 目录存放所有数据库操作。这些代码返回原本的数据库数据，不对数据进行任何操作
- service 目录会依赖 repository, 对数据进行处理，完成业务功能
- controller 目录用于实现对外接口

## Http 接口定义

接口必须保证唯一，明确，无歧义。

### method, url

接口应当具有唯一的 method 与 url, 并且 url 名称只能包含小写/下划线

好的案例:

```kotlin
@GetMapping("/api/vip_users")
fun getVipUsers(): IWebResult<List<User>> { 
    /** ... */
}
```

不好的案例

```kotlin
// method 不唯一
@RequestMapping("/api/vip_users", method = [RequestMethod.GET, RequestMethod.POST])
fun getVipUsers(): IWebResult<List<User>>

// url 不唯一
@GetMapping(values = ["/api/vip_users", "/api/vip_user_list"])
fun getVipUsers(): IWebResult<List<User>>

// url 命名不规范
@GetMapping("/api/vip-users")
fun getVipUsers(): IWebResult<List<User>>
```

### 参数

明确定义参数，参数的位置没有歧义, 使用蛇形命名。即

1. 不允许使用 Map/Object 等非结构化 class 接受参数
2. 不允许同时从多个地方接受同一个参数。例如允许用户将 userId 参数放在 body 和 query params 里面
3. path/query param/body 等参数均使用蛇形命名。(headers 除外)

好的案例

```kotlin
// 案例1: 接收 query params 参数
@GetMapping("/api/books")
fun getBooks(
    @RequestParam("name__icontains", required = true) nameIContains: String,
    @RequestParam author: String,
    @RequestParam(defaultValue = "10") limit: Int,
    @RequestParam(defaultValue = "0") offset: Long,
): IWebResult<List<Book>> {
    /** ... */
}

// 案例2: 接收 path/body 参数
@PostMapping("/api/books/{id}/buy")
fun buyBook(
    @PathVariable(required = true) id: String,
    @RequestBody buyBookVo: BuyBookVo,
): IWebResult<Book> {
    /** ... */
}

// 案例3: 接收 header/cookie 参数
@GetMapping("/api/profile")
fun getUserProfile(
    @RequestHeader("X-Trace-Id") traceId: String,
    @CookieValue("auth") auth: String,
): IWebResult<User> {
    /** ... */
}
```

不好的案例

```kotlin
// 参数命名不规范
@GetMapping("/api/books")
fun getBooks(
    @RequestParam("nameIContains", required = true) nameIContains: String,
): IWebResult<List<Book>> {
    /** ... */
}

// 没有明确定义参数，并且使用了非结构化数据作为参数
@GetMapping("/api/books")
fun getBooks(@RequestParam params: Map<String, String>): IWebResult<List<Book>> {
    val author = params.get("author")
    /** ... */
}

// 没有明确定义参数，并且使用了非结构化数据作为参数
@PostMapping("/api/books/{id}/buy")
fun getBooks(@RequestBody body: Map<String, String>): IWebResult<List<Book>> {
    /** ... */
}

// 没有明确定义参数，使用了裸奔的 ServerHttpRequest 获取参数
@GetMapping("/api/books")
fun getBooks(serverHttpRequest: ServerHttpRequest): IWebResult<List<Book>> {
    val body = serverHttpRequest.getBody()
    val headers = serverHttpRequest.getHeaders()
    /** ... */
}

// 允许多出同时传递 auth 参数，存在歧义
@GetMapping("/api/profile")
fun profile(
    @CookieValue("auth") headerAuth: String?, 
    @RequestParam paramAuthor: String?,
): IWebResult<List<Book>> {
    var auth = headerAuth
    if (auth.isNullOrEmpty()) {
        auth = paramAuthor
    }
    /** ... */
}
```

## 封装 IO 操作

提供一个交互中间层, 放在 thirdapi 目录，将程序所有与外界隔离。

这个中间层对 IO 操作封装后，需要保证在其他模块眼里，就是一个普通方法

```kotlin
// thirdapi/NerApi.kt
interface NerApi {
    fun textToWords(text: String): List<Word>
}

// TextAnalyzeService.kt
class TextAnalyzeService(
    private val nerApi: NerApi,
) {
    fun analyze(text: String) {
        /**
         * 对于 TextAnalyzeService 来说，它只知道 textToWords 输入一个字符串，返回分词结果。
         * 至于内部是规则实现，还是远程调用，是不需要感知的。
         */
        val words = nerApi.textToWords(text)
    }
}

```

有了这个隔离层，便于实现单元测试，例如在测试期间可以提供一个假的 `NerApi` 辅助单元测试:

```kotlin
class FakeNerApi: NerApi {
    override fun textToWords(text: String): List<Word> {
        if (text == "江南皮革厂倒闭了") {
            return Words.of("江南", "皮革厂", "倒闭", "了")
        }
        throw NotImplementedError("我就是个假的分词，别对我要求太高")
    }
}
```
