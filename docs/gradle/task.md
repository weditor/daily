# gradle 的 Project、Tasks

## Task

Project 能够设置的东西比较少，这里直接介绍 Task。

### hello world

一个简单的 task:

```kotlin
// build.gradle.kts
tasks.register("hello") {
    doLast {
        println("Hello world!")
    }
}
```

通过 `gradle -q hello` 来执行这个任务

```shell
~/work/demo$ gradle -q hello
Hello world!
```

注意: `-q` 选项是 `--quite` 的缩写，并不是必需的，只是为了让日志简洁一些。

### doFirst/doLast

task 主要有两个步骤，首先执行 doFirst 代码块，然后执行 doLast 代码块

```kotlin
// build.gradle.kts
tasks.register("hello") {
    doFirst {
        println("Hello world first!")
    }
    doLast {
        println("Hello world last!")
    }
}
```

```shell
~/work/demo$ gradle -q hello
Hello world first!
Hello world last!
```

### task 是代码

`doLast` 中可以包含任意的 kotlin 代码. 例如下面将字符串转换为 大写:

```kotlin
tasks.register("upper") {
    doLast {
        val someString = "mY_nAmE"
        println("Original: $someString")
        println("Upper case: ${someString.toUpperCase()}")
    }
}
```

```shell
> gradle -q upper
Original: mY_nAmE
Upper case: MY_NAME
```

### task 依赖

通过 `dependsOn` 指定任务的依赖。
存在依赖项时，会先执行依赖。

```kotlin
tasks.register("hello") {
    doLast {
        println("Hello world!")
    }
}
tasks.register("intro") {
    dependsOn("hello")
    doLast {
        println("I'm Gradle")
    }
}
```

```shell
> gradle -q intro
Hello world!
I'm Gradle
```

注意，依赖关系是懒加载的，可以在依赖项还没声明时就知名依赖。
例如上面的例子， intro 依赖了 hello，依然可以把 hello 放在 intro 后面声明:

```kotlin
tasks.register("intro") {
    dependsOn("hello")
    // ... ...
}
tasks.register("hello") {
    // ... ...
}
```

### 动态任务

任务可以通过动态代码创建出来:

```kotlin
listOf(1,2,3,4).forEach {
    tasks.register("hello-$it") {
        // ... ...
    }
}
```

这段代码动态创建了四个任务: hello-1, hello-2, hello-3, hello-4.

### 后期配置

声明任务以后，仍然可以在后期通过 `tasks.named` 获取到任务进行再次配置。

```kotlin
tasks.register("hello") {
    doLast {
        println("Hello Earth")
    }
}

// 下面都是二次配置
tasks.named("hello") {
    doFirst {
        println("Hello Venus")
    }
}
tasks.named("hello") {
    doLast {
        println("Hello Mars")
    }
}
tasks.named("hello") {
    doLast {
        println("Hello Jupiter")
    }
}
```

上面的代码，对 `hello` 任务进行了总共三次后期配置，分别附加了一次 `doFirst` ，两次 `doLast` 。
因此 `hello` 任务总共有 1 次 `doFirst` ，3 次 `doLast` ，最终效果如下:

```shell
> gradle -q hello
Hello Venus
Hello Earth
Hello Mars
Hello Jupiter
```

gradle 有很多第三方插件，它们自带了很多 task ，如果项目中需要对这些插件提供的 Task 做后期配置，
这个功能就派上用场了。

### 探索所有任务

通过 `gradle tasks --all` 查看当前项目以及所有子项目的任务

```shell
~/work/demo$ gradle tasks --all

> Task :tasks

--------------------------------------------
Tasks runnable from root project
--------------------------------------------

............ 这里会列出大量 task .............

Other tasks
-----------
app:hello

BUILD SUCCESSFUL in 1s
1 actionable task: 1 executed

```

## 原理

好像很复杂的样子?
这是怎么实现的呢?

### Project 对象

比如这样一个简单的构建脚本

```kotlin
// build.gradle.kts
println("hello world")
```

它会被复制到一个上下文的模板代码里面执行，
类似这样(不要深究, 这只是一种感性的理解):

```diff
    class Project {
        val name: String
        // TaskContainer is Collection<Task>
        val tasks: TaskContainer
        ... ...

        fun run() {
+           println("hello world")
        }
    }
    Project().run()
```

所以... 如果不知道 gradle 有哪些配置项，想了解 _Project 里面有什么东西_ 。可以通过两种途径:

1. 官方文档 [kotlin-api#Project](https://gradle.github.io/kotlin-dsl-docs/api/org.gradle.api/-project/index.html)
2. 编辑器中敲入 `this.` 或者 `project.` 查看代码提示

   ![gradle hint](/_static/gradle/gradle-project-this.jpg)

可以通过 `this` 以及 `project` 的代码提示找出所有操作。

### Task 对象

之前介绍 Task 一直是以 DSL 的形式，接下来介绍一下 Task 最原始的代码形式，以及如何演变成为 DSL。

#### task dsl 的原始形式

`Project::tasks` 是 `TaskContainer` 类型，它继承了 `Collection<Task>`，所以，最原始的代码我们应该这么写:

```kotlin
// gradle.build.kts 伪代码
val helloTask = Task()
helloTask.name = "hello"
helloTask.dependsOn("task1", "task2")
helloTask.doFirst({ println("hello doFirst") })
helloTask.doLast({ println("hello doLast") })

this.tasks.add(task)
```

当然，这只是伪代码，实际上是无法通过的，因为 Gradle 的 `Task` 是一个 interface，无法直接实例化。
不过 gradle 的 `TaskContainer` 提供了 `create` 方法创建 Task，
所以只需要稍微改造一下:

```kotlin
// 调用 TaskContainer.create
val helloTask = this.tasks.create("hello")

helloTask.dependsOn("task1", "task2")
helloTask.doFirst({ println("hello doFirst") })
helloTask.doLast({ println("hello doLast") })
```

不过，上面的代码有语法错误，因为 _gradle_ 要求不能通过 `this` 显式引用 `Project` 对象，只需要把上面的 `this` 去掉就好了； 或者改成通过 `project` 关键字引用 :

```kotlin
// 把 this.tasks 改成 tasks
val helloTask = tasks.create("hello")
// 或者改成:
// val helloTask = project.tasks.create("hello")

// 因为没有 task1/task2, 这里先注释掉
// helloTask.dependsOn("task1", "task2")
helloTask.doFirst({ println("hello doFirst") })
helloTask.doLast({ println("hello doLast") })
```

这个版本就是第一个可以正常运行的版本， 尝试运行一下:

```shell
> gradle -q hello
hello doFirst
hello doLast
```

结果和预期一致!! 这便是 task 原始的代码形式。

#### task dsl 的简化

**kotlin 特性 1** : lambda 作为函数最后一个参数时，可以省略括号。

借助这个特性，上面的 task 声明代码可以简化成这样:

```kotlin
val helloTask = tasks.create("hello")

helloTask.doFirst {
    println("hello doFirst")
}
helloTask.doLast {
    println("hello doLast")
}
```

这下有点 dsl 的意思了。

**kotlin 特性 2** : 对象初始化可以通过 scope function - apply 简化.

借助这个特性，则可以简化成这样:

```kotlin
tasks.create("hello").apply {
    this.doFirst {
        println("hello doFirst")
    }
    this.doLast {
        println("hello doLast")
    }
}
```

把 `this` 也进一步去掉:

```kotlin
tasks.create("hello").apply {
    doFirst {
        println("hello doFirst")
    }
    doLast {
        println("hello doLast")
    }
}
```

大功告成!!

实际上的 dsl 把 apply 也省略掉了，实现原理也很简单，
就是内部仿照 apply 实现了一遍:

```kotlin
TaskContainer.register(name: String, action: Action<Task>) {
    this.create(name).apply(action)
}
```

就变成了这样:

```kotlin
tasks.register("hello", {
    doFirst {
        println("hello doFirst")
    }
    doLast {
        println("hello doLast")
    }
})
```

注意上面的第二个参数 action 也是一个 lambda，所以也可以放到括号外面，就变成了最终形式:

```kotlin
tasks.register("hello") {
    doFirst {
        println("hello doFirst")
    }
    doLast {
        println("hello doLast")
    }
}
```
