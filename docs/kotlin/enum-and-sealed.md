# when、enum 和 sealed

## when - 加强版 switch

kotlin 将 java 的 `switch` 关键字重命名为 `when`, 并对其做了强化。

`when` 除了支持传统的 `char`/`int` 这类基础类型外，还支持 `string`，`object`，
这在 java12 也引入了。

`when` 的另一个特性是提供了对 `enum` 的支持。例如下面的四则运算 `enum` 与 `when`:

```kotlin
enum class BinOp(val type: String) {
    ADD("+"),
    MINUS("-"),
    MULTIPLY("*"),
    DIVIDE("/"),
}

fun calc(one: Int, two: Int, op: BinOp): Int {
    return when(op) {
        BinOp.ADD -> one + two
        BinOp.MINUS -> one - two
        BinOp.MULTIPLY -> one * two
        BinOp.DIVIDE -> one / two
    }
}
```

kotlin 会检查 `when` 语句中是否包含了 `enum BinOp` 中所有四个操作，如果少了，程序直接编译不通过。
再也不必担心添加枚举值后其他地方没改的情况了。如果不希望这种行为，也可以加上 `else` 分支:

```kotlin
fun calc(one: Int, two: Int, op: BinOp): Int {
    return when(op) {
        BinOp.ADD -> one + two
        BinOp.MINUS -> one - two
        else -> ... // 此处实现对其他 op 的默认操作
    }
}
```

个人更倾向于前一种: 枚举完所有情况。一旦引入 else ， when+enum 的编译检测就没有了。

## sealed class - 加强版 enum

`enum` 是一种特殊的 class, 它们只能实例化出来特定个数的实例。
与 `enum` 类似，`sealed` 也是一种特殊的 class，但是它们只能派生出有限个子类，而不是限制实例个数。

例如，颜色有(且只有)两种表达方案: RGB, HSI; 这很像 enum，但没法用 enum 表达，因为 RGB 还包含可变的 r/g/b 三个属性，
这就是 `sealed class` 发挥作用的时候了。

```kotlin
sealed class Color()

data class RGBColor(val red: Int, val green: Int, val blue: Int): Color()
data class HSIColor(val hue: Int, val saturation: Int, val intensity: Int): Color()
```

`Color` 是 `sealed class`，限定了它 **所有派生的子类必须和 Color 写在同一文件** 。
这个例子中，和 `Color` 只有两个子类 `RGBColor`/`HSIColor`。

**所有派生的子类必须和 Color 写在同一文件**， 这个限定条件隐含的意思就是: `Color` 的所有子类在编译期就已经完全确定了!
这才能保证 `sealed class` 们只能派生出有限个子类。
说到这里已经很明确了，其实 `sealed class` 就是广义的 `enum` 。

由于不限定实例个数，可以实例化出任意个数的 `Color`:

```kotlin
val color = HSIColor(0, 0, 0)

val color = RGBColor(0, 0, 0)
val color = RGBColor(128, 0, 0)
val color = RGBColor(128, 128, 128)
```

`sealed class` 与 `when` 配合:

```kotlin
val color = ...
when (color) {
    is RGBColor -> ...
    is HSIColor -> ...
}
```

`sealed class` + `when` 也能享受到编译期检查的好处。

## 总结

由于 java 风气颇为执迷面向对象， 视 `instanceof` 如死敌.
在 kotlin 里面就不必了。 `when` + `is` 算是一种惯用法。
