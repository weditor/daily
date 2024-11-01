# Arthas 常用方法

## 快速开始

启动方法, 运行 `java -jar arthas-boot.jar`，并按照提示，选择要调试的进程:

```bash
[tmpUser@localhost-iy89g ~]$ cd /opt/lib/arthas
[tmpUser@localhost-iy89g arthas]$ java -jar arthas-boot.jar
* [1]: 11 ./lib/project-main.jar
1

[INFO] arthas home: /opt/lib/arthas
[INFO] Try to attach process 11
[INFO] Attach process 11 success.
[INFO] arthas-client connect 127.0.0.1 3658
  ,---.  ,------. ,--------.,--.  ,--.  ,---.   ,---.
 /  O  \ |  .--. ''--.  .--'|  '--'  | /  O  \ '   .-'
|  .-.  ||  '--'.'   |  |   |  .--.  ||  .-.  |`.  `-.
|  | |  ||  |\  \    |  |   |  |  |  ||  | |  |.-'    |
`--' `--'`--' '--'   `--'   `--'  `--'`--' `--'`-----'


wiki: https://arthas.aliyun.com/doc
version: 3.5.4
pid: 11
time: 2024-10-25 19:16:24

[arthas@11]$
```

看到 `[arthas@pid]$` 样式的命令行提示符就代表成功了，之后可以输入 arthas 命令进行调试。

## watch

监控 `com.example.demo.MathGage::primeFactors` 方法的参数、返回值

```bash
[arthas@11]$ watch com.example.demo.MathGame primeFactors
Press Q or Ctrl+C to abort.
Affect(class count: 1 , method count: 1) cost in 32 ms, listenerId: 5
method=com.example.demo.MathGame.primeFactors location=AtExceptionExit
ts=2021-08-31 15:22:57; [cost=0.220625ms] result=@ArrayList[
    @Object[][
        @Integer[-179173],
    ],
    @MathGame[
        random=@Random[java.util.Random@31cefde0],
        illegalArgumentCount=@Integer[44],
    ],
    null,
]
```

## watch 参数

参数名称 | 参数说明
---|---
class-pattern | 类名表达式匹配
method-pattern | 函数名表达式匹配
express | 观察表达式，默认值：`{params, target, returnObj}`
condition-express | 条件表达式
-b | 在函数调用之前观察
-e | 在函数异常之后观察
-s | 在函数返回之后观察
-f | 在函数结束之后(正常返回和异常返回)观察
-E | 开启正则表达式匹配，默认为通配符匹配
-x \<arg\> | 指定输出结果的属性遍历深度，默认为 1, 最大值是 4
-m \<arg\> | 指定 Class 最大匹配数量，默认值为 50。长格式为[maxMatch \<arg\>]

## ognl

[Apache Commons OGNL](https://commons.apache.org/dormant/commons-ognl/language-guide.html)

```java
name.toCharArray()[0].numericValue.toString()
```

## sc/sm

sc: 展示 class(show class)

```shell
[arthas@11]$ sc com.example.*
com.example.Application
com.example.compressor.Compressor
com.example.compressor.Compressor$ZstdCompressor
com.example.config.AppConfig
com.example.config.AppConfig##EnhancerBySpringCGLIB$$a59fae24
# more class ...
```

sm: 展示方法(show method)

```shell
[arthas@11]$ sm com.example.config.AppConfig
com.example.config.AppConfig <init>
com.example.config.AppConfig startLogMonitorTask$lambda-0
com.example.config.AppConfig getByteRedisTemplate
com.example.config.AppConfig startLogMonitorTask
```

sc/sm 与 grep 配合使用

```shell
[arthas@11]$ sc com.example.* | grep Compressor
com.example.compressor.Compressor
com.example.compressor.Compressor$ZstdCompressor
```

## stack/trace

```shell
$ stack demo.MathGame primeFactors
Press Ctrl+C to abort.
Affect(class-cnt:1 , method-cnt:1) cost in 36 ms.
ts=2018-12-04 01:32:19;thread_name=main;id=1;is_daemon=false;priority=5;TCCL=sun.misc.Launcher$AppClassLoader@3d4eac69
    @demo.MathGame.run()
        at demo.MathGame.main(MathGame.java:16)
```

stack: 当前函数的调用者
trace: 当前函数调用的其他函数

```txt
App::main()                            |
└─ Dispatcher::dispatch()              | stack
    ├─ UserController::listUser        |
    └─ UserService::listUser             | current function
        ├─ UserService::filter         |
        │  └─ ConditionParser::parse   | trace
        └─ UserRepository::listUser    |
```

## thread

展示所有线程简略信息

```sh
$ thread
Threads Total: 33, NEW: 0, RUNNABLE: 9, BLOCKED: 0, WAITING: 3, TIMED_WAITING: 4, TERMINATED: 0, Internal threads: 17
ID   NAME                           GROUP          PRIORITY  STATE     %CPU      DELTA_TIME TIME      INTERRUPT DAEMON
-1   C2 CompilerThread0             -              -1        -         5.06      0.010      0:0.973   false     true
-1   C1 CompilerThread0             -              -1        -         0.95      0.001      0:0.603   false     true
23   arthas-command-execute         system         5         RUNNABLE  0.17      0.000      0:0.226   false     true
-1   VM Periodic Task Thread        -              -1        -         0.05      0.000      0:0.094   false     true
-1   Sweeper thread                 -              -1        -         0.04      0.000      0:0.011   false     true
-1   G1 Young RemSet Sampling       -              -1        -         0.02      0.000      0:0.025   false     true
12   Attach Listener                system         9         RUNNABLE  0.0       0.000      0:0.022   false     true
11   Common-Cleaner                 InnocuousThrea 8         TIMED_WAI 0.0       0.000      0:0.000   false     true
3    Finalizer                      system         8         WAITING   0.0       0.000      0:0.000   false     true
2    Reference Handler              system         10        RUNNABLE  0.0       0.000      0:0.000   false     true
4    Signal Dispatcher              system         9         RUNNABLE  0.0       0.000      0:0.000   false     true
15   arthas-NettyHttpTelnetBootstra system         5         RUNNABLE  0.0       0.000      0:0.029   false     true
22   arthas-NettyHttpTelnetBootstra system         5         RUNNABLE  0.0       0.000      0:0.196   false     true
24   arthas-NettyHttpTelnetBootstra system         5         RUNNABLE  0.0       0.000      0:0.038   false     true
16   arthas-NettyWebsocketTtyBootst system         5         RUNNABLE  0.0       0.000      0:0.001   false     true
17   arthas-NettyWebsocketTtyBootst system         5         RUNNABLE  0.0       0.000      0:0.001   false     true
```

展示线程详细信息

```sh
$ thread 1
"main" Id=1 WAITING on java.util.concurrent.CountDownLatch$Sync@29fafb28
    at sun.misc.Unsafe.park(Native Method)
    -  waiting on java.util.concurrent.CountDownLatch$Sync@29fafb28
    at java.util.concurrent.locks.LockSupport.park(LockSupport.java:175)
    at java.util.concurrent.locks.AbstractQueuedSynchronizer.parkAndCheckInterrupt(AbstractQueuedSynchronizer.java:836)
    at java.util.concurrent.locks.AbstractQueuedSynchronizer.doAcquireSharedInterruptibly(AbstractQueuedSynchronizer.java:997)
    at java.util.concurrent.locks.AbstractQueuedSynchronizer.acquireSharedInterruptibly(AbstractQueuedSynchronizer.java:1304)
    at java.util.concurrent.CountDownLatch.await(CountDownLatch.java:231)
```

展示阻塞其他线程的线程

```sh
$ thread -b
"http-bio-8080-exec-4" Id=27 TIMED_WAITING
    at java.lang.Thread.sleep(Native Method)
    at test.arthas.TestThreadBlocking.doGet(TestThreadBlocking.java:22)
    -  locked java.lang.Object@725be470 <---- but blocks 4 other threads!
    at javax.servlet.http.HttpServlet.service(HttpServlet.java:624)
    at javax.servlet.http.HttpServlet.service(HttpServlet.java:731)
```

## heapdump

## profiler

生成调用堆栈的 html

```sh
$ profiler start
Started [cpu] profiling

$ profiler stop --file /tmp/first.html
profiler output file: /tmp/first.html
OK
```

## jobs

后台任务可以用来排查偶发问题

```shell
# 启动后台任务并输出到文件
$ watch com.example.demo.MathGame primeFactors > /tmp/out.txt &

# 查看所有后台任务
$ jobs
[1]*
    watch com.example.demo.MathGame primeFactors

# 停止后台任务
$ kill 1
```

## 链接

https://arthas.aliyun.com/doc/expert/intro.html

https://arthas.aliyun.com/doc/commands.html

ognl: https://commons.apache.org/dormant/commons-ognl/language-guide.html