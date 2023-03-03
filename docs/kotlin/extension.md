# 扩展

扩展是 kotlin 的一个很神奇的特性，对于一些不可修改的代码, 例如第三方库的 class，可以通过 **扩展** 无侵入地对其增强。

例如我们希望对内置的 Int 类增加判断是否是偶数的功能:

```kotlin
// 一个简单的代理函数，
// 为 Int 增加判断是否是偶数的能力
fun Int.isEven(): Boolean {
    return this % 2 == 0
}

print(3.isEven()) // false
print(4.isEven()) // true
```

可以看到，代理函数的写法和普通函数差不多，只是需要把被绑定类写在函数名前面，函数体内可以通过 this 访问当前绑定的对象。

它的原理也很简单，只是在编译期做了一些转换，实际上会转换为下面的代码:

```kotlin
fun isEven(this: Int): Boolean {
    return this % 2 == 0
}

print(isEven(3)) // false
print(isEven(4)) // true
```

知道这一点后，对于扩展的限制也就很容易理解了。例如 无法在扩展函数中通过 this 访问 private 成员；
扩展也无法实现多态，因为它是编译期的, 比如下面的代码

```kotlin
interface AbstractUser()
class User(): AbstractUser

// 对父子都定义一个扩展
fun AbstractUser.speak() {
    println("I'm AbstractUser")
}
fun User.speak() {
    println("I'm User")
}

val user = User()
user.speak() // I'm User

val user: AbstractUser = User()
user.speak() // I'm AbstractUser
```

## 为什么需要扩展

扩展表面上只是一种简单的语法糖。

真正使用时却并不是语法糖这么简单，它能够避免我们在不破坏封装的情况下自然地使用 `text.isEmpty()` 面向对象风格,
而不是写出 `StringUtils.isEmpty(text)` 这种违和的风格, 甚至能够实现一些面向对象很难的东西。

我们以 java 的 stream 为例。 stream 是一个泛型: `Stream<T>`, 它包含了一系列通用 filter、map 等操作。

不过难免有一些特化的新需求，比如，

1. 对于 `Stream<Int>`, 希望它能提供 `sum` 方法
2. 而 `Stream<String>` 希望它提供 `join` 为一整个字符串的方法，
3. 对于 `Stream<List<T>>`, 则希望有 `flattern` 可以将二维数组变成一维，

通过 java 很难实现这种需求，它只能变通地绕过这几个问题, 针对 1、2，提供通用地 `reduce`、`collect` 让用户自己填充逻辑，
针对 3， 提供了 `flatMap`, 让用户自己重复写 `.flatMap(items -> items)`.

而使用扩展，可以很容易实现这些逻辑, 从而给用户提供尽量简单的接口:

```kotlin
fun Stream<Int>.sum(): Int {
    return this.reduce(Collectors.summingInt())
}
fun Stream<String>.join(): Int {
    return this.reduce(Collectors.joining())
}
fun Stream<List<T>>.flattern(): Stream<T> {
    return this.flatMap { it }
}
```

对扩展语法又使用经验的人可能或多或少意识到，这个语法糖所发挥出来的能力已经足以影响编程风格了，而且这种影响不容小觑。
这是为什么呢?

第一个原因; 扩展本身是一个全局函数，但是当以全局函数的视角看待它时，
会发现它提供了一种 `域` 的概念，它只能作用域它绑定的那个 class .
编辑器也可以利用这种 `域` 优化代码提示，使他们用起来就和原生成员一样。

第二个原因; 我们真的需要多态吗？java 从一开始就把面向对象和多态绑定了，但是面向对象的大部分场景下是不需要多态的，
想象一下那一大堆 get/set 函数，这些函数需要多态做什么呢？又例如 C++ 中, 只有通过 virtual 关键字声明的函数才具有多态性。

而 kotlin 则通过扩展来实现解绑了多态的 OOP，在实际体验上，kotlin 这种方式也是更好的。

正是由于 `扩展` 其实是一种解绑了多态的 OOP，才能提前到编译期，捕获到泛型类型.

如果将扩展实现为 inline 函数，甚至运行期都不会发生函数调用。 kotlin 自带的大部分集合操作，都是通过扩展实现的。

也正是因为扩展的存在，开源社区大量库在进行 kotlin 适配的时候，
只需要额外提供一个使用扩展实现的 `xxx-kotlin-module` 包，就可以完全享受到 kotlin 语法带来的开发便利，
对原有 java 代码没有影响。

## 总结

扩展本身是一种编译期语法糖，但在实践中却影响深远。
它给全局函数增加了成员的语义，将面向对象与多态分离。
