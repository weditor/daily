# task 结构、生命周期

到现在为止，已经介绍了 gralde 作为通用构建系统的那部分功能。

这部分功能几乎与 Make 是等价的，只不过它多了 Project 的概念，然后 task 多了 doFirst , doLast，以及通过 jvm 实现跨平台。

所以，如果只是这样的话，gradle 也会遇到和 Make 一样的问题: 任务组织比较混乱。所以，gradle 提供了两种方式来突出主要任务: 默认任务、构建周期。

## 默认任务

每个 Project 都有默认任务，通过 `defaultTasks` 函数指定. 如果直接不带参数运行 gradle, 则会运行默认任务。

例如:

```kotlin
// build.gradle.kts
// 设置 clean/run 为默认任务
defaultTasks("clean", "run")

tasks.register("clean") {
    doLast {
        println("Default Cleaning!")
    }
}
tasks.register("run") {
    doLast {
        println("Default Running!")
    }
}
tasks.register("other") {
    doLast {
        println("I'm not a default task!")
    }
}
```

```shell
> gradle -q
Default Cleaning!
Default Running!
```

## 生命周期任务(Lifecycle Tasks)

### 概念

生命周期任务是 gradle 定义的一系列标准任务名称，例如我们常用的:

- run: 运行
- build: 构建

如此一来，无论我们构建的是 java 还是 c++ 项目，都可以通过 `gradle run` 进行启动， `gradle build` 进行构建

生命周期任务本身 **并不会做任何事情** ，只是为了让其他任务附加到上面。
举个例子，假设项目构建时需要把配置文件拷贝到 dist, 就可以这么写:

```kotlin
tasks.register<Copy>("copyConfig") {
    from("config/config.json")
    into("$buildDir/config.json")
}
tasks.named("build") {
    dependsOn("copyConfig")
}
```

### 生命周期任务

[生命周期任务](https://docs.gradle.org/current/userguide/more_about_tasks.html#sec:lifecycle_tasks) 定义在 [Base Plugin](https://docs.gradle.org/current/userguide/base_plugin.html#sec:base_tasks) 中，所有的 gradle plugin 几乎都要实现这些标准任务，比如 `java plugin` .

所有生命周期任务如下:

- clean

  递归删除构建目录以及其中的所有文件。具体的目录路径可以通过 Project.getBuildDir() 获取到。

- check — lifecycle task

  用于附加其他项目检查任务，如 lint/unittest 等。
  用户执行 gradle check 执行所有检查

- assemble — lifecycle task

  所有用于生产最终产物的的任务都应该汇总到 assemble，例如 java plugin 的 jar 任务会创建 jar 包产物，
  因此 jar 任务就会被绑定到 assemble ，通过 assemble.dependsOn(task) 将其他 task 绑定到 assemble。

- build — lifecycle task

  依赖 check, assemble 任务。用于绑定所有构建动作，包括跑完所有测试，构建最终产物，生成文档。
  一般很少在 build 上直接附加其他任务，通常附加到 check/assemble 上更合适一点。

- buildConfiguration — task rule

  执行所有当前 Configuration 的依赖项。例如，buildArchives 会执行 archives 任务的所有依赖项。

- cleanTask — task rule

  约定每个任务可以定义一个自己的 clean 任务，用于删除当前任务的输出，例如在 java plugin 中 cleanJar 任务可以删除 jar 任务的所有输出
