# 插件

## Script Plugin

构建项目过程中，有一些逻辑是通用的，比如构建 JavaDoc。
如果按照常规做法，我们得在每个 project 里面写一次 JavaDoc 构建任务的 task:

```kotlin
// build.gradle.kts
project.task("buildDoc") {
    doLast
        println("building document from comment... ")
    }
}
```

一个常规做法是文件复用, 这里就涉及到另一个知识: Gradle 的构建脚本(\*.kts) 是可以被其他构建脚本引入(import)的！
按照这个思路，我们把需要复用的逻辑放到 javadoc.gradle.kts 里面，然后其他项目引用它:

```kotlin
// myPlugins/javadoc.gradle.kts
project.task("buildDoc") {
    doLast
        println("building document from comment... ")
    }
}

// build.gradle.kts
apply(from = "myPlugins/javadoc.gradle.kts")
```

然后我们就可以执行 `gradle buildDoc` 使用这个任务了.
另外，`apply(from = ...)` 的语法不仅支持本地文件，也支持远程(http)文件.

这就是 Gradle 的 `Script Plugin`.

Script Plugin 使用非常直观，不过 Script Plugin 写多了之后不太好维护，尤其是插件需要跨项目共享的时候。
所以 Gradle 存在另一种更加适合工程化的 `Binary Plugin`，接下来介绍 Gradle 另一种插件: `Binary Plugin` 。

## Binary Plugin

Script Plugin 在单项目中跨模块共享比较好用，如果要跨项目，甚至开源社区共享的插件，
需要针对插件有比较正式的发布、测试流程，这种场景中 Binary Plugin 就更加适合。

为了实现插件的模块化，一个比较符合开发直觉的做法是: 把它封装为一个函数！

```kotlin
// build.gradle.kts
fun addJavaDocTask(proj: Project) {
    proj.task("buildDoc") {
        doLast
            println("building document from comment... ")
        }
    }
}

// 调用这个函数
addJavaDocTask(project)
```

这便是 Gradle 插件的基本原理! 只不过需要以一种特定的形式实现的: Plugin 接口。

下面是一个 Plugin 接口的简单案例

```kotlin
// build.gradle.kts
class JavaDocPlugin : Plugin<Project> {
    override fun apply(project: Project) {
        project.task("buildDoc") {
            doLast {
                println("building document from comment... ")
            }
        }
    }
}

// Apply the plugin
apply<JavaDocPlugin>()
```

```shell
> gradle -q buildDoc
building document from comment...
```

这个案例中，直接把 JavaDocPlugin 放在了 `build.gradle.kts` 构建脚本里面。
如果把它独立为一个插件项目，就变成了 `Binary Plugin` 了。
具体做法可以通过 [Java Gradle Plugin Development Plugin](https://docs.gradle.org/current/userguide/java_gradle_plugin.html#java_gradle_plugin) 实现。

最终 `Binary Plugin` 会发布为一个 maven jar 包, 其他人只需要在 gradle 的 plugins 配置项中引用这个 jar 包就可以了.
如果是发布到了私有 maven 仓库，需要在 settings.gradle.kts 中配置源。

```kotlin
// build.gradle.kts
plugins {
    id("org.springframework.boot") version "2.7.5"
}

// settings.gradle.kts
pluginManagement {
    repositories {
        maven {url = uri("https://maven.aliyun.com/repository/gradle-plugin")}
    }
}
```

## 总结

虽然 Binary Plugin 更加工程化，而且可以对其进行测试。
但是 Script Plugin 和 Binary Plugin 并不存在哪个更“高级”的说法，
Script Plugin 使用更加直观，团队中的插件一般都是从 Script Plugin 开始发展，在其流程确定、发展成熟后，
才会开始考虑将其实现为 Binary Plugin 以便大规模共享。

官方文档: [gradle plugins](https://docs.gradle.org/current/userguide/custom_plugins.html)
