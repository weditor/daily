# gradle wrapper

gradle 仍然是一个正在进行快速迭代的项目，并且内置 java 插件也要时刻跟上 jdk 的发行步伐，
经常新增特性或者有旧特性 deprecated , 这也导致了很多项目的 gradle 版本不统一的问题。

gradle 通过 gradle wrapper 实现项目自举解决了这个问题.
项目中只需要配置好需要的 gradle 版本号，构建过程中就会自动下载对应的版本进行构建.

这也是 **官方推荐** 的使用方式.

gradle-wrapper 是项目自带的，不需要额外安装。
使用项目初始化工具(gradle、spring-initializer 等)创建的项目，一般都自带 gradle-wrapper，
如果没有的话，也可以从其他项目复制过来.

## gradle wrapper 介绍

这是一个带有 gradle wrapper 的项目文件结构:

```diff
    .
    ├── src/
+   ├── gradle
+   │   └── wrapper
+   │       ├── gradle-wrapper.jar
+   │       └── gradle-wrapper.properties
+   ├── gradlew
+   ├── gradlew.bat
    ├── build.gradle.kts
    └── settings.gradle.kts

```

它相比正常的项目多出来四个文件

1. gradlew/gradlew.bat

   分别是 windows、linux 的执行入口。所有 `gradle` 命令都可以替换为 `./gradlew`,
   例如 `./gradlew build`

2. gradle-wrapper.properties

   gradle-wrapper 的配置文件，这是重点，后面介绍

3. gradle-wrapper.jar

   gradle-wrapper 的实现，一般不用关注。
   gradlew/gradlew.bat 脚本调用了 gradle-wrapper.jar 包

下面重点介绍 gradle-wrapper.properties

## gradle-wrapper.properties

gradle-wrapper.properties 文件内容为:

```ini
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-7.6.1-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
```

最重要的应该是 distributionUrl 配置，由于国内下载官网安装包很慢，
可以更改为使用[腾讯 gradle 镜像](https://mirrors.cloud.tencent.com/gradle/)

其次，有好几个配置使用了 `GRADLE_USER_HOME` 环境变量, 它们用于配置自动下载的 gradle 安装路径。
同时这个环境变量也决定了 gradle 管理的 manven 包缓存到什么地方。
GRADLE_USER_HOME 如果没有设置，默认是 `$HOME/.gradle` , 如果不想缓存到这里，可以修改这个环境变量。

见: [gradle-wrapper 官方文档](https://docs.gradle.org/current/userguide/gradle_wrapper.html)
