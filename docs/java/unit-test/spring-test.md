# Spring Test

## 测试后端服务

spring 服务的单元测试和普通 java 代码单元测试差不多，不过需要注意:

1. Spring 所有组件基于 ApplicationContext。需要注意 Context 管理
2. Spring 后端服务需要注意其启动端口号。

下面是一个简单的案例:

```java
package com.example;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import org.junit.jupiter.api.Assertions;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;

import java.io.IOException;

/** spring web 测试, 使用随机端口启动 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class LivenessTest {
    /** 通过 LocalServerPort 将启动端口号注入进来 */
    @LocalServerPort
    private Long port;

    public void testLiveness() throws IOException {
        // 尝试请求 liveness 接口, 断言其返回 http 200
        var url = "http://localhost:" + port + "/liveness";

        var client = new OkHttpClient();
        var request = new Request.Builder().url(url).build();
        var call = client.newCall(request);
        var response = call.execute();
        Assertions.assertEquals(200, response.code());
    }
}

```

上面的代码需要注意:

1. class 上增加 `@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)` 启动后端服务.
   随后便可以通过 http client 测试服务接口
2. 使用随机端口启动后，通过 `@LocalServerPort` 得到端口号。

:::{note}
如果不需要测试后端 http 接口，也可以将 `SpringBootTest::webEnvironment` 设置为其他值。
使其不通过端口号启动。
:::

这种情况下，会自动寻找代码中的 `@SpringBootApplication` 启动入口, 这种情况下和服务正常启动的流程几乎一样。
这些细微差别体现在，单元测试情况下，很多周边的东西不会自动配置，例如 Scheduler, Metrics, Caching 等，
需要手动添加 `@AutoConfigureXXX` 注解，下面是启用指标收集的单元测试案例:

```java
/** 启用指标 */
@AutoConfigureMetrics
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class UserServiceTest {
    // ... ...
}
```

## 使用 Bean

如果需要在测试过程中使用 Bean，可以通过 `@Autowired` 注入进来:

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class LivenessTest {
    /** 方式一: 属性注入 */
    @Autowired UserService userService;

    /** 方式二: 参数注入 */
    @Test
    public void testForRepository(UserRepository userRepository) {
        // 使用 Bean
        userService.saveUser(new User(...));
        // ... ...
    }
}
```

## Mock/Spy Bean

如果需要替换 Context 中的某个 Bean，可以使用 `@MockBean` `@SpyBean` 注解。
这个 Mock 动作是临时的，仅仅对当前函数有效。

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class MyTests {
    @Autowired private Reverser reverser;
    @MockBean private RemoteService remoteService;

    @Test
    void exampleTest() {
        given(this.remoteService.getValue()).willReturn("spring");
        // Calls injected RemoteService
        String reverse = this.reverser.getReverseValue();
        assertThat(reverse).isEqualTo("gnirps");
    }
}
```

`@MockBean` 会将 ApplicationContext 中的 RemoteService 替换为 mockito `mock` 生成的对象。

如果要基于现有对象进行mock，可以使用 `@SpyBean`, 从而实现最小化修改。

## ReflectionTestUtils

spring test 提供了一个强大的 ReflectionTestUtils 辅助工具。
借助 ReflectionTestUtils 可以直接修改对象中的任意字段。例如:

1. `ReflectionTestUtils.getField(myObj, "name")`. 获取 `myObj.name`
2. `ReflectionTestUtils.setField(myObj, "name", "value")`. 等价于 `myObj.name = "value"`
3. `ReflectionTestUtils.invokeMethod(myObj, "someFunction")`, 等价于 `myObj.someFunction()`

支持对 private 字段、函数进行操作。

所以，也可以通过 ReflectionTestUtils 将某些属性替换为我们 mock 的对象:

```java
@Test
public void testUserService(@Autowired UserService userService) {
    ReflectionTestUtils.setField(userService, "userRepository", new MockUserRepository());
}
```

不过这个替换是永久的，用完记得恢复现场。

## Context 管理

一般来说，整个测试复用一个 ApplicationContext 就可以了。
每次启动一个新 Context 可能很耗时，但是，有需要的话，也可以通过不同的配置启动多个 Context。

```java
// 启用 test/resources/application-one.properties
@ActiveProfiles("one")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class OneTests {
    // ... ...
}

// 启用 test/resources/application-two.properties
@ActiveProfiles("two")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class TwoTests {
    // ... ...
}
```

