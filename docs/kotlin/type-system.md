# 类型系统

类型系统作为编程语言的基础之一，经常被忽略, 随着 typescript 的风靡，类型系统的重要性也逐渐被很多编程人员意识到。

毫无疑问，类型系统方面， kotlin 的类型系统相对于 typescript 也只是个弟弟，但相对于 java 仍然有一些改进。

在介绍 kotlin 类型系统之前，有必要先介绍一下类型系统本身。

## 类型系统的重要性

类型系统在编译期为数据提供保障，决定了数据如何解释。

例如我们有下面的类型:

```kotlin
// 只读数组接口
interface ReadonlyStrArray {
    fun get(idx: Int): String
}
// 读写数组接口
interface ReadWriteStrArray: ReadonlyStrArray {
    fun set(idx: Int, value: String)
}
```

这是两个普通的数组接口，一个是只读，一个是读写。然后我们可以写出这样的函数:

```kotlin
fun getStrArray(): ReadonlyStrArray {
    val arr: ReadWriteStrArray = ...
    return arr
}

val strArr = getStrArray()
strArr.set(...) // ERROR
```

作为编程人员，我们知道 getStrArray 返回的是*可读写*的数组，它底层数据与 ReadWriteStrArray 一模一样。
但是由于类型系统的存在，我们无法调用这个对象的 set 接口!

正是因为类型系统给我们提供了这种约束，划分数据能力边界。

## 关于类型系统

类型是什么? 在编程语言理论中，类型是集合。

以一些常见的类型举例: Boolean, Int, String. 他们的集合形式是:

```kotlin
Boolean = {true, false}
Int = {-2^31, ..., -1, 0, 1, 2, ..., 2^31-1}
String = {"a", "b", ..., "aa", "ab", ...}
```

以集合的角度，任何类型都可以看成是一种集合

那...函数是什么? 当我们写下这样一个函数的时候:

```kotlin
fun numberToString(num: Int) {
    return num.toString()
}
```

从集合的角度考虑，它其实是从一个集合到另一个集合的映射: `Int => String`。

那再看看另一个简单的函数:

```kotlin
fun doubleNumber(num: Int) {
    return number*2
}
```

它的是将一个整数集合映射为另一个偶数集合。
理想情况下，应该存在一种偶数类型: `Even = {0, 2, -2, 4, -4, ...}`.
如此一来，这个函数就可以表达为 `Int => Even`

实际上，对于一个完备的类型系统，这是合理的，因为类型系统本身能够做到图灵完备。
但是图灵完备的类型系统，可能会导致编译期间类型推导陷入死循环，所以才有了众多残缺的类型系统。

这个理论的数学分支是<范畴论>, 后面不再深入介绍。这里重点介绍 kotlin 类型系统相对于 java 的改进。

回到类型本身，接下来要介绍几个奇怪的类型。

## 几个奇怪的类型

**问题 1**: 从集合的角度来讲，Void 如何表达？

答案: `Void = {singleValue}`, void 是一个只拥有一个元素的集合(Boolean 稍微比它强一些，有两个)。

里面的 singleValue 可以是任何唯一值, 这乍一看可能有点反直觉，可能很多人(包括我)会下意识认为 Void 应该对应一个空集合。

**问题 2**: 为什么 Void 不是空集合?

它的解释过程是这样的。
先说一个普通函数函数，例如 `Int => String`, 任何一个 Int 都会映射到一个 String，这个函数本身存在的意义就是让我们得到那个 String;
而对于 Void 函数: `Int => Void`, 因为 Void 集合本身只有一个值，所以即使这个函数不执行，
我们也知道输入的 Int 会映射到的目标值(因为 Void 集合本身只有一个值)。这种返回值的意义不是很大，所以这种函数从范畴论角度看意义也不大，
现实情况中通常这种函数的意义都是通过 **副作用** 体现，例如 `deleteFile(file: String): Void`.

**问题 3**: 既然 Void 并非空集合，那空集合对应了什么类型?

这就对了! 从范畴论的角度看 `Int => ∅` 是无意义的! 因为目标是一个空集合，压根没法映射。

如果我们写出了这样一个函数，意味着这个函数压根没法返回!

等等，真的有这样的函数吗? ... 还真有! 至少有两种情况: 死循环、强行退出!

```kotlin

fun deadLoop(): "∅" {
    while (true) {
        ...
    }
}

fun notImplementFunc(): "∅" {
    throw NotImplementError()
}

fun errorExit(): "∅" {
    exit(1)
}

```

## why

所以这些花里胡哨的东西有什么用呢?

### Unit

在 kotlin 中， `Void` 更名为 `Unit`, 从语义上表达了它是一个单一值的集合。

并且由于 Unit 是按照标准模型实现，这允许我们得到一个全局的 Unit 实例，这在泛型中尤其有用。
例如 Http 返回值, 通常会定义一个泛型结构将数据存储在泛型字段 data 中:

```kotlin
class WebResult<T>(val code: Int, val msg: String, val data: T)
```

但是，如果有一个接口不需要返回任何数据怎么办呢? 我们可以实例化 `WebResult<Unit>(0, "ok", Unit)`,
而在 java 中, 没有办法实例化 Void.

### NoReturn

kotlin 中空集类型为 `NoReturn`, 对应 typescript 的 `never`.

它的应用场景是这样的. 下面这个例子是一个做加减乘除的函数:

```kotlin
fun binCalc(left: Int, right: Int, op: String): Int {
    return when (op) {
        "+" -> left+right
        "-" -> left-right
        "*" -> left*right
        "/" -> left/right
        else -> throw IllegalArgumentError()
    }
}
```

一般来说调用方是绝不会传入非法值，所以上面的 else 分支只是一种保护性措施。

对于这种非法状态，如果我们想将它封装为一个更可读、可复用的函数怎么办呢? 例如:

```kotlin
fun YOU_SHOULD_NOT_BE_HERE(): ??? {
    throw IllegalArgumentError("you should not be here, maybe it's a bug")
}

fun binCalc(left: Int, right: Int, op: String): Int {
    return when (op) {
        ...
        else -> YOU_SHOULD_NOT_BE_HERE()
    }
}
```

会发现，在 java 中压根实现不了这样的函数! 而在 kotlin 中却可以, 这都得益于 NoReturn:

```kotlin
fun YOU_SHOULD_NOT_BE_HERE(): NoReturn {
    throw IllegalArgumentError("you should not be here, maybe it's a bug")
}
```

### 非空

对于 java 中的 `Integer`, 其实它并不是一个纯粹的整数集合，
而是 `Integer = {null} | {0, 1, -1, 2, -2, ...}`, 这就导致类型的不纯粹，要命的是，java 没有办法表达纯粹的 Integer 类型，
这种隐含的不纯粹也导致 java 在函数式编程上举步维艰。

不过，java 有自己的解决方案，通过引入 `@NotNull`，以及 `Optional`.

这两种方案都有各自的问题， `@NotNull` 只是一种标准，并未提供语言级别实现，
而且实现方式也是运行期检查，已经脱离了类型系统和编译期的范畴。

`Optional` 的问题在于它发挥作用需要团队自发的编程约定，而且由于 Optional 本质上是一种全新的类型，
`Optional<Int>` 与 `Int` 之间并不具备直接替换性(不具备父子关系，不适用里氏代换法则)。
又由于泛型擦除, 我们并不知道 `Optional<T>` 中的 T 是什么, 会导致诸如 `T => Optional<T>` 的函数返回多层 Optional 嵌套: `Optonal<Optonal<Int>>`. 虽然用户知道 Optional 无论嵌套多少层都是等价的，
但语言编译检查无法理解。

而 kotlin 提供了纯粹的类型: `Int = {0, 1, -1, 2, -2, ...}`,
如果需要类似 java 的可空类型，可以加上问号: `Int? = {null} | {0, 1, -1, 2, -2, ...}`。
在语言级别支持了非空类型以及 Optional，它们之间具备继承关系。

## 总结

总体上 kotlin 在类型系统上的改进比较有限，不过仍然解决了一些痛点。

如果想体验另一些 _好的类型系统_ 设计，强烈推荐试试 typescript。
