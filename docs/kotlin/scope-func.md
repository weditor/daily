# scope function

在介绍 scope function 前，我们先介绍一下它尝试解决的问题。 比如下面的代码:

```kotlin
fun requestForData(url, param): List<String> {
    val tmpUrl = if (url.startsWith("/")) {
        hostName + url
    } else {
        hostName + "/" + url
    }
    val result: Mono<Data> = webClient.get(tmpUrl, param)
    if (data.status != 0) {
        throw RequestServerError()
    }
    return data.results.map { it.words }.flatern()
}
```

上面这个函数从远程获取了一些数据然后处理成需要的样子。函数的第一行代码先创建了一个 `tmpUrl`,
但是这个变量只用过一次，之后并没有用到。秉着多一个变量不如少一个的原则，自然会思考怎么节省掉这个变量，提升代码可维护性呢？

现实中函数代码可能非常长，这种一次性使用的变量比比皆是，但是又不能把这些创建变量的逻辑抽象成函数，
因为创建过程可能依赖了很多乱七八糟的其他变量。更不能直接把创建逻辑嵌入到使用的地方，这样更丑了:

```kotlin
    val result: Mono<Data> = webClient.get(
        if (url.startsWith("/")) {
            hostName + url
        } else {
            hostName + "/" + url
        },
        param
    )
```

其实是有一种解决方法的:

```kotlin
fun requestForData(url, param): List<String> {
    val result: Mono<Data>
    {
        val tmpUrl = if (url.startsWith("/")) {
            hostName + url
        } else {
            hostName + "/" + url
        }
        result = webClient.get(tmpUrl, param)
    }

    if (data.status != 0) {
        throw RequestServerError()
    }
    return data.results.map { it.words }.flatern()
}
```

咱们可以使用大括号凭空创造一个作用域，虽然 tmpUrl 仍然存在，但是外面访问不到了，
后期维护看到这个函数就知道它专属于那个 web 请求了。

这在 C/C++ 中是一种惯用法，但是在 java 里面这么写，我怕你会被全组揍一顿。
而如今，kotlin 又把它捡起来了!

kotlin 中 scope function 是一组用于创建小作用域的函数，它们可以在维持原有代码流程的情况下，
将代码划分为很多小作用域，使得代码更加易于维护；正所谓大问题划分为小问题。
比如上面的功能，可以使用 scope function 中的 run 来解决:

```kotlin
fun requestForData(url, param): List<String> {
    val result: Mono<Data> = run {
        val tmpUrl = if (url.startsWith("/")) {
            hostName + url
        } else {
            hostName + "/" + url
        }
        webClient.get(tmpUrl, param)
    }

    if (data.status != 0) {
        throw RequestServerError()
    }
    return data.results.map { it.words }.flatern()
}
```

嗯... 只是在大括号前面加了一个 run 关键字. 这下不用怕被揍了，这是 kotlin 官方鼓励的做法!

## scope function 的原理

所以，上面的 run 关键字是怎么实现的呢?

```kotlin
val result = run { ... }
val result = run({ ... })
```

run 其实是 kotlin 自带的一个普通函数， run 后面的大括号是另一个函数。
run 接受后面的函数作为参数，然后直接执行它.

```kotlin
fun <T> run(f: () -> T) {
    return f()
}
```

就是这么朴实无华...

官方稍微对上面的实现改进了一下，主要是把 run 和 f 都变成了内联函数。

## scope function

上面提到的问题，只是这一类问题的冰山一角，这类问题都是和作用域相关的问题。
所以 kotlin 官方鼓励通过 scope function 给碎片代码增加语义，提升可维护性。

### apply

apply 可以将上游变为 lambda 中的上下文，从而可以通过 this 访问，并原样返回 this，便于做链式处理。

apply 一般用于对象初始化。

```kotlin
val user = User().apply {
    setName("Tom")
    setEmail("tom@outlook.com")
}
```

apply 相当于告诉维护者:

> 虽然这里 new 了一个默认对象, 但是在 apply 里面有初始化，
> 我想你应该并不太想关注这一大堆无聊的 set 代码，现在你可以把 apply 代码折叠起来了，别在这种地方浪费时间。

### with

with 和 apply 很像，但会返回 lambda 的返回值，而且写法也稍微有点不同。

```kotlin
val username = with (user) {
    val firstName = this.firstName ?: ""
    val lastName = this.lastName ?: ""
    "$firstName $lastName"
}
```

with 代码相当于告诉维护者:

> 接下来这段代码是用来处理 user 的，它会频繁获取 user 的成员变量和方法，然后经过一些冗长无聊的处理得到 username。
> 依我看，这段 with 代码从逻辑上可以实现为 User 的成员方法，只不过使用场景及其有限，可能只有我想这么用。
> 所以我也能理解 User 的开发者没有提供这么一个方法，毕竟都是为了可维护性。
>
> 你可以稍微关注里面的逻辑，不想关注也可以折叠这段代码，反正它就是为了构造 username。

### let

let 函数用于将一组操作串联到一起，从语义上体现它们是一组相关操作。

比如下面的代码

```kotlin
val name = user.getName()
val lowName = name.toLowerCase()
println(lowName)
```

可以修改成

```kotlin
user.getName().let {
    it.toLowerCase()
}.let {
    println(it)
}
```

let 函数体中通过 it 访问上游，并返回 lambda 的返回值。
它很像 `map` 函数，只不过它针对的是普通对象，而不是集合。

let 函数相当于告诉维护者:

> 你问我为什么要写这么长的一个 let 链? 我明白把 let 去掉也可以，但是它们是一个整体，要么都看完，要么别看。
> 我只是不太希望后面的开发人员无意间在 语句 1/语句 2 中间插入一些无关的代码破坏这种整体性。

### also

also 和 let 很像，只不过会原样返回上下文。
它经常用于函数返回前做一些顺带的处理。例如下面的代码：

```kotlin
val user = updateUser(...)
kafkaService.pushMessage("user created: $user")
return user
```

这段代码，原本可以直接写成 `return updateUser(...)`, 但为了通知消息队列，不得不新建一个临时变量，
also 就可以解决这种问题:

```kotlin
return updateUser(...).also {
    kafkaService.pushMessage("user created: $it")
}
```

### run

run 函数之前介绍过，就是原地产生一个小作用域, 使其中的局部变量不外泄，以及从语义上表达它们是一个整体:

```kotlin
val result = run {
    val url = host + ":" + port + postUrl
    val param = mapOf(...)
    webClient.get(url, param)
}
```

其实 run 和 apply/with 表达的语义很像，只不过 apply/with 都需要一个对象作为上下文，
而 run 不需要上下文，它就只是为了凭空创造一个作用域。

run 相当于告诉开发者:

> 我知道把 run 里面的东西提出来也一样。里面这段代码只是为了完成一个简单的 X 功能，实现它还是需要那么 4~5 行代码的。
> 这几行代码只有这里会用，跟其他代码无关，所以把他们专门塞到一个子作用域了，祝你 996 愉快!

## takeIf/takeUnless

作为 scope function 的补充，kotlin 额外提供了 takeIf/takeUnless, 用于判断变量符合特定条件下将其转换为 null。

takeIf/takeUnless 的目的不是为了提供子作用域，它是 java 三目运算符的变种。

```kotlin
val rawNum = 3
// 如果 rawNum % 2 == 0, 则返回 rawNum, 否则返回 null.
val evenNum: Int? = rawNum.takeIf { it % 2 == 0}
// takeUnless 是 takeIf 的反义词
val evenNum: Int? = rawNum.takeUnless { it % 2 != 0 }
```

## 总结

kotlin 的 scope function 思想很不错，使用一种比函数更轻量的方法拆分作用域，提升代码可维护性。

只不过官方并没有提供使用场景，需要在实践中慢慢摸索，文中提供了一些我摸索出来的经验，希望能能帮助。
