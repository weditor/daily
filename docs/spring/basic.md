# Spring 基本原理

## IOC/DI

Spring 最核心的概念在于依赖注入(DI)以及控制反转(IOC)。

想象一下我们有三个类 A/B/C, 其中 C 依赖 A/B.

```kotlin
// 代码 1
class A()
class B()
class C(val a: A, val b: B)
```

作为集成方，要使用这些代码我们需要手动把所有类实例化出来并维护好他们的依赖关系：

```kotlin
// 代码 2
fun main() {
    val a = A()
    val b = B()
    val c = C(a, b)
}
```

而spring就充当了这个集成方，我们只需要像 _代码 1_ 中声明每个类以及它们的依赖，
剩下的组装交给 spring 就好了。

那 spring 是怎么组装的呢? 可以理解为，spring 内部有一个 Map:

```kotlin
val applicationContext = mapOf(
    "a": A(), 
    "b": B(),
)
```

实例化 C 时，通过反射发现 C 依赖 A/B, 然后就到这个 Map 里面找到 A/B,
并且把C也加入到 Map:

```kotlin
val c = C(applicationContext.get<A>("a"), applicationContext.get<B>("B"))
applicationContext.put("c", c)
```

后续如果有人要依赖C,便也可以从 applicationContext 读取了。
这个流程中 ，a/b/c 三个对象创建后，是不会销毁的，在进程的生命周期中一直存在并被复用，
我们称这种对象为 `Bean`, 而保存这些对象的Map, 称为 `ApplicationContext`, 它是 spring 的基石。

汇总代码:

```kotlin
@Component
class A()

@Component
class B()

@Component
class C(val a: A, val b: B)

fun main() {
    // 内部会自动扫描所有 @Component 注解，识别为 Bean
    val applicationContext = SpringApplication.run()
}
```

## 一些例外

`ApplicationContext` 这套做法，并非没有限制。

例外1: Bean 实际上是一种单例, 如果一个对象不适合作为单例持久存在，
这个对象就不太适合这种场景。不过 spring 也提供了 Scope 来兼容这种情况。

例外2: 由于 AppliationContext 中是以类型作为查找的，即每个Class一般只存在一个实例（单例模式）。
这就导致如果希望实例化多个对象时会造成冲突。针对这种场景，需要使用 spring 提供的 `@Qualifier` 解决冲突问题。

## IOC/DI 的好处

所以，spring 的控制反转给我们带来了什么好处呢?
从上面的代码中可以看到，我们只需要声明每个 class 的依赖，
依赖会自动注入进来，而不用关注是如何初始化的。
回归到代码层面，就是说，我们节省了那个 `main` 函数的代码, 不必维护他们的初始化流程了。

嗯...这么说起来，有一点好处，但不多。

但是，当项目变得越来越复杂时，spring 提供了以这种良好的代码组织方式。

### 场景1, 组件初始化注入

想象一下，我们是一个微服务 client 库的作者, 假设叫 micro-client,
micro-client 要创建一个 okhttpClient 用于通过 http 协议请求其他微服务。
直觉告诉我们，把 okhttpClient 参数写死在库里面是不好的。

所以，第一种方法就是，把 okhttp 的所有配置项暴露出来，也作为 micro-client 的参数。
但是 okhttp 可配置的参数太多，而且每个版本的配置项还不一样，但是如果有了 spring framework,
我们就可以通过依赖注入来轻松解决这个问题：

```kotlin
// code in micro-client

interface OkHttpCustomizer {
    fun customize(okhttpClient: OkHttpClient): OkHttpClient
}

@Bean
fun createOkhttp(okhttpCustomizer: OkHttpCustomizer): OkHttpClient {
    val client = OkHttpClient()
    return okhttpCustomizer.customize(client)
}
```

这段代码里面，我们在创建 OkHttpClient 后，允许通过注入进来的 `OkHttpCustomizer` 对其进行修改。

至于 OkHttpCustomizer 是从哪儿来的? 可能是用户，可能是其他库，我们不必关心。
得益于 spring framework, 我们只需要声明: 我可能需要一个 OkHttpCustomizer, 具体的实现由用户提供。

最终，通过这种 **customizer** 模式, 我们实现了无关业务逻辑的解耦。
在 spring 源码内部，这种模式也被大量使用

### 场景2, 模块化

想象一下我们在写一个 web 后端, 需要依赖数据库。
对于不同的部署，我们需要依赖的数据来源也不一样。

借助于 spring framework, 可以帮助我们很方便的实现 facade 模式:

```text
project/
├─ app/
├─ service/
│   └─ src/
│       └─ com.example.service
│           └─ UserService.kt
├─ dbfacade/
│   └─ src/
│       └─ com.example.db
│           └─ IUserRepository.kt
├─ dbmysql/
│   └─ src/
│       └─ com.example.db
│           └─ UserMySqlRepositoryImpl.kt
└─ dbmongo/
    └─ src/
        └─ com.example.db
            └─ UserMongoRepositoryImpl.kt
```

其中 service 模块依赖 `IUserRepository` 查询用户信息，
但是并不需要依赖具体的 `UserMySqlRepositoryImpl` 或者 `UserMongoRepositoryImpl`。
service 模块只需要知道，外面有人实现了 `IUserRepository` 接口，自己只需要负责使用就好了。

最终，开发者可以在编译期，通过条件编译选项，选择将 `dbmysql` 或者 `dbmongo` 加入到编译。
依赖关系图为:

```{mermaid}
graph TD
    dbfacade --> service
    dbfacade --> dbmysql
    dbfacade --> dbmongo

    service --> app
    dbmysql --> app
    dbmongo --> app
```
