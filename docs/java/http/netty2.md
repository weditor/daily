# Netty

## Netty 简介

下面是 Netty Server 的简单案例:

```kotlin
public class TestApplication {
    Integer port = 8080;

    public void run() throws Exception {
        EventLoopGroup bossGroup = new NioEventLoopGroup(); // (1)
        EventLoopGroup workerGroup = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap(); // (2)
            b.group(bossGroup, workerGroup)
                    .channel(NioServerSocketChannel.class) // (3)
                    .childHandler(new ChannelInitializer<SocketChannel>() { // (4)
                        @Override
                        public void initChannel(SocketChannel ch) throws Exception {
//                            ch.pipeline().addLast(new DiscardServerHandler());
                        }
                    })
                    .option(ChannelOption.SO_BACKLOG, 128)          // (5)
                    .childOption(ChannelOption.SO_KEEPALIVE, true); // (6)

            // Bind and start to accept incoming connections.
            ChannelFuture f = b.bind(port).sync(); // (7)

            // Wait until the server socket is closed.
            // In this example, this does not happen, but you can do that to gracefully
            // shut down your server.
            f.channel().closeFuture().sync();
        } finally {
            workerGroup.shutdownGracefully();
            bossGroup.shutdownGracefully();
        }
    }
}
```

以上代码标号对应解释:

1. 创建两个事件循环。这个事件循环即线程池，用来处理用户请求。
2. 创建一个启动器。ServerBootstrap 大部分方法都是 fluent api, 即会返回 this
3. 设置 ServerSocketChannel. 对应 java.nio 的 ServerSocketChannel。
4. 设置接受请求后的处理逻辑。
5. (暂时不必关注, 略)
6. (暂时不必关注, 略)
7. 绑定服务端口并阻塞

可以看到和 Java NIO 的概念可以大致对应上，例如 线程池/ServerSocketChannel/clientSocket 等。当然内部也有 ByteBuffer 之类概念。
而不同之处在于，netty 对这些东西都有自己的封装，对其或多或少作了改进，例如 ByteBuffer 实现了零拷贝，而 EventLoop 甚至已经不只是线程池，而是借鉴了协程的概念。

## ServerBootstrap

### ServerBootstrap 初始化

`ServerBootstrap::bind` 是启动服务的代码。其最终会调用到初始化核心逻辑 `ServerBootstrap::init` 函数, 核心代码如下:

```java
@Override
void init(Channel channel) {
    // 1. 构建 accept 的处理流水线
    ChannelPipeline p = channel.pipeline();

    // 2. 处理 ServerSocketChannel accept 事件，接收新请求
    p.addLast(new ChannelInitializer<Channel>() {
        @Override
        public void initChannel(final Channel ch) {
            // 3. 构建 read/write 的处理流水线
            final ChannelPipeline pipeline = ch.pipeline();
            ChannelHandler handler = config.handler();
            if (handler != null) {
                pipeline.addLast(handler);
            }

            ch.eventLoop().execute(new Runnable() {
                @Override
                public void run() {
                    // 4. 接收到新请求后, 将 SocketChannel 丢到线程池中进行读写 (read/write 事件)
                    pipeline.addLast(new ServerBootstrapAcceptor(ch, ...));
                }
            });
        }
    });
}
```

1. Pipeline: accept/read/write 处理器不再是单一函数，而是多个函数聚合成的 pipeline。
2. Channel: Netty 的 channel 仍然分为两层。
   1. 第一层 channel: 即 init 方法的参数，是 **Netty 简介** 案例代码第3步注册进来的 NioServerSocketChannel， 负责 `accept` 事件
   2. 第二层 channel: 负责 `read`/`write` 事件。
3. `config.handler()`: (第3步)是用户注册进来的 handler，即 **Netty 简介** 案例代码第4步。

随后，会将准备好的 channel 放到 eventloop 线程池中持续运行，见 `AbstractBootstrap::doBind0`。至此，服务启动完成。

:::{note} init 的调用链路

- AbstractBootstrap::bind
  - AbstractBootstrap::doBind
    - AbstractBootstrap::initAndRegister
      - ServerBootstrap::init
    - AbstractBootstrap::doBind0

`AbstractBootstrap::doBind0` 可以看到调用了 `NioServerSocketChannel::bind` 绑定具体套接字的操作。
如果继续追踪下去，会发现 executor 方法内会隐式调用 `startThread` 启动 EventLoop 的 run 方法，持续监听套接字。

:::

将客户端连接放到 childGroup 中进行读写是 `ServerBootstrapAcceptor` 的逻辑。

## Netty Pipeline

Netty pipeline 存在两个接口:

1. ChannelOutboundHandler, 表示与外界交互的接口, 以下简称为 Outbound
2. ChannelInboundHandler, 处理逻辑, 以下简称为 Inbound

上述两个接口的多个实现由 ChannelPipeline(默认实现: DefaultChannelPipeline) 汇总为一条责任链,
并且为了方便调用，ChannelPipeline 伪装为了 Outbound/Inbound.

Pipeline 中的责任链存在两个特殊的节点:

- HeadContext, 它实现了 Outbound
- TailContext. 实现了 Inbound

剩余用户添加的 Handler 的实现均为 Inbound.

HeadContext、TailContext 是 ChannelPipeline 的内部类，可以直接访问 pipeline 本身。

<!-- 由于是责任链实际代码里面，HeadContext/TailContext 都同时实现了 Outbound/Inbound, 只不过非本职的那部分都是代理了责任链上游接口。 -->

<!-- 例如 TailContext 的 Outbound 那部分的接口实现就都是一层简单的代理。 -->

Handler 都有自己的能力集。 Inbound 和 Outbound 都有自己特殊的能力集。发生事件后通过 findContextInbound、findContextOutbound 查找对应处理器，这两个函数一个是从前到后，一个是从后到前查找。

handler 引用 pipeline, pipeline 绑定 channel, channel 绑定 executor。

HeadContext 与 NioServerSocketChannel 之间通过 NioServerSocketChannel.unsafe() 对象连结。

DefaultChannelPipeline::read
AbstractNioChannel 里面保存了 selectionKey。

## TODO

- FastThreadLocal
