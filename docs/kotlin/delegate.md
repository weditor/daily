# 代理

kotlin 的代理通过 `by` 关键字实现。实际使用时主要有两种用途: 接口代理、属性代理。

## 接口代理

接口代理，这种使用方法来源于装饰器模式。可以使用 kotlin 的代理快速实现装饰器模式。

例如 我们有下面的一个接口及其实现:

```kotlin
interface AbstractUser {
    fun getName(): String
    fun getEmail(): String
}

class SimpleUser(
    private val name: String,
    private val email: String,
): AbstractUser {
    override fun getName() = this.name
    override fun getEmail() = this.email
}
```

下面的代码就实现了一个简单的代理类:

```kotlin
class ObserveOnUser(private val user: AbstractUser): AbstractUser by user {
}
```

注意 `ObserveOnUser` 本身也是 `AbstractUser` 的一个实现。

这个 `ObserveOnUser` 代理类对传进来的 user 做了一层包装，除此之外什么都没有做，
只会简单地把 `getName` `getEmail` 等所有方法调用都转发给 `user` (通过 `by user` 实现的)；效果如下:

```kotlin
val simpleUser = SimpleUser("Tom", "tom@outlook.com")
val delegateUser = ObserveOnUser(simpleUser)
println(delegateUser.getName()) // tom
println(delegateUser.getEmail()) // tom@outlook.com
```

可以理解为 `by` 关键字生成了下面的等价代码:

```kotlin
// class ObserveOnUser(private val user: AbstractUser): AbstractUser by user
class ObserveOnUser(private val user: AbstractUser): AbstractUser {
    override fun getName() = user.name
    override fun getEmail() = user.email
}
```

现在, 我们对它做一些改进，例如希望每次有人访问用户 Email 的时候都打印一条信息，作为提示，就可以这样实现:

```diff
    class ObserveOnUser(private val user: AbstractUser): AbstractUser by user {
+       override fun getEmail(): String {
+           println("warning, someone is visiting my email!")
+           return user.getEmail()
+       }
    }
```

也许有人会有疑惑, 我直接把这个提示写在 `SimpleUser` 里面它不香吗?
这就是代理模式的好处了，它能把业务逻辑(本案例中是观察第三方访问 email)与核心代码分离。

想象一下我们可能不只有保存在内存的 `SimpleUser`, 例如还有保存在文件中的 `FileUser`,
保存到 Redis 的 `RedisUser` 等等很多实现.
利用代理模式，它们全都可以无差别复用这个观察逻辑:

```kotlin
val user: AbstractUser = ObserveOnUser(FileUser(...))
val user: AbstractUser = ObserveOnUser(RedisUser(...))
```

更复杂的情况下，甚至可以实现类装饰器的嵌套:

```kotlin
// 将返回的用户名转换为小写的装饰器
class LowerCaseUser(private val user: AbstractUser): AbstractUser by user {...}
// 将所有访问记录到日志的装饰器
class LoggerUser(private val user: AbstractUser): AbstractUser by user {...}

val user = LoggerChecker(LowerCaseUser(SimpleUser(...)))
println(user.getEmail())
```

以此来实现业务逻辑原子化，降低耦合和实现可插拔。

当然, 代理也不一定只能代理一个接口, 可以实现多个代理, 而且也可以传递一些其他参数:

```kotlin
class ReadWriteDeletage(
    val user: User,
    val group: Group,
    val useGroupPerm: Boolean,
): User by user, Group by group {
    ...
    fun hasPerm(perm: String): Boolean {
        if (user.hasPerm(perm)) {
            return true
        }
        if (useGroupPerm) {
            return group.hasPerm(perm)
        }
        return false
    }
}
```

不过，确实大部分情况下，一个接口也就一个实现，这种情况就没必要强行这样抽象啦，
还是直接把业务逻辑写在 `SimpleUser` 里面吧。 :D

## 属性代理

上面说的 _接口代理_ 是对整个类进行代理，而 _属性代理_ 是对单个成员进行代理。

还是这个例子, 如果我们想要监听属性的 `get`、`set`；使用一般的代码我们可以这么实现:

```kotlin
class User(val innerName: String, val innerEmail: String) {
    fun getName(): String {
        println("someone's getting name")
        return innerName
    }
    fun setName(name: String) {
        println("someone's setting name")
        this.innerName = name
    }
    fun getEmail(): String {
        println("someone's getting email")
        return innerEmail
    }
    fun setEmail(email: String) {
        println("someone's setting email")
        this.innerEmail = name
    }
}
```

可以看到, 对 `name`、`email` 的监听代码其实非常类似，有没有什么办法复用呢？这时候属性代理就派上用场了!

首先我们要实现一个代理类，代理类约定有两个特殊的方法: `getValue`/`setValue`;
这不难解释，因为对于属性一般就两种操作: `get`/`set`, 所以我们需要把这两种操作分别转发到代理类的 `getValue`/`setValue` 上,
这是 kotlin 对于代理类约定的两个特殊方法。

```kotlin
class ObservableString(defaultValue: String="") {
    private var innerValue = defaultValue

    operator fun getValue(thisRef: Any?, property: KProperty<*>): String {
        println("someone's getting $thisRef -> $property")
        return this.innerValue
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        println("someone's getting $thisRef -> $property")
        this.innerValue = value
    }
}
```

> 注: `getValue`/`setValue` 前有 `operator` 关键字, 这是因为它们其实是两个特殊的操作符, 不过这个概念和代理没有关系，有关概念可以搜索 kotlin 操作符重载.

然后就可以像下面一样使用了:

```kotlin
class User() {
    var name: String by ObservableString()
    var email: String by ObservableString()
}

val user = User()
user.name = "Tom" // someone's setting User@282003e1 -> var User.name: kotlin.String
println(user.name) // someone's getting User@282003e1 -> var User.name: kotlin.String
```

> 关于 getValue/setValue 的参数含义，这里通过案例来说明。
> 对 `user.name` 的访问相当于执行了 `ObservableString::getValue(user, user::name)`;
> 设置 `user.name = "Tom"` 相当于执行了 `ObservableString::setValue(user, user::name, "Tom")`。

通过属性代理，可以把对成员的赋值操作转移到代理类的 `setValue` 函数上，取值操作转移到代理类的 `getValue` 上。
因此操作空间非常大!

最粗浅的理解就是，属性代理可以看成是一组可复用的 `get`/`set`.

### 案例 1: 通用字段校验

这个案例我们实现一个数字校验器，可以限制其最大值、最小值。

```kotlin
class BoundedInt(val min, val max) {
    private var innerValue = 0

    operator fun getValue(thisRef: Any?, property: KProperty<*>): Int {
        return this.innerValue
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: Int) {
        if (value < min || value > max) {
            throw IllegalArgumentException("value must between [$min, $max]")
        }
        this.innerValue = value
    }
}
```

使用如下:

```kotlin

class User() {
    // 年龄必须介于 0~120 岁
    var age: Int by BoundedInt(0, 120)
}

user.age = 10   // OK
user.age = 100  // OK
user.age = 1000 // IllegalArgumentException!!! value must between [0, 120]
```

大家有兴趣的话，可以私下尝试实现一个邮箱校验器

### 案例 2: Redis ORM

```kotlin
// ORM 表的基类, 子类必须含有一个 jedis 客户端对象
interface RedisTable {
    val jedis: Jedis
}

// String 属性代理
// 每次 get 都实时从 redis 读取，每次 set 都实时写入 redis
class RedisString() {
    operator fun getValue(thisRef: RedisTable, property: KProperty<*>): String {
        val redisKey = property.name
        return thisRef.jedis.get(redisKey)
    }

    operator fun setValue(thisRef: RedisTable, property: KProperty<*>, value: String) {
        val redisKey = property.name
        thisRef.jedis.set(redisKey, value)
    }
}

// 一个案例 ORM 结构
class MyTable(override val jedis: Jedis): RedisTable {
    val username: String by RedisString()
    val email: String by RedisString()
}

val table = MyTable(jedis)
table.email = "tom@outlook.com"
println(table.email) // tom@outlook.com
```

### 案例 3: Borg

Borg 是星际迷航中的一个集体意识种族，所有个体(名为 Drone)共享意识。

我们使用 kotlin 实现一个 Borg, 它能制造出很多个独立的 Drone 个体，但是 Drone 们内部状态一样!

```kotlin
// 一个代理类，这里就不写了，上面实现过
class DelegateString() {....}

class Borg() {
    val delegateName = DelegateString()
    val delegateEmail = DelegateString()

    fun createDrone() = Drone(delegateName, delegateEmail)
}
class Drone(delegateName: DelegateString, delegateEmail: DelegateString) {
    var name: String by delegateName
    var email: String by delegateEmail
}

val borg = Borg()
val drone1 = borg.createDrone()
val drone2 = borg.createDrone()
drone1.name = "Tom"
print(drone2.name) // "Tom"
```

这个案例主要是为了说明，其实 `DelegateString` 对象也只是一个普通对象而已，是可以被作为参数传递的。

至于这个 Borg 有什么应用场景呢？我也不知道，只是觉得好玩而已。
而且共享状态的功能使用普通代码也可以很容易实现，

## 总结

kotlin 的代理是一种很强大的特性，尤其是属性代理，可以用来实现很多 _魔法_ .
