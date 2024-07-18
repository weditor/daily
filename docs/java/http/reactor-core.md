# Reactor Core

## 基本流程

以一个最简单的 Reactor 案例

```kotlin
Flux.just(1, 2, 3).subscribe { println(it) }
```

上面的代码类似于 Java Stream。如果不看 Reactor 内部实现，而是我们自己实现，可以想象代码类似于这样

```kotlin
class Publisher(val data: List<Int>) {
    fun subscribe(subscriber: (Int) -> Unit) {
        data.forEach { subscriber(it) }
    }
}

// Publisher(listOf(1, 2, 3)).subscribe { println(it) }
```

```kotlin
class Publisher(val data: List<Int>) {
    private var subscriber: (Int) -> Unit

    fun subscribe(subscriber: (Int) -> Unit) {
        this.subscriber = subscriber
    }

    fun run() {
        while (true) {
            if (someCondition) {
                data.forEach { subscriber(it) }
            }
        }
    }
}

这是这类以流为基础的框架最基本的理念。下一步尝试扩充 subscriber 的能力, 希望 publisher 在送入数据之前先通知一下, 将它也定义为一个类:

```kotlin
class Subscriber {
    fun onSubscribe()
    fun onNext(item: Int) {
        println()
    }
}
```

```kotlin
class Publisher(val data: List<Int>) {
    private lateinit var subscriber: Subscriber

    fun subscribe(subscriber: (Int) -> Unit) {
        this.subscriber = subscriber
    }

    fun run() {
        while (true) {
            if (someCondition) {
                this.subscriber.onSubscribe()
                data.forEach { subscriber.onNext(it) }
            }
        }
    }
}
```

Reactor 中分为两种基本角色: Publisher(数据生产者)，Subscriber(数据消费者)

![reactor core](/_static/java/reactor-stream-1.drawio.svg)

```kotlin
Flux.just(1, 2, 3)
    .map { it * 2 } // op1
    .map { it * 2 } // op2
    .map { it * 2 } // op3
    .map { it * 2 } // op4
    .subscribe { println(it) } // subscriber
```

![reactor core](/_static/java/reactor-stream.drawio.svg)

考虑 (op3, op2) 这对操作符，这里面 op3 是 Subscriber, op2 是 Publisher. 而对于 (op4, op3) 来说，op3 就是 op4 的 Publisher。所以在一个流中，中间节点都同时兼任 Publisher/Subscriber 的角色。

## 算子优化

由于 Reactor 异步流本质上是递归回调，如果组织不好，有可能堆栈溢出，所以 subscribe 操作中会将递归调用组织为 for 循环，不过从功能上来讲，这两种实现是没有区别的。

具体实现为 `InternalFluxOperator`, 大部分算子都继承了这个类，所以构建流的过程中，大部分算子都可以避免递归。

它的原理就是 `InternalFluxOperator::optimizableOperator` 字段保留了对上游 Publisher 的引用。因此可以一直访问 optimizableOperator 字段来循环获得上游节点:

```kotlin
class InternalFluxOperator(source: Flux): FluxOperator(source) {
    // source 一般都继承了 OptimizableOperator
    private val optimizablesource = 
        if (source is OptimizableOperator) source else null

    fun subscribe(subscriber: CoreSubscriber) {
        var op = this
        while (true) {
            subscriber = op.subscribeOrReturn(subscriber)
            op = op.optimizablesource
        }
    }
}
```

## 算子重用

## ConditionalSubscriber


## 

AutomicIntegerFieldUpdater
