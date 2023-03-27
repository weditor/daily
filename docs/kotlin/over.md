# 后记

从表面上看，kotlin 对于 java 的大部分改进似乎都是语法糖。
实践中这些语法糖所发挥出来的作用却不仅限于语法糖。

从广义上讲，编程语言本身其实就是一种语法糖，
这不难理解，编程语言最后都要编译成汇编机器码执行。汇编是机器码的文本形式，C 语言可以直接翻译为汇编，C++的大部分代码也可以翻译为 C。虽然 C++ 是汇编的语法糖，但作为编程语言 C++ 与汇编相去甚远。

导致这种差异的原因，在于高级语言对代码赋予了 **语义**.
例如汇编最常规的是栈操作，而 C 语言基于栈操作，将指令分组，
为其赋予了函数的语义，又通过类型系统，将基础数据分组，赋予结构体的语义。
kotlin 引入的 `val` 、 `scope function` 等单独看似乎平平无奇，
但它们为代码提供的额外语义，积累起来形成的编程风格已经和 java 相去甚远。
kotlin 本身很简单，要领会 kotlin 的编程风格，要花费大量时间。

## 接下来

也许可以了解一下 [kotlin 协程](https://kotlinlang.org/docs/coroutines-overview.html) , [ArrowKt](https://arrow-kt.io/), [kotlin native](https://kotlinlang.org/docs/native-overview.html)?

社区和官方都很活跃, 未来可期。
主流 Java 库对于 kotlin 的适配异常积极，spring 官方也很早就完成了对 kotlin 的适配。
另外，最近(2022-12) kotlin 已经把 wasm 的原生支持排上了 roadmap; K2 编译器也有望 2023 年 stable 。
