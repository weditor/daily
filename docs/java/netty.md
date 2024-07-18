# netty

- handler 处理请求: io.netty.channel.ChannelInboundHandlerAdapter
- eventloop 事件循环: io.netty.channel.nio.NioEventLoopGroup
- bootstrap 启动服务: io.netty.bootstrap.ServerBootstrap。`b.bindPort(port).sync()`
- channel ?: io.netty.channel.socket.nio.NioServerSocketChannel
- channelInitializer: io.netty.channel.ChannelInitializer

java.nio.channel: https://www.baeldung.com/java-nio-2-async-channels

SingleThreadEventExecutor::execute
    - runAllTasks
    - takeTask
    - pollTask

NioEventLoop:
    - 生成 selectedKeys: openSelector
    - SelectorProvider provider 是内部的 socket selector

NioEventLoopGroup 构造函数(MultithreadEventExecutorGroup)中会调用 NioEventLoopGroup::newChild 创建 NioEventLoop
NioEventLoopGroup extends MultithreadEventLoopGroup extends MultithreadEventExecutorGroup
NioServerSocketChannel::bind -> DefaultChannelPipeline::bind
NioEventLoopGroup::next实现: MultithreadEventExecutorGroup::chooser 负责从 children 中选出需要执行的 NioEventLoop

NioServerSocketChannel::doBind 绑定套接字
从 NioServerSocketChannel::doReadMessages 往上溯源

## java

AccessController.doPrivileged: https://stackoverflow.com/questions/2233761/when-should-accesscontroller-doprivileged-be-used

## 有意思的代码

DefaultEventExecutorChooserFactory::isPowerOfTwo
