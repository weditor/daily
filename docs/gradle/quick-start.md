# gradle 快速入门

gradle 是什么? gradle 是 maven 构建工具的替代品

## 安装 gradle

> gradle 运行需要 jdk, 所以要先安装 java, 设置 JAVA_HOME。这里就不演示了

gradle 可以从[官网 Release 页面](https://gradle.org/releases/)下载安装包。
解压后 bin/gradle 可以直接执行:

```text
gradle/
    ├─ bin/
    │   ├─ gradle       # linux 执行入口
    │   └─ gradle.bat   # windows 执行入口
    ├─ docs/
    ├─ init.d/
    ├─ lib/
    ├─ src/
    ├─ LICENSE
    ├─ NOTICE
    └─ README
```

注意事项 1: gradle 版本类型

> gradle 发行包有 binary-only 和 complete 两种，下载的文件后缀分别是 `-bin` 和 `-all`。
> binary-only 是编译好的可执行程序, complete 还额外附带 gradle 本身的代码。
> 一般 bin 就够用了，不过我推荐下载 all, 如果要写自定义插件的话，会依赖 src 进行编译, 还不如一步到位。

注意事项 2: gradle 国内下载慢

> 可以到腾讯云镜像上下载: [腾讯云 gradle 镜像](https://mirrors.cloud.tencent.com/gradle/)

注意事项 3: gradle 环境变量配置

> 默认情况下，gradle 会把下载的文件(例如从 maven repository 下载的依赖包)缓存到 home 目录。
> 如果不希望下载到默认目录，
> 可以通过设置环境变量 GRADLE_USER_HOME 指定为其他目录

## 初始化一个 gradle 项目

执行 `gradle init`, 初始化一个 gradle 项目。
gradle 项目初始化脚手架提供了丰富的选项，用于创建各种类型的项目模板。
下面的案例初始化了一个常见的 java 单模块的可执行项目。

```shell
~/work$ mkdir demo && cd demo
~/work/demo$ gradle init

Select type of project to generate:
  1: basic
  2: application
  3: library
  4: Gradle plugin
Enter selection (default: basic) [1..4] 2

Select implementation language:
  1: C++
  2: Groovy
  3: Java
  4: Kotlin
  5: Scala
  6: Swift
Enter selection (default: Java) [1..6] 3

Split functionality across multiple subprojects?:
  1: no - only one application project
  2: yes - application and library projects
Enter selection (default: no - only one application project) [1..2] 1

Select build script DSL:
  1: Groovy
  2: Kotlin
Enter selection (default: Groovy) [1..2] 2

Select test framework:
  1: JUnit 4
  2: TestNG
  3: Spock
  4: JUnit Jupiter
Enter selection (default: JUnit 4) [1..4] 1

Project name (default: demo):
Source package (default: demo): com.example.demo

> Task :init
Get more help with your project: https://docs.gradle.org/6.7/samples/sample_building_java_applications.html

BUILD SUCCESSFUL in 28s
2 actionable tasks: 2 executed

~/work/demo$
```

新项目结构如下:

```shell
~/work/demo$ tree
.
│  .gitattributes
│  .gitignore
│  gradlew
│  gradlew.bat
│  settings.gradle.kts
│
├─.gradle
├─app
│  │  build.gradle.kts
│  │
│  └─src
│      ├─main
│      │  ├─java
│      │  │  └─com
│      │  │      └─example
│      │  │          └─demo
│      │  │                  App.java
│      │  │
│      │  └─resources
│      └─test
│          ├─java
│          │  └─com
│          │      └─example
│          │          └─demo
│          │                  AppTest.java
│          │
│          └─resources
└─gradle
    └─wrapper
            gradle-wrapper.jar
            gradle-wrapper.properties

```

## 运行项目

原本这个项目是可以直接运行的，由于国内访问 maven/gradle 等网站很慢，编译被卡脖子了，所以咱们还得采用一些手段让它运行起来。

### 配置 settings.gradle.kts

在 settings.gradle.kts 中加入:

```kotlin
// settings.gradle.kts
pluginManagement {
    repositories {
        maven {url = uri("https://maven.aliyun.com/repository/gradle-plugin")}
    }
}
```

### 配置 build.gradle.kts

注释掉 build.gradle.kts 中的 jcenter 源, 配置 maven 国内源:

```kotlin
// build.gradle.kts
repositories {
    // jcenter()
    maven {url = uri("https://maven.aliyun.com/repository/public")}
}
```

### 配置 IDEA 编辑器

使用 IDEA 打开我们刚才创建的项目

![open project](/_static/gradle/idea-open-gradle.jpg)

选中新项目的目录，点击 **OK**

![open project](/_static/gradle/idea-open-gradle-2.jpg)

项目打开后，IDEA 默认会从官网重新下载 gradle 进行构建, 一般都会失败. 所以构建之前得告诉他使用本地安装好的 gradle.

通过菜单栏依次进入 `File` -> `settings` -> `Build,Execution,Deployment` -> `Build Tools` -> `Gradle`,
在下面一点的位置找到 Use Gradle from 下拉框，设置为 _Specified location_ , 填写 gradle 安装的路径，这里是 `D:\env\gradle-6.7`. 保存

![choose gradle](/_static/gradle/idea-choose-gradle.jpg)

### 运行

然后就可以进行构建了, 重启 IDEA 会自动构建。或者在右侧找到 gradle 页卡, 点刷新按钮，刷新按钮是灰色可能是因为正在构建。
如果遇到什么问题，可以尝试重启 IDEA.

![gradle refresh](/_static/gradle/gradle-refresh.jpg)

等待一会儿刷新完成，就可以执行 main 函数了

![run](/_static/gradle/run-gradle.jpg)

## 增加依赖

在 dependencies 配置段的 implementation 增加依赖。

例如我们要增加 logback 日志库的依赖:

```kotlin
dependencies {
    // Use JUnit test framework.
    testImplementation("junit:junit:4.13")

    // This dependency is used by the application.
    implementation("com.google.guava:guava:29.0-jre")
    // 增加 logback 依赖
    implementation("ch.qos.logback:logback-classic:1.2.11")
    implementation("ch.qos.logback:logback-core:1.2.11")
}
```

## 构建

命令行中可以通过执行 `gradle build` 进行构建. 会在 _app/build/libs_ 下生成构建好的 jar 包。

```shell
~/work/demo$ gradle build

Starting a Gradle Daemon, 2 incompatible and 2 stopped Daemons could not be reused, use --status for details

BUILD SUCCESSFUL in 15s
7 actionable tasks: 7 executed

~/work/demo$ tree
.
├─... ...
├─app
│  │  build.gradle.kts
│  │
│  ├─build
│  │  ├─libs
│  │  │      app.jar
│  │  │
│  │  └─... ...

~/work/demo$
```

## gradle + spring

如果使用 spring 框架开发，可以通过 [spring initializer](https://start.spring.io/) 脚手架生成项目模板。

恭喜! 至此您已经学会使用 gradle 进行日常 java 开发了.

如果想了解如何新建其他类型项目(如 kotlin/c++)，可以参照 gradle [samples](https://docs.gradle.org/current/samples/index.html) 页面的案例。

## 梦的破碎

gradle 是 maven 的替代品吗? 是的。但 gradle 不是 maven!

gradle 可以像上面一样用的很简单，也可以用的很复杂。
真实项目场景下，难免也会遇到很复杂的 gradle 构建脚本，
初学者初次面对这类构建脚本往往一头雾水，例如下面是节选 spring-core 的构建脚本:

```groovy
description = "Spring Core"

apply plugin: "kotlin"
apply plugin: "kotlinx-serialization"

def javapoetVersion = "1.13.0"
def objenesisVersion = "3.2"

configurations {
    javapoet
    graalvm
}
task javapoetSource(type: ShadowSource) {
    configurations = [project.configurations.javapoet]
    relocate('com.squareup.javapoet', 'org.springframework.javapoet')
    outputDirectory = file("build/shadow-source/javapoet")
}

task javapoetSourceJar(type: Jar) {
    archiveBaseName = 'spring-javapoet-repack'
    archiveVersion = javapoetVersion
    archiveClassifier = 'sources'
    from javapoetSource
}

task objenesisRepackJar(type: ShadowJar) {
    archiveBaseName = 'spring-objenesis-repack'
    archiveVersion = objenesisVersion
    configurations = [project.configurations.objenesis]
    relocate('org.objenesis', 'org.springframework.objenesis')
}
dependencies {
    javapoet("com.squareup:javapoet:${javapoetVersion}@jar")
    objenesis("org.objenesis:objenesis:${objenesisVersion}@jar")
    api(files(javapoetRepackJar))
    api(files(objenesisRepackJar))
    api(project(":spring-jcl"))
    compileOnly("io.projectreactor.tools:blockhound")
    compileOnly("org.graalvm.sdk:graal-sdk")
    optional("net.sf.jopt-simple:jopt-simple")
    optional("org.jetbrains.kotlinx:kotlinx-coroutines-core")
    testImplementation("jakarta.annotation:jakarta.annotation-api")
    testImplementation("jakarta.xml.bind:jakarta.xml.bind-api")
    testFixturesImplementation("com.google.code.findbugs:jsr305")
    testFixturesImplementation("io.projectreactor:reactor-test")
}

jar {
    manifest.attributes["Dependencies"] = "jdk.unsupported"  // for WildFly (-> Objenesis 3.2)

    dependsOn javapoetRepackJar
    from(zipTree(javapoetRepackJar.archivePath)) {
        include "org/springframework/javapoet/**"
    }

    dependsOn objenesisRepackJar
    from(zipTree(objenesisRepackJar.archivePath)) {
        include "org/springframework/objenesis/**"
    }
}

test {
    jvmArgs += [
        "-XX:+AllowRedefinitionToAddDeleteMethods"
    ]
}

sourcesJar {
    dependsOn javapoetSourceJar
    dependsOn objenesisSourceJar
    from javapoetSource
    from objenesisSource
}

eclipse {
    synchronizationTasks javapoetSourceJar, objenesisSourceJar
    classpath {
        file {
            whenMerged {
                def pattern = ~/\/spring-\w+-repack-/
                entries.forEach {
                    if (pattern.matcher(it.path).find()) {
                        def sourcesJar = it.path.replace('.jar', '-sources.jar');
                        it.sourcePath = fileReference(file(sourcesJar))
                    }
                }
            }
        }
    }
}

tasks['eclipse'].dependsOn(javapoetRepackJar, javapoetSourceJar, objenesisRepackJar, objenesisSourceJar)
```

与 maven 的简单比起来，gradle 这种复杂度令人望而生畏。
很多 gradle 教程也试图掩盖这些东西(把狗先骗进来再杀)。
不过不用担心，后面的章节会帮助大家理解 gradle 的工作原理，将把这些东西全都剥开，这些前期看似复杂的配置后面就都能看懂了(至少知道怎么能看懂)。

这都是因为 gradle 是一种通用型任务工具，而 maven 更多地是作为 java 依赖管理工具, 两者不是同一个领域的东西。
只不过在 java 领域，maven 附加的构建功能刚好够用而已。
maven 的简单是因为它只能完成这么简单的工作，在 gradle 的复杂在于，只要使用 gradle 的高级特性，
很可能就会让构建脚本复杂度急剧上升。
毫无疑问 gradle 功能更加强大，也更难把控。
