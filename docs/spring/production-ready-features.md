# spring 生产环境特性

最近在看 spring-boot 文档的 [Production-ready Features](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html#actuator) 一章，做一些记录。

所谓的生产环境特性，就是服务对外暴露监控、指标之类的。

这类 spring 功能全都封装在 `spring-actuator` 中，只需要引入
`org.springframework.boot:spring-boot-starter-actuator` 这个 starter 即可启用。

spring-actuator 中封装了很多这类监控工具。有一些不仅可以查看运行期状态，设置还支持通过 web/jmx 接口修改程序状态。

:::{hint}
文档中提到的配置，例如 `management.endpoints.web.base-path=/manage`
如果没有特殊说明，均是指 spring properties 配置，如 `application.properties` `application.yml`
:::

## Endpoints(监控点)

启用 spring-actuator 后，可以通过一个简单的例子来了解 spring 的指标监控: health.

假设我们有一个普通的 spring-webmvc 服务，服务端口是 8080，
通过访问接口可以直接查看 actuator 中的 health 状态:

```shell
~$ curl http://127.0.0.1:8080/actuator/health

{"status": "UP"}
```

返回结果表示服务正常.

这个简单的例子，涉及到了两个概念

1. Endpoint - 监控点

   spring 提供了多种监控指标种类，它们被成为 Endpoint， health 是其中一种。

   通过访问 `http://127.0.0.1:8080/actuator` 可以查看所有 Endpoint (实际上默认也只有 health，囧)

2. Exposing Endpoint - 暴露监控

   有了 Endpoint 之后，还要暴露到外面给人看，暴露方式最常用的两种是 web(刚才的例子)、 JMX。

   下面对这两个概念做更详细的解释

### 启用 Endpoint

Spring 包含的 Endpoint :

| ID               | 功能                                                                                           |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| auditevents      | 展示 AuditEventRepository 的审计信息.                                                          |
| beans            | 展示所有 Bean 信息                                                                             |
| caches           | 展示缓存信息                                                                                   |
| conditions       | spring @Condition 和 AutoConfiguration 的信息. 以及为什么条件满足/不满足                       |
| configprops      | 展示所有 @ConfigurationProperties.                                                             |
| env              | 显示程序环境变量                                                                               |
| flyway           | 显示所有已经生效的 Flyway 的数据库变更，需要 Flyway bean.                                      |
| health           | 程序健康信息                                                                                   |
| httptrace        | 展示 http 请求(默认最近 100 条). 需要 HttpTraceRepository bean.                                |
| info             | 显示应用程序信息.                                                                              |
| integrationgraph | 显示 Spring Integration 图. 依赖 spring-integration-core.                                      |
| loggers          | 显示、修改日志配置.                                                                            |
| liquibase        | 显示已经生效的 Liquibase 的数据库变更，需要 Liquibase bean.                                    |
| metrics          | 显示程序的所有指标                                                                             |
| mappings         | 显示 @RequestMapping web 路由                                                                  |
| quartz           | 显示 Quartz 定时任务的信息                                                                     |
| scheduledtasks   | 显示执行过的定时任务.                                                                          |
| sessions         | spring servlet web 程序中允许获取/删除用户 session                                             |
| shutdown         | 允许停止应用程序，此 Endpoint 默认禁用.                                                        |
| startup          | 显示 ApplicationStartup 收集的启动信息，可用于统计启动耗时。需配置 BufferingApplicationStartup |
| threaddump       | 显示所有线程信息。                                                                             |

还有一些 web 程序 (Spring MVC, Spring WebFlux, or Jersey)专用的 Endpoint (默认不启用)。

| ID         | 功能                                                                                     |
| ---------- | ---------------------------------------------------------------------------------------- |
| heapdump   | 将当前堆 dump 为文件并下载，对于 HotSpot, 返回 HPROF 文件格式. OpenJ9 JVM 返回 PHD 格式. |
| jolokia    | 将 JMX 通过 http 暴露出去(此功能对 WebFlux 程序不可用)，依赖 jolokia-core.               |
| logfile    | 返回日志文件内容，需要配置 logging.file.name 或者 logging.file.path.                     |
| prometheus | 暴露 Prometheus 指标，需要依赖 micrometer-registry-prometheus.                           |

这就是所有可用的 Endpoint。要手动启用、关闭某个 Endpoint，
可以通过配置 `management.endpoint.{id}.enabled`, 如关闭 health:

```ini
management.endpoint.health.enabled=false
```

默认情况下, 除 `shutdown` 以及 web 专用的 Endpoint 外，所有 Endpoint 都是启用的。如果希望默认全部关闭，可以设置
`management.endpoints.enabled-by-default=false`，例如，要设置默认全部关闭，并手动打开 health:

```ini
management.endpoints.enabled-by-default=false
management.endpoint.health.enabled=true
```

### 暴露 Endpoints

Spring 提供了两种暴露 Endpoints 的方式: web/jmx ，通过它们的 `include/exclude` 配置来决定每一种方式要暴露哪些 Endpoint。

例如要配置通过 jmx 暴露 health/info: `management.endpoints.jmx.exposure.include=health,info`.
也可以通过 `*` 来包含所有可用 Endpoint。

所有可用配置项如下:

| Property                                  | 默认值 |
| ----------------------------------------- | ------ |
| management.endpoints.jmx.exposure.exclude |
| management.endpoints.jmx.exposure.include | \*     |
| management.endpoints.web.exposure.exclude |
| management.endpoints.web.exposure.include | health |

:::{note}
Endpoint 要最终能对外看到, 需要 Endpoint 本身启用，并且这里设置为暴露，缺一不可。

例如 web 程序专用的四个 Endpoint 本身默认是不启用的，
即使这里设置 `*` 也还是不会暴露。
:::

:::{attention}

Endpoint 启用的配置是 `management.endpoint`

暴露 Endpoint 的配置项是 `management.endpoints`

:::

暴露 Endpoints 后，可以通过访问 url `/actuator/{id}` 来查看信息，
例如: `http://127.0.0.1:8080/actuator/health`

### 其他配置

#### Endpoints 缓存

actuator 状态接口可能很慢，(例如 `/actuator/beans` 就需要扫描所有 bean 并生成信息), 所以很多 Endpoint 自带缓存功能，
可以通过 `management.endpoint.{id}.cache.time-to-live` 来设置缓存时间。例如:

```properties
management.endpoint.beans.cache.time-to-live=10s
```

#### actuator 发现页(首页)

默认情况下，访问 `/actuator` 会展示所有可用的 Endpoint。

可以通过以下配置禁用 actuator 首页

```ini
management.endpoints.web.discovery.enabled=false
```

#### CORS

通过 `management.endpoints.web.cors.*` 可以配置 actuator 允许跨域请求。

```ini
management.endpoints.web.cors.allowed-origins=https://example.com
management.endpoints.web.cors.allowed-methods=GET,POST
```

## 自定义状态

### 自定义 Endpoint

自定义 Endpoint 只需要两步:

1. 使用 `@Endpoint` 注解，将 Bean 标记为 Endpoint
2. 使用 `@ReadOperation` 将某个方法标记为状态获取方法。

例如:

```java
@Endpoint
@Component
public class CustomEndpoint {

  @ReadOperation
  public CustomData getData() {
    return new CustomData("test", 5);
  }
}
// class CustomData{
//     final String name;
//     final Integer counter;
// }
```

访问这个 Endpoint 会返回 `{"name": "test", "counter": 5}`。

`@Endpoint` 注解的 Endpoint 可以用于 JMX 以及 web,
也可以使用仅 JMX 可用的 `@JmxEndpoint` 或者仅 Web 可用的 `@WebEndpoint`.

也可以通过 `@EndpointWebExtension` 和 `@EndpointJmxExtension` 来编写用于特定场景的 Endpoint，以便可以使用一些特有的特性。(todo aochujie, 不是很明白?)

:::{note}
从技术角度讲，自定义状态也可以通过 @Controller 来实现为 http 接口。

不过这会导致无法在 JMX 中使用。而且如果更换 web 框架，也会导致无法使用。兼容性不好。

也可以通过 `@WriteOperation` 定义可以修改状态的 Endpoint。

```{code-block} java
:emphasize-lines: 10-14

@Endpoint
@Component
public class CustomEndpoint {

  @ReadOperation
  public CustomData getData() {
    return new CustomData("test", 5);
  }

  @WriteOperation
  public CustomData updateData(String name, int counter) {
    CustomData data = new CustomData(name, counter);
    // update data ...
  }
}
```

:::{tip}
由于无法确定 endpoint 会暴露在在什么地方，有些暴露方式可能并不支持传递复杂参数，所以修改时的传参只支持基础数据类型。
不支持复杂(嵌套)数据类型
:::

### health - 健康检查

#### health 配置

默认情况下，访问 `/actuator/health` 只会显示最简单的 `{"status": "UP"}`，要控制是否显示更详细的信息，
可以配置 `management.endpoint.health.show-details` 和 `management.endpoint.health.show-components` 为下面几种取值:

| value           | 描述                                                                                                           |
| --------------- | -------------------------------------------------------------------------------------------------------------- |
| never           | (默认值) 不显示详情                                                                                            |
| when-authorized | 对认证用户显示详情，通过 `management.endpoint.health.roles` 额外配置仅对指定用户显示，需要依赖 spring-securety |
| always          | 总是显示详情                                                                                                   |

#### 自定义 Health

actuator 健康信息是由 `HealthContributor` 产生的，把它们注册到 `HealthContributorRegistry` 即可使用，要自定义 `HealthContributor`， 有两种方法

1. 实现 `HealthContributor` Bean，它会在启动时自动注册进去。
2. 获取 `HealthContributorRegistry` Bean, 将实现的 `HealthContributor` new 出来注册进去，一般用于运行期动态调整。

再来看看 `HealthContributor`，会发现它其实是个空接口，一般使用的时下面细分的两个接口:

1. HealthIndicator

   需要实现其 `Health health()` 接口，返回健康信息。形式就像之前提到的 `{"status": "UP"}`

2. CompositeHealthContributor

   组合其他 `HealthContributor` 的接口，其形式是嵌套的健康检查信息。
   其作用就是把同类的健康信息组合到一起，整体形成树状结构。

   `CompositeHealthContributor` 不需要自己实现，直接调用 `CompositeHealthContributor.fromMap(Map<String, HealthContributor>)` 即可。

对于 webflux, 也可以使用 `ReactiveHealthContributer` `ReactiveHealthIndicator` `CompositeReactiveHealthContributor`

#### StatusAggregator

Actuator Health 最终状态是通过 StatusAggregator 实现的，它将下面的 HealthIndicator 返回的状态进行排序，并把能代表整体状态的那个子状态放在第一个，
约定以第一个作为最终状态。

默认的实现是 `SimpleStatusAggregator`, 其排序方式是优先把 DOWN 放前面，UP 放后面，这样的话，只要有一个是 DOWN，整体就认为不健康了。

可以通过 `management.endpoint.health.status.orde` 配置为指定的排序:

```ini
management.endpoint.health.status.order=fatal,down,out-of-service,unknown,up
```

也可以自己实现 StatusAggregator.

:::{tips}
默认的 health status 有 UNKNOWN/UP/DOWN/OUT_OF_SERVICE,
见 `org.springframework.boot.actuate.health.Status`
:::

#### 默认提供的健康检查

| key           | 实现 Bean                        | 描述                              |
| ------------- | -------------------------------- | --------------------------------- |
| cassandra     | CassandraDriverHealthIndicator   | 检查 Cassandra 数据库是否已启动   |
| couchbase     | CouchbaseHealthIndicator         | 检查 Couchbase 集群是否已启动     |
| db            | DataSourceHealthIndicator        | 检查 DataSource 连接是否可用      |
| diskspace     | DiskSpaceHealthIndicator         | 检查磁盘空间是否不足              |
| elasticsearch | ElasticsearchRestHealthIndicator | 检查 Elasticsearch 集群是否已启动 |
| hazelcast     | HazelcastHealthIndicator         | 检查 Hazelcast 服务是否已启动     |
| influxdb      | InfluxDbHealthIndicator          | 检查 InfluxDB 服务是否已启动      |
| jms           | JmsHealthIndicator               | 检查 JMS 代理是否已启动           |
| ldap          | LdapHealthIndicator              | 检查 LDAP 服务是否已启动          |
| mail          | MailHealthIndicator              | 检查邮件服务器是否已启动          |
| mongo         | MongoHealthIndicator             | 检查 Mongo 数据库是否已启动       |
| neo4j         | Neo4jHealthIndicator             | 检查 Neo4j 数据库是否已启动       |
| ping          | PingHealthIndicator              | 始终返回 UP                       |
| rabbit        | RabbitHealthIndicator            | 检查 Rabbit 服务是否已启动        |
| redis         | RedisHealthIndicator             | 检查 Redis 服务是否已启动         |

默认提供的响应式(Reactive)健康检查：

key | 实现 Bean | 描述
cassandra | CassandraDriverReactiveHealthIndicator | 检查 Cassandra 数据库是否已连接
couchbase | CouchbaseReactiveHealthIndicator | 检查 Couchbase 集群是否已连接
elasticsearch | ElasticsearchReactiveHealthIndicator | 检查 Elasticsearch 集群是否已连接
mongo | MongoReactiveHealthIndicator | 检查 Mongo 数据库是否已连接
neo4j | Neo4jReactiveHealthIndicator | 检查 Neo4j 数据库是否已连接
redis | RedisReactiveHealthIndicator | 检查 Redis 服务是否已连接

#### DataSource Health(TODO)

里面提到标准 data source 和路由 data source. 感觉和我平常用的 data source 不太一样。

这一块我不是很懂。。。

### 程序信息

这些信息，一般是程序静态信息。类似于一般软件上菜单上的 `关于本软件` 的弹出框。

默认提供的程序信息有:

| ID    | 实现 Bean                  | 描述                                     | 需要的依赖                                            |
| ----- | -------------------------- | ---------------------------------------- | ----------------------------------------------------- |
| build | BuildInfoContributor       | 显示构建信息                             | 需要包含 META-INF/build-info.properties resource 文件 |
| env   | EnvironmentInfoContributor | 显示所有 `info.` 开头的 Environment 属性 | 无                                                    |
| git   | GitInfoContributor         | git 信息                                 | 需要包含 git.properties resource 文件                 |
| java  | JavaInfoContributor        | java 运行时(jre) 的信息                  | 无                                                    |
| os    | OsInfoContributor          | 显示操作系统信息                         | 无                                                    |

:::{attention}
Environment 属性不是环境变量，而是 Spring 的 Environment，包含了环境变量、properties、`-D`选项等
:::

默认启用 build/git， 要启用其他信息, 配置 `management.info.{id}.enabled` ，以 os 信息为例，配置:

```ini
management.info.os.enabled=true
```

要配置所有信息默认开启，可配置 `management.info.defaults.enabled=true`

### 自定义信息

通过实现 `InfoContributor` Bean 可以自定义信息。

```java
import org.springframework.boot.actuate.info.Info;
import org.springframework.boot.actuate.info.InfoContributor;

@Component
public class MyInfoContributor implements InfoContributor {

  @Override
  public void contribute(Info.Builder builder) {
    builder.withDetail("example", Collections.singletonMap("key", "value"));
  }
}
```

获取信息的运行效果:

```json
{
  "example": {
    "key": "value"
  }
}
```

## http management 配置

### 配置 actuator 路径

actuator url 默认是 `/actuator` 开头，例如要修改为 `/manage` 可以配置:

```ini
management.endpoints.web.base-path=/manage
```

配置后，actuator 发现页，Endpoint 页面均会随此配置而变更。

如果要单独配置配置某个 Endpoint 路径，可以配置 `management.endpoints.web.path-mapping.{id}`。
例如要将 `/actuator/health` 修改为 `/actuator/healthcheck` :

```ini
management.endpoints.web.path-mapping.health=healthcheck
```

这两个配置可以结合使用，例如要把 `/actuator/health` 修改为 `/healthcheck`:

```ini
management.endpoints.web.base-path=/
management.endpoints.web.path-mapping.health=healthcheck
```

:::{attention}
由于技术原因，防止路由冲突，`management.endpoints.web.base-path` 配置为 `/` 后会自动禁用发现页
:::

### 配置监听端口和地址

```ini
management.server.port=8081
management.server.address=127.0.0.1
```

这个配置可以使 actuator 端口和 http 端口分离，防止互相影响(或者出于权限方面的考虑)

`management.server.port=-1` 会禁用 web Endpoint。
等价于配置 `management.endpoints.web.exposure.exclude=*`

## jmx management 配置

JMX 默认不启用，需要配置 `spring.jmx.enabled=true` 启用。

默认情况下，Spring 会自己生成一个 `MBeanServer` Bean。
不过，如果应用程序中有定义的话，就会直接用程序定义的。
然后，所有拥有 JMX 注解的 bean 都会注册进这个 `MBeanServer`，
JMX 注解包括: `@ManagedResource`, `@ManagedAttribute`, `@ManagedOperation` 。

如果要控制 JMX Endpoint 注册流程，可以关注 `JmxAutoConfiguration` `EndpointObjectNamingFactory`

MBean 会根据 Endpoint 的 id 生成名字,例如 `org.springframework.boot:type=Endpoint,name=Health`.
设置 `spring.jmx.unique-names=true` 可以使其生成唯一的名字，
通常用于程序中有多个 ApplicationContext 以避免命名冲突的情况。

通过 `management.endpoints.jmx.domain=com.example.myapp` 设置仅暴露某些 domain 下的 Endpoint。

`management.endpoints.jmx.exposure.exclude=*` 禁用所有 Endpoint

### Jolokia

Jolokia 是一个将 JMX 桥接到 http 的工具。通过下面的步骤启用

1. 引入依赖 `org.jolokia:jolokia-core`
2. 配置 `management.endpoints.web.exposure.include` 包含 `jolokia`，或者设置为 `*`

然后就可以通过 url `/actuator/jolokia` 访问 JMX 了。

jolokia 本身支持很多配置，这些配置统一放在 `management.endpoint.jolokia.config.*`,
例如 `management.endpoint.jolokia.config.debug=true` .

项目只要有 jolokia jar，spring 就会检测到进行自动配置。有时候项目其他地方依赖了 jolokia，但是又不想让 spring 用，
可以配置 `management.endpoint.jolokia.enabled=false`

## 日志

访问 `/actuator/loggers` 查看所有日志信息。

POST `{"configuredLevel": "DEBUG"}` 可以修改某个 logger 的日志等级。

## 指标

actuator 的指标收集主要依赖了 [Micrometer](https://micrometer.io/), Micrometer 是一个指标门面库，支持很多种监控系统。

这里主要介绍 Prometheus。

添加 micrometer 的 Prometheus 依赖: `io.micrometer:micrometer-registry-prometheus:1.11.2`， 即可启用。
可以配置 `management.metrics.export.prometheus.enabled=false` 禁用。启用后，访问 `/actuator/prometheus` 访问 prometheus 指标。

### 支持的指标

- JVM 指标
  - 各代内存和 buffer 详情
  - GC 相关的统计数据
  - 线程信息
  - 加载和卸载 Class 的数量
- 系统指标

  这部分包括 `system.` `process.` `disk.` 开头的一系列指标

  - CPU 指标
  - 文件描述符指标
  - 启动时间
  - 磁盘用量

- 进程启动时间指标
  - application.started.time: 启动耗时
  - application.ready.time: 启动并配置好知道能够正常服务的这段耗时
- 日志指标
- ... ...

### 注册自定义指标

```java
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import org.springframework.stereotype.Component;

@Component
public class MyBean {
  private final Dictionary dictionary;

  public MyBean(MeterRegistry registry) {
    this.dictionary = Dictionary.load();
    registry.gauge(
      "dictionary.size",
      Tags.empty(),
      this.dictionary.getWords().size()
    );
  }
}
```

如果指标依赖了其他 Bean，推荐使用 MeterBinder 进行注册:

```java
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.binder.MeterBinder;
import org.springframework.context.annotation.Bean;

public class MyMeterBinderConfiguration {

  @Bean
  public MeterBinder queueSize(Queue queue) {
    return registry ->
      Gauge.builder("queueSize", queue::size).register(registry);
  }
}
```

### 自定义指标信息

对于已经配置好的 Meter 实例，可以实现 io.micrometer.core.instrument.config.MeterFilter 来对其进行后期修改。

例如，对于 ID 是 com.example 开头的指标，下面的代码会把 mytag.regin 的 tag 改成 mytag.area:

```java
import io.micrometer.core.instrument.config.MeterFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration(proxyBeanMethods = false)
public class MyMetricsFilterConfiguration {

  @Bean
  public MeterFilter renameRegionTagMeterFilter() {
    return MeterFilter.renameTag("com.example", "mytag.region", "mytag.area");
  }
}
```

通过配置 `management.metrics.enable.*` 禁用某个前缀的所有指标.
例如禁用 `example.remote` 前缀的所有指标 `management.metrics.enable.example.remote=false`

## 审计信息

如果项目依赖了 Spring Security, 就可以发布一些审计事件。
然后应用程序中实现 AuditEventRepository 即可。

Spring Security 没怎么用过，就不深究了。

## http 请求记录

只需要实现一个 `HttpTraceRepository` Bean , 即可拥有 http 请求记录的功能。

Spring 默认提供了一个 `InMemoryHttpTraceRepository` 的简单实现，
需要在 Configuration 中 new 出来。会记录最近的 100 条请求。

`InMemoryHttpTraceRepository` 一般用于开发调试，生产环境推荐使用一些成熟的中间件，比如 Zipkin 或者 Spring Cloud Sleuth.

## 进程监控

linux 上，有些服务会根据 linux 约定生成 `.pid`，里面只需要写一个进程 id。
一些监控程序就会根据这个约定读取 pid 获取进程 id 进行监控。

Spring 也提供了自动生成当前进程 `pid` 的功能，不过默认没有启用。

对于 Spring 来说，它们其实是一类 _启动时自动生成特定文件_ 的一类功能，提供了两个实现(也可以自定义实现):

- ApplicationPidFileWriter: 在当前目录创建 application.pid 文件，里面包含当前进程 id
- WebServerPortFileWriter: 在当前目录创建 application.port, 里面包含当前服务暴露的端口。

要启用这两个功能，可以配置 `META-INF/spring.factories` 文件:

```ini
org.springframework.context.ApplicationListener= \
  org.springframework.boot.context.ApplicationPidFileWriter,\
  org.springframework.boot.web.context.WebServerPortFileWriter
```

或者手动调用 `SpringApplication.addListeners(...)`, 把上面两个(或自定义实现的)Writer 对象传进去。
