# JUnit 单元测试

JUnit 是 java 技术栈使用的主流单元测试框架。对于spring项目，只需要引入 _spring-boot-test-starter_ 就可以了。

```kotlin
// build.gradle.kts
// 通过 spring starter 引入 java 常用测试套件
dependencies {
    // ... ...
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

// 使用 junit 进行单元测试
tasks.withType<Test> {
    useJUnitPlatform()
}
```

## JUnit 入门

比如我们有下面的计算器代码

```kotlin
// src/main/java/com/example/Calc.kt
package com.example

class Calc {
    fun add(a: Int, b: Int): Int {
        return a + b
    }
}
```

下面的代码是单元测试代码，测试 `Calc::add` 方法的行为是否符合预期.

```kotlin
// src/test/java/com/example/CalcTests.kt
package com.example

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class CalcTests {
    private val calc = Calc()

    // 注意，测试方法需要添加 @Test 注解
    @Test
    fun testAdd() {
        val ret = calc.add(1, 2)
        // 预期返回值是 3
        Assertions.assertEquals(3, ret)
    }
}
```

上面的案例，介绍了 JUnit 两个重要概念:

1. `@Test`: 测试函数
2. `Assertions`: 判断程序行为是否符合预期的测试用例

## JUnit 测试生命周期

- `@BeforeAll`: 测试 class 执行前的初始化动作
- `@AfterAll`: 测试 class 中所有函数执行完后的销毁动作
- `@BeforeEach`: 每个测试函数执行前的初始化动作
- `@AfterEach`: 每个测试函数执行后的销毁动作

```kotlin
package com.example

import org.junit.jupiter.api.*

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class CalcTests {
    private val calc = Calc()

    @BeforeAll
    fun beforeAll() { println("## BeforeAll") }

    @BeforeEach()
    fun beforeEach() { println("#### BeforeEach") }

    @AfterEach()
    fun afterEach() { println("#### AfterEach") }

    @AfterAll
    fun afterAll() { println("## AfterAll") }

    @Test
    fun testAdd() { println("###### start testAdd1") }
    @Test
    fun testAdd2() { println("###### start testAdd2") }
}
```

上面的函数会打印:

```text
## BeforeAll

#### BeforeEach
###### start testAdd1
#### AfterEach

#### BeforeEach
###### start testAdd2
#### AfterEach

## AfterAll
```
