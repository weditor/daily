# spring 生产环境特性

最近在看 spring-boot 文档的 [Production-ready Features](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html#actuator) 一章，做一些记录。

所谓的生产环境特性，就是服务对外暴露监控、指标之类的。
spring 自带封装了很多这类监控指标，甚至可以通过接口对内部状态进行控制。

这类 spring 功能全都封装在 `spring-actuator` 中，只需要引入
`org.springframework.boot:spring-boot-starter-actuator` 这个 starter 即可启用。

## Endpoints(监控点)

启用 spring-actuator 后，可以通过一个组简单的例子来了解 spring 的指标监控: health.

例如一个普通的 spring-webmvc 服务，暴露了 8080 端口， 就可以直接访问:

```shell
~$ curl http://127.0.0.1:8080/actuator/health

{"status": "UP"}
```

返回结果表示服务正常.

这个简单的例子，涉及到了两个概念

- Endpoint - 监控点

  spring 提供了多种监控指标种类，它们被成为 Endpoint， health 是其中一种。

  通过访问 `http://127.0.0.1:8080/actuator` 可以查看所有 Endpoint (实际上默认也只有 health，囧)

- Exposing Endpoint - 暴露监控

  有了 Endpoint 之后，还要暴露到外面给人看，暴露方式最常用的两种是 web(刚才的例子)、 JMX。

### 启用 Endpoint

| ID               | Description                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| auditevents      | 展示 AuditEventRepository 的审核信息(用户认证).                                                |
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

| ID         | Description                                                                                  |
| ---------- | -------------------------------------------------------------------------------------------- |
| heapdump   | 将当前堆 dump 为文件并下载，对于 HotSpot, 返回 HPROF 文件格式. OpenJ9 JVM 返回 PHD 文件格式. |
| jolokia    | 将 JMX 通过 http 暴露出去(此功能对 WebFlux 程序不可用)，依赖 jolokia-core.                   |
| logfile    | 返回日志文件内容，需要配置 logging.file.name 或者 logging.file.path.                         |
| prometheus | 暴露 Prometheus 指标，需要依赖 micrometer-registry-prometheus.                               |

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

### Endpoints 其他配置

## 自定义 Endpoint

## 自定义健康检查

## 程序运行时信息

## http management 配置

## jmx management 配置

## 指标

## 认证信息

## http 请求记录

## 进程监控
