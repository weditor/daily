# 构建系统

## 构建系统介绍

首先介绍一下 Make，Ant 这些构建系统, 会对 gradle 的设计思路有一些帮助。

### Make

Make 是一个古老、广泛使用的经典构建系统，或者是 "任务系统"， 任务是 Make 比较重要的概念.
它的格式是这样的:

```makefile
# Makefile
mytask:
    cd /work/project && touch desc.txt
    ls /work/project
    echo "finish!"
```

`mytask` 是任务名称, 任务(Task)由一系列 shell 命令(Command)组成，通过缩进来体现层级。

在 Linux 上将这个文件保存为 Makefile, 然后执行 `make mytask` 命令(make 隐式约定会寻找当前目录下的 Makefile 文件)，就会执行 `mytask` 里面的指令，最后一条指令会输出 "finish"

任务之间也可以有依赖, 下面的 `taskZ` 依赖了 `taskA`、`taskB`:

```makefile
// Makefile
taskA:
    echo "I'm task a"
taskB:
    echo "I'm task b"

taskZ: taskA taskB
    echo "I'm task Z"
```

执行 `make taskZ` 会输出:

```text
I'm task a
I'm task b
I'm task z
```

如果用 make 来做 java 构建:

```makefile
build:
    javac *.java -d build/classes/
    cd build/classes && jar cvf mine.jar *.class
```

Makefile 理念很简单，使用灵活，语法完善，功能强大，几乎是一种完美的构建系统，所以经久不衰。它确定了基于 _DAG 任务系统_ 来实现 _构建系统_ 的基本思路.

Make 内的指令都是 shell 指令，与 shell 深度绑定绑定，所以在 Linux 上使用较多，跨平台不太方便。那有什么是跨平台的呢？java 就是其中之一，所以就有人想能不能将指令使用 java 实现，如此一来就能实现一种跨平台的任务系统了。所以就诞生了 Ant。

### Ant

[Ant](https://ant.apache.org/) 也是一种通用型构建系统，基本思路与 Make 一致。

Make 只有 Task/Command 两层结构，主 task 和子 task 在并没有分别，都可以单独执行，所以维护者可能很难找到要执行哪一个任务, 这方面只能靠公共约定。

Ant 做了一些改进，拥有 Project/Target/Task 三层结构，
其中 Target/Task 分别对应了 Make 的 Task/Command 概念，
这么一来虽然不是纯粹的任务系统，但是更像构建系统了。
也能凸显出上层的 project，而更少关注细节。

下面是 Ant 官网的构建配置入门案例:

```xml
<project name="MyProject" default="dist" basedir=".">
  <description>
    simple example build file
  </description>
  <!-- set global properties for this build -->
  <property name="src" location="src" />
  <property name="build" location="build" />
  <property name="dist" location="dist" />

  <target name="init">
    <!-- Create the time stamp -->
    <tstamp />
    <!-- Create the build directory structure used by compile -->
    <mkdir dir="${build}" />
  </target>

  <target name="compile" depends="init" description="compile the source">
    <!-- Compile the Java code from ${src} into ${build} -->
    <javac srcdir="${src}" destdir="${build}" />
  </target>

  <target name="dist" depends="compile" description="generate the distribution">
    <!-- Create the distribution directory -->
    <mkdir dir="${dist}/lib" />

    <!-- Put everything in ${build} into the MyProject-${DSTAMP}.jar file -->
    <jar jarfile="${dist}/lib/MyProject-${DSTAMP}.jar" basedir="${build}" />
  </target>

  <target name="clean" description="clean up">
    <!-- Delete the ${build} and ${dist} directory trees -->
    <delete dir="${build}" />
    <delete dir="${dist}" />
  </target>
</project>
```

虽然是 xml，不过仍然可以看出来 Make 的影子,
比如上面的 `mkdir` `delete` `javac` 等, 只不过他们都是 java 实现的。
比如 delete, 就对应了一个 java 函数，它接受一个 dir 参数。

如果希望自定义指令，可以自己写一个 ant 插件，编译一个 jar 包让 ant 加载上去。

另外，Ant 抽象出的 Project/Target/Task 三层概念除了体现在 xml 配置上，在 Ant 中也有对应的 class 定义，例如 Project 是一个 class，绑定了 name/baseDir 等属性，Target 也是一个 class 保留了父 Project 的引用，可以读取上面的属性。

在实践中，要自定义功能写 Ant 插件的场景比较多，每个项目都针对性地写插件还是有些麻烦。有人就想: 为什么不直接在构建脚本里面写 jvm 代码呢? 所以就诞生了 gradle。

## Gradle

它和 Make 类似，也是一种通用构建系统，使用 DAG 组织任务

![gradle dag](/_static/gradle/gradle-dag.png)

gradle 也有三层概念: Project/Task/Code, 其中 Task/Code 对应了 Make 的 Task/Command。
gradle 的构建脚本就是 jvm 代码，目前支持两种语言: `groovy`/`kotlin`. 后面介绍主要使用 `kotlin DSL`.

比如这就是一个很简单的 gradle 构建脚本:

```kotlin
// build.gradle.kts
println("hello world")
```

只不过它只打印了 _hello world_ , 而且这个案例没有体现 task 概念，后面再展开介绍。

gradle 的历史以及基本原理算是说完了，后面开始介绍 gradle 的使用方法了。
