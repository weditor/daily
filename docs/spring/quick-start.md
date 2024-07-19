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

## todo

1. 基本原理
2. 注入方式
3. 配置方式(ConfigurationProperties)
4. config 组织, @Bean
5. 接口定义
6. 规范第三方接口 thirdapi
7. Entity 隔离
