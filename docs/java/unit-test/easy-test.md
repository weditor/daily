# 大型程序的构建与测试

现实中的程序，往往依赖关系错综复杂。

```java
public class UserService {
    @Autowired
    private UserRepository userRepository;

    public User findUser(String userId) {
        var user = userRepository.findById(userId)
        if (this.isUserValid(user)) {
            return user;
        }
        return null;
    }
    private boolean isUserValid(User user) {
        return user.isValid != null && user.isValid);
    }
}
```

上面的代码是一个简单的模块依赖的案例。要对这份代码进行单元测试，存在两个难点:

1. `UserService` 依赖 `UserRepository`。为了实例化 UserService, 我们必须先实例化 UserRepository。
   更进一步讲，UserRepository 可能也有各种依赖，这种连锁依赖，最终可能导致我们不得不把所有对象都实例化出来。
2. `UserService` 使用了 `@Autowired` 注入。即便我们已经有了 `UserRepository` 也无法通过常规手段 new 一个 `UserService`.

## 解决 Autowired 注入问题

@Autowired 注入问题比较好解决，我们只需要更改成 spring 推荐的构造函数注入方式即可:

```diff
    public class UserService {
-       @Autowired
        private final UserRepository userRepository;

+       public UserService(UserRepository userRepository) {
+           this.userRepository = userRepository;
+       }

        ... ...
    }
```

这种方式不需要显式添加 `@Autowired` 注解，并且不影响我们手动实例化。

## 解决依赖链问题

模块化做得好的代码，一定是对单元测试友好的。依赖链的问题需要通过接口抽象来解决。

在上个案例中，`UserService` 依赖 `UserRepository`。为了避免依赖链，我们可以将 `UserRepository` 抽象为接口 `IUserRepository`:

```{mermaid}
classDiagram

    namespace repository {
        class MongoUserRepository
        class TestUserRepository
        class IUserRepository {
            + findById(String)
        }
    }
    class UserService { }

    AnotherDependency --* MongoUserRepository
    SomeOtherDependency --* MongoUserRepository
    MongoUserRepository ..|> IUserRepository
    TestUserRepository ..|> IUserRepository
    IUserRepository --* UserService
```

在正式环境中，照常使用 `MongoUserRepository`.
在单元测试的时候，就使用模拟出来的 `TestUserRepository`:

```java
public class TestUserRepository implements IUserRepository {
    @Override
    public User findById(String userId) {
        return new User(userId);
    }
}

class UserTest {
    UserService userService = 
        new UserService(new TestUserRepository);

    @Test
    public void testUserService() {
        // .... ...
    }
}
```

UserService 也可能被其他 class 依赖(可能是 `UserController`), 这种情况下，为了测试 `UserController`, 可以按照同样的方法将 UserService 抽象为接口。

当然这也不是绝对的，在 UserController/UserService/UserRepository 这条依赖链中，也可以选择将他们当做一组模块，只抽象 UserRepository，给 UserController 提供真实的 UserService, 这取决于业务中如何划分模块的边界:

```java
var repository = new TestUserRepository();
var userService = new UserService(repository);
var userController = new UserController(userService);
```

通过模块划分与接口抽象，就可以将一些很难构造的对象隔离出来，伪造一个假的对象进行替换，这种方法称为 Mock。
