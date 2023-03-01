# enum 和 sealed

## when - 加强版 switch

kotlin 将 java 的 switch 关键字重命名为 when, 并对其做了强化。

when 除了支持传统的 char/int 这类基础类型外，还支持 string，object，
这些东西在 java12 也引入了。

when 的另一个特性是它提供了对 enum 的支持。例如下面的四则运算 enum 与 when:

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

kotlin 会检查 when 语句中是否包含了 BinOp 中所有四个操作，如果少了一个，程序直接编译不通过。
再也不必担心添加枚举值后其他地方没改的情况了。如果不希望这种行为，也可以加上 else 分支:

```kotlin
fun calc(one: Int, two: Int, op: BinOp): Int {
    return when(op) {
        BinOp.ADD -> one + two
        BinOp.MINUS -> one - two
        else -> ... // 此处实现对其他 op 的默认操作
    }
}
```

我个人更倾向于前一种，枚举完所有情况。使用 else 后，when+enum 的编译检测就没有了。

## sealed class - 加强版 enum

enum 是一中特殊的 class, 它们只能实例化出来特定个数的实例。
与 enum 不一样，sealed 也是一种特殊的 class，它们只能派生出有限个子类，但是不限制实例个数。

例如，颜色有两种表达方案: RGB, HSI; 就可以使用 sealed 表达，

```kotlin
sealed class Color()

data class RGBColor(val red: Int, val green: Int, val blue: Int): Color()
data class HSIColor(val hue: Int, val saturation: Int, val intensity: Int): Color()
```

Color 是一个 sealed class，限定了它 **所有派生的子类必须和 Color 写在同一文件** 。
这个例子中，和 Color 只有两个子类 RGBColor/HSIColor。

**所有派生的子类必须和 Color 写在同一文件**， 这个限定条件隐含的另外一层意思是: Color 的所有子类在编译期就已经完全确定了!
说到这里已经很明确了，其实 sealed class 是一种更广义的 enum。

由于不限定实例个数，可以实例化出任意个数的 Color:

```kotlin
val color = HSIColor(0, 0, 0)
val color = RGBColor(0, 0, 0)
val color = RGBColor(128, 0, 0)
val color = RGBColor(128, 128, 128)
```

sealed class 与 when 配合:

```kotlin
val color = ...
when (color) {
    is RGBColor -> ...
    is HSIColor -> ...
}
```

sealed class + when 也能享受到编译期检查的好处。
