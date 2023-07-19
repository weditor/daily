# 可变&不可变

## 前言

java 声明的变量: `String name = "Tom"`

kotlin 声明的变量: `var name = "Tom"`

java 支持声明不可变的变量: `final String name = "Tom"`.

kotlin 简化了不可变的变量: `val name = "Tom"`

## 变化导致的陷阱

假设有一个 java User 类:

```java
public class User {
  private String name;
  private Integer age;

  public User(String name, Integer age) {
    this.name = name;
    this.age = age;
  }

  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public Integer getAge() {
    return age;
  }

  public void setAge(Integer name) {
    this.age = age;
  }
}
```

这个类很简单，提供了两个成员，都支持 get/set。然后我们使用的时候:

```java

void myfunction() {
    User user = new User("jack", 20);
    someThirdFunction(User);
    System.out.println(user.age); // what it is?
}
```

对于这样一个简单函数，如果想知道 user.age 能打印出来什么，都必须深入第三方函数看看有没有人修改过。
也许可以通过全局查找 set 函数等方法去定位，但是对于大型项目，这些方法作用都有限。

## 消除变化

但是...如果 User 类不提供 set 方法，或者更激进一些，所有类都不提供 set 方法，我们的大部分函数就能保证没人修改了吗?
后续维护者就可以专心于某一个函数而不必关注上下文。

所以，有代码洁癖的码农会在代码中尽可能减少变化，例如这样:

```java
public final class User {
  private final String name;
  private final Integer age;

  public User(String name, Integer age) {
    this.name = name;
    this.age = age;
  }

  public String getName() {
    return name;
  }

  public Integer getAge() {
    return age;
  }
}
```

1. 只提供 get 方法
2. 尽量给类、成员加上 final 修饰

这个类就实现了不可变的特性，一旦创建，正常途径就不再有更改的可能。

这个类可以简化一下，因为 name/age 已经是 final 了，本身不可以更改，就不必写成 private 了:

```java
public final class User {
  public final String name;
  public final Integer age;

  public User(String name, Integer age) {
    this.name = name;
    this.age = age;
  }
}
```

最终，它就变成了 kotlin 中的 data class;

```kotlin
data class User(val name: String, val age: String)
```

另外 data class 还自带了 equal、hashCode、toString 等函数。

java 在 jdk15 新版本中也增加了 record class，与 data class 类似。
不过由于历史包袱，默认不可变的概念是别指望了。

## 可变 vs. 不可变

很多新兴编程语言都开始吸收函数式编程的数据不可变性的思想。kotlin 在这方面也抄了一些。
不过 kotlin 并不是一个极端函数式编程语言，也仅仅是 _偏向_ 数据不可变而已。这些偏好体现在:

1. 类默认 final，除非显式加上 open
2. 成员变量、函数默认 final，除非显式加上 open
3. 集合类型默认不可变，除非加上 mutable 前缀，如 `mutableListOf(...)`
4. 鼓励使用 val 而不是 var.

数据的不可变性，对于写出好维护的代码至关重要。
kotlin 的非空概念 + 不可变性，是提升项目可维护性的神器。

## WhatIf

**问题 1**: 如果都声明为不可变 class，想修改的话怎么办?

update = delete + create. 创建一个新的，销毁旧的。例如修改年龄 `User user2 = new User(oldUser.name, 18)`。

kotlin 对 data class 提供了 copy 语法糖，可以改写成等价的代码: `val user2 = user.copy(age=18)`

至于性能问题, 没有确切的 profile 证据，实在是没必要在这种地方抠性能。
人工维护成本大于机器运行成本。

**问题 2**: 所有字段都声明为 public, 后期需求变更，那个字段变成了只能函数计算怎么办?

kotlin 支持 property 函数

```kotlin
class User(val age: Int, val firstName: String, val lastName: String) {
    val name: String
        get() = "$firstName $lastName"
}
```

**问题 3**: 下面的代码，由于 name 的构造过于复杂，导致我们不得不先声明一个临时变量，然后修改它，怎么避免这个临时变量?

```kotlin
var name = ""
if (...) {
    name = "A"
}
else if (...) {
    name = "B"
} else {
    name = "C"
}
```

kotlin 支持的一些变种赋值语法可以解决这类问题:

```kotlin
// 情境 1
val name = if (...) {
    "A"
} else {
    "B"
}

// 情境 2
val name = run {
    var tmpName = ""
    // 这里一些很复杂的代码
    // 构造 tmpName 然后返回
    tmpName
}
```

## 总结

两个原则:

1. 保证所有变量都是 val. 凡是遇到 var 都要慎重评估是否真的有需要。
2. 能用 data class 就别用 class。
