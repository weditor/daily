# 内联(inline)函数

内联函数是在普通函数基础上加上 `inline` 关键字，使得它们在编译期间会在被调用处原地展开，因此并不会发生函数调用。

由于省略了一次函数调用，最直接的受益就是(少许)性能提升。

下面这段代码定义了一个 inline 函数, 并且在 main 中调用它。可以看到用法与普通函数一样

```kotlin
inline fun add(a: Int, b: Int) {
    return a + b
}

fun main() {
    val first = 1
    val second = 3
    val third = add(first, second)
}
```

编译后上面的 add 会被调用者原地展开, 因此会变成类似下面这样:

```kotlin
fun main() {
    val first = 1
    val second = 3
    val third = first + second
}
```

## 使用场景

第一个小场景是把一些大量使用的函数使用 inline 实现，可以稍微提升性能，
例如对集合操作: `numbers.map { it * 2 }`;
这些 map、filter 等操作在 kotlin 里面就是用 inline 函数实现，
下面是伪代码

```kotlin
class ArrayList<T> {
    ...
    public inline fun map(transform: (T) -> R): List<R> {
        val target = mutableListOf<R>()
        for (item in this) {
            target.add(transform(item))
        }
        return target
    }
}
```

因此我们每次对集合使用 filter/map 等操作的时候，调用都会在原地展开为 for 循环(transform 函数本身也有办法能展开)。

如果只是节省一次函数调用，难道我们就差这一次函数调用的性能吗？
那自然也不是的，导致这个功能初看似乎很鸡肋, 甚至官方也不鼓励通过 inline 提升性能。

终于进入正题了，下面介绍第二个使用场景: `inline` 函数引申出来的神奇用法: **规避泛型擦除!**

例如，下面是 mongoTemplate 数据库的查询接口的 java 代码:

```java
public <T> T findOne(Query query, Class<T> entityClass) {
    ...
}
```

为什么这个接口不能少一个参数，写成:

```java
public <T> T findOne(Query query) {
    Class<T> entityClass = T.class;
    ...
}
```

还不是因为万恶的泛型擦除!

但是这个功能在 kotlin 里面可以使用 inline 实现了! 只需要顺带声明泛型的时候加上 reified 关键字。

```kotlin
public inline <reified T> findOne(Query query): T {
    Class<T> entityClass = T.class;
    ...
}

// 使用 findOne
void main() {
    val user = findOne<User>(query);
}
```

kotlin 基于 jvm, 也存在泛型擦除问题，但是 `findOne` 压根不是一个函数，它会在调用的地方展开，
所以能在编译期看到上下文里面的那个泛型! 上面那段代码会在 main 里面展开成类似这样的伪代码:

```kotlin
void main() {
    val user = {
        Class<T> entityClass = User.class;
        ...
    }
}
```

kotlin 可以与 java 无缝调用，但是仍然有很多开源 java 库(例如 spring, jackson)主动适配 kotlin,
一个主要适配点，就是通过 inline 这个特性，规避泛型擦除，提升接口易用性。

## 注意点

class 中的 inline 函数需要关注权限问题。例如 public inline 函数不能访问 private 成员和方法, 会导致无法展开。

例如，下面的 isTeenager 函数访问了私有的 age:

```kotlin
class User {
    private val age: Int

    public inline fun isTeenager(): Boolean {
        // 访问了 私有成员 age
        return this.age < 18
    }
}
```

导致下面的函数

```kotlin
fun main() {
    val user: User = ...
    val isTeen = user.isTeenager()
}
```

会被展开成下面这样，存在无法访问 _私有变量_ 的问题。

```kotlin
fun main() {
    val user: User = ...
    // 没有权限访问 age.
    val isTeen = user.age < 18
}
```
