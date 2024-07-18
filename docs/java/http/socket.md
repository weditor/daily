# Java Nio Socket

## 服务端 Socket 概念

对于 Linux 系统，一切皆文件，socket 也是文件，所以对于socket通信，其操作等价于打开一个文件描述符(fd)进行读写，与普通文件读写无异。

伪代码:

```python
socket = open(fd)
# 向远程发送消息
socket.send("hello")
# 读取对方发送过来的消息
content = socket.read()
```

对于客户端来说，与服务端建立一个 socket 连接, 对其进行读写就好了.
对于服务端来说，情况稍微有些不同，服务端需要两层 socket:

1. 第一个固定 socket 对象用于绑定服务端口，监听有哪些 client 请求连接(accept)。
2. 接收到连接后，针对每个连接创建一个新的 socket 对象，用于与 client 通信(read/write)。

![服务端 socket](/_static/java/socket.drawio.svg)

## 单线程 Server

下面是 Java 实现的一个简单的 echo 服务器，客户端输入什么，服务端就会返回什么。
(为了突出重点，省略了很多错误处理逻辑)

```kotlin
fun startServer() {
    val socket = ServerSocketChannel.open()
    socket.bind(InetSocketAddress("localhost", 8000))

    while (true) {
        // accept 阻塞， 监听客户端连接，
        // 得到一个新的 SocketChannel
        val clientSocket = socket.accept()
        // 处理客户端请求
        processClient(clientSocket)
        clientSocket.close()
    }
}
```

处理客户端请求:

```kotlin
fun processClient(socket: SocketChannel) {
    socket.write(ByteBuffer.wrap("hello from server".toByteArray()))

    // 4k buffer
    val byteBuffer = ByteBuffer.allocate(4 * 1024)
    while (true) {
        // read 阻塞
        if (socket.read(byteBuffer) < 0) {
            return
        }
        byteBuffer.flip()
        socket.write(byteBuffer)
        byteBuffer.clear()
    }
}
```

启动服务后，通过telnet 输入 `hello` 可以看看效果:

```bash
root@localhost:~/$ telnet localhost 8000
hello from server hheelllloo
```

可以看到，服务端输出 `hello from server` 后，我们每次输入一个字符，服务端都会立即返回一个相同的字符。

这便是最简单的 echo 服务端。

## 多线程 Server

上面的单线程 Server 只能对一个客户端服务，因为 read/write 过程中，不会走到 `socket.accept()` , 导致服务端无法接收新请求。

正确的做法应该是 `socket.accept()` 接收到新请求后，立即将其丢到其他线程(池)里面去处理，这样主线程就能继续接收新请求了:

```{code-block} kotlin
:emphasize-lines: 2,10,13
:lineno-start: 1

fun startServer() {
    val threadPool = Executors.newFixedThreadPool(4)

    val socket = ServerSocketChannel.open()
    socket.bind(InetSocketAddress("localhost", 8000))

    while (true) {
        val clientSocket = socket.accept()

        threadPool.submit {
            processClient(clientSocket)
            clientSocket.close()
        }
    }
}
```

## 非阻塞 Server

java.nio.channels 提供了非阻塞接口，只需要调用 `channel.configureBlocking(false)` 即可。
这会导致原来的 `accept` `read` 等阻塞接口编程非阻塞接口，需要我们自己实现轮询:

- `SocketChannel accept()`: 如果当前没有新的连接，则立即返回 null，而非阻塞。
- `int read(ByteBuffer dst)`: 如果没有新数据，则立即返回读取长度=0，而非阻塞。

仍然以服务端为例:

```{code-block} kotlin
:emphasize-lines: 3,8-10
:lineno-start: 1

fun startServer() {
    val socket = ServerSocketChannel.open()
    socket.configureBlocking(false)
    socket.bind(InetSocketAddress("localhost", 8000))

    while (true) {
        val clientSocket = socket.accept()
        if (clientSocket == null) {
            continue
        }
        processClient(clientSocket)
        clientSocket.close()
    }
}
```

引入这个特性后就牛逼了, 可以实现通过单线程同时监听多个服务端口!

```{code-block} kotlin
:emphasize-lines: 3,5,11
:lineno-start: 1

fun startServer() {
    val pool = Executors.newFixedThreadPool(4)
    val sockets: List<ServerSocketChannel> = ...
    while (true) {
        for (socket in sockets) {
            val clientSocket = socket.accept()
            if (clientSocket == null) {
                continue
            }
            pool.submit { processClient(clientSocket) }
        }
    }
}
```

当然也可以实现单线程监听多个客户端连接!

```{code-block} kotlin
:emphasize-lines: 2,5,14
:lineno-start: 1

fun processClient() {
    val sockets: List<SocketChannel> = ...
    
    while (true) {
        for (socket in sockets) {
            val size = socket.read(buffer)

            if (size == 0) continue
            if (size < 0) {
                println("closed by client")
                return
            }
            ... ...
        }
    }
}
```

:::{note}
如果你乐意的话，甚至把所有 socket 的 accept/read/write 都放到一个线程里面做，共享一个 Selector。
:::

## Selector

非阻塞 Server 已经非常接近理想的服务端 socket 模型，
接下来介绍的 Selector 则是 Java NIO 开发者提供的原生的轮询机制，用来协助监听多个 channel 。

只要把上面的 while 轮询改为 Selector 就差不多完美了!

:::{note}
Selector 这个名字看起来有些奇怪? 这是因为 select 编程模型(IO 多路复用)来自 linux c api,
后面其他编程语言就都约定使用这套概念。相关概念可以搜索 select/poll/epoll，不过它们的演进又是另一个话题了。
:::

Selector 基础用法:

```kotlin
// 创建一个 selector
val selector = Selector.open()

// 往 selector 中注册多个 channel
// 并告知感兴趣的事件类型
channelA.register(selector, SelectionKey.OP_ACCEPT)
channelB.register(selector, SelectionKey.OP_ACCEPT)

while (true) {
    // 阻塞，直到任意 channel 有请求进来
    selector.select()

    // 获取所有准备好的连接
    val keys = selector.selectedKeys()
    keys.forEach {
        val channel = it.channel()
        // do something ...
    }
    // 清空当前 keys, 准备进行下次 select.
    keys.clear()
}
```

`processClient` 中也可以照搬这套逻辑, 准备一个全局 `Selector`, 有新的连接就往 Selector 中注册:

```kotlin
class ClientHandler {
    private val selector = Selector.open()

    fun register(channel: SocketChannel) {
        channel.register(this.selector, SelectionKey.OP_READ)
    }

    fun run() {
        while (true) { this.run0() }
    }
    private fun run0() {
        selector.select()
        val keys = selector.selectedKeys()
        keys.forEach {
            val channel = it.channel() as SocketChannel
            val buffer = ByteBuffer.allocate(128)

            if (channel.read(buffer) < 0) {
                channel.close()
            } else {
                buffer.flip()
                channel.write(buffer)
                buffer.clear()
            }
        }
        keys.clear()
    }
}
```

## 总结

这里粗略介绍了服务端 socket 编程的演进路线。

1. 单线程 Server
2. 多线程 Server
3. 非阻塞 Server
4. Selector

在最后的 Selector 模型中，其中涉及到三个重要的对象: `Selector`/`Channel`/`ByteBuffer`

后面继续介绍在 NIO 的基础上， Netty 是如何实现的。  
