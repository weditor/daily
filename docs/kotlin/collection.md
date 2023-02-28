# 集合操作

对于初步从 java 转 kotlin 的人来说。感受最深的地方，绝对包含了 kotlin 丰富的集合操作。

再也不用 new 一个集合挨个塞元素了。kotlin 可以:

```kotlin
val texts = listOf("aa", "bb")
val texts = setOf("aa", "bb")
val texts = mapOf("aa" to 1, "bb" to 2)
```

再也不用费劲地取最后一个元素了: `someList.length() > 0?someList[someList.length()-1]:null`, kotlin 可以:

```kotlin
someList.lastOrNull()
someList.firstOrNull()
```

也终于不用什么 CollectionUtils, Arrays, StringUtils 了. 我们可以使用 **真·**面向对象 的方式写:

```kotlin
if (text.isEmpty())
if (text.isNullOrEmpty())
if (textA == textB)
if (listA == listB)
val setA = listA.toSet()
```

也不用担心自己创建的集合传入第三方函数后，数据被哪个老六改掉了，因为 kotlin 集合默认是不可变的:

```kotlin
val listA = listOf(1, 2, 3)
listA.add(33) // ERROR!!

val listB = mutableListOf(1, 2, 3)
listB.add(33) // OK
```

连 stream 的体验都上升了一个档次:

```kotlin
texts
    .filter {...}
    .map {...}
    .mapNotNull {...}
    .findLastNot {...}
val userMap: Map<Int, User> = users.associateBy { u -> u.getId() }
```

也许你能想出对集合的 20 中操作方法，但是 kotlin 能给你自带 100 个，编码提速必备。

探索一下编辑器提示的方法，以及官方文档，这一切你值得拥有:

1. [从 java 到 kotlin 之 string](https://kotlinlang.org/docs/java-to-kotlin-idioms-strings.html)
2. [从 java 到 kotlin 之 collections](https://kotlinlang.org/docs/java-to-kotlin-collections-guide.html)
3. [从 java 到 kotlin 之 nullability](https://kotlinlang.org/docs/java-to-kotlin-nullability-guide.html)
4. [kotlin collections api 参考](https://kotlinlang.org/docs/collections-overview.html#)

祝早日适应 kotlin 风格, 脱离苦海。
