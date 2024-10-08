# Mockito

大部分情况下，我们并不需要手动实现 mock 对象。
利用 java 的 mockito 框架，可以方便的模拟对象以及监测对象行为:

1. mock. 凭空创建指定类型的对象，定制每个方法的行为。并进行检测。
2. spy. 基于已有对象，改变其部分方法行为。并进行监测。
3. verify. 断言 mock 对象行为是否符合预期。

## mock

mock 允许我们凭空创建一个指定类型的对象。

```java
import static org.mockito.Mockito.*;

// 创建 mock 对象
List<String> mockedList = mock(List.class);

// 使用 mock 对象
mockedList.add("one");
mockedList.clear();

// 断言mock对象的 add/clear 方法被调用过。
verify(mockedList).add("one");
verify(mockedList).clear();
```

1. mockedList 拥有 List 所有方法吗? 是的
2. `mockedList.add("one")` 执行之后，mockedList 中真的存在 `"one"` 这个元素吗?
   不是, mockedList 只是实现了 `List::add` 方法，默认是空实现。
3. `verify(mockedList).add("one")` 做了什么? 
   可以理解为 mock 对象内部存在一个行为记录器: `List<Action> actions`,
   当执行 `mockedList.add("one")` 时，会增加一条记录: `actions.add(new Action("add", args=new Args("one")))`,
   然后执行 `verify(mockedList).add("one")` 相当于检索 actions 中是否存在这条记录。

当然，我们可以定制 mock 对象的某些方法:

```java
List<String> mockedList = mock(List.class);

// 定制 get(0), 总是返回 "first"
when(mockedList.get(0)).thenReturn("first");

Assertions.assertEquals("first", mockedList.get(0));
```

## spy

spy 几乎和 mock 功能一样，不过可以基于某个真实对象进一步 mock。

```java
// mock way
List<String> mockedList = mock(List.class);

// spy way
List<String> list = new ArrayList();
List<String> spyList = spy(list);

// 和 mock 一样，也可以定制方法行为:
when(spyList.get(0)).thenReturn("first");
```

## mock static

```java
class IpUtils {
    public static String tryGetLocalIp() {
        try {
            return InetAddress.getLocalHost().getHostAddress();
        } catch(UnknownHostException e) {
            return "";
        }
    }
}
```

模拟 ip 获取失败的情况:

```java
@Test
public void testGetIpFailed() {
    try (var mocked = Mockito.mockStatic(InetAddress.class)) {
        mocked.when(InetAddress::getLocalHost).thenThrow(UnknownHostException.class);

        Assertions.assertEquals("", IpUtils.tryGetLocalIp())
    }
}
```
