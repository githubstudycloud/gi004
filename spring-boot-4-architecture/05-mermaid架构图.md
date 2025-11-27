# Spring Boot 4.0 Mermaid 架构图

> 以下架构图使用 Mermaid 语法，可在支持 Mermaid 的 Markdown 预览器中渲染

## 一、整体架构图

```mermaid
graph TB
    subgraph Application["应用层"]
        App[Spring Boot Application]
        Config[Configuration]
        CustomBeans[Custom Beans]
    end

    subgraph AutoConfig["自动配置层 (70+ 模块)"]
        WebMVC[spring-boot-webmvc]
        WebFlux[spring-boot-webflux]
        DataJPA[spring-boot-data-jpa]
        Security[spring-boot-security]
        Actuator[spring-boot-actuator]
        OpenTel[spring-boot-opentelemetry]
        Kafka[spring-boot-kafka]
        Redis[spring-boot-data-redis]
    end

    subgraph Core["Spring Framework 7.0 核心"]
        IoC[IoC Container]
        DI[Dependency Injection]
        AOP[AOP]
        SpEL[SpEL]
        TX[Transaction Management]
    end

    subgraph Infrastructure["基础设施"]
        JVM[JVM Runtime<br/>Java 17-25]
        Jakarta[Jakarta EE 11]
        DB[(Database)]
        Cache[(Cache)]
        MQ[Message Queue]
    end

    App --> AutoConfig
    AutoConfig --> Core
    Core --> Infrastructure

    style Application fill:#e1f5fe
    style AutoConfig fill:#fff3e0
    style Core fill:#e8f5e9
    style Infrastructure fill:#fce4ec
```

## 二、四层架构图

```mermaid
graph TB
    subgraph Presentation["表现层 Presentation Layer"]
        direction LR
        REST["@RestController<br/>REST API"]
        WS["WebSocket<br/>Handler"]
        GraphQL["GraphQL<br/>Controller"]
        View["Thymeleaf<br/>View"]
    end

    subgraph Business["业务层 Business Layer"]
        direction LR
        Service["@Service<br/>业务逻辑"]
        TX["@Transactional<br/>事务管理"]
        Auth["@PreAuthorize<br/>权限检查"]
        Event["Event<br/>Publisher"]
    end

    subgraph Persistence["持久层 Persistence Layer"]
        direction LR
        Repo["@Repository<br/>Spring Data"]
        Cache["Cache<br/>Manager"]
        Query["Query<br/>Builder"]
    end

    subgraph Database["数据库层 Database Layer"]
        direction LR
        RDBMS[(PostgreSQL<br/>MySQL)]
        NoSQL[(MongoDB<br/>Redis)]
        Search[(Elasticsearch)]
    end

    Presentation --> Business
    Business --> Persistence
    Persistence --> Database

    style Presentation fill:#bbdefb
    style Business fill:#c8e6c9
    style Persistence fill:#fff9c4
    style Database fill:#ffccbc
```

## 三、模块化架构图

```mermaid
graph LR
    subgraph Starters["Starter POMs"]
        S1[spring-boot-starter-webmvc]
        S2[spring-boot-starter-data-jpa]
        S3[spring-boot-starter-security]
        S4[spring-boot-starter-actuator]
        S5[spring-boot-starter-kafka]
        S6[spring-boot-starter-opentelemetry]
    end

    subgraph Modules["Auto-Configure 模块"]
        M1[spring-boot-webmvc]
        M2[spring-boot-data-jpa]
        M3[spring-boot-security]
        M4[spring-boot-actuator]
        M5[spring-boot-kafka]
        M6[spring-boot-opentelemetry]
    end

    subgraph TestModules["Test 模块"]
        T1[spring-boot-webmvc-test]
        T2[spring-boot-data-jpa-test]
        T3[spring-boot-security-test]
        T4[spring-boot-actuator-test]
        T5[spring-boot-kafka-test]
    end

    S1 --> M1
    S2 --> M2
    S3 --> M3
    S4 --> M4
    S5 --> M5
    S6 --> M6

    M1 -.-> T1
    M2 -.-> T2
    M3 -.-> T3
    M4 -.-> T4
    M5 -.-> T5

    style Starters fill:#e3f2fd
    style Modules fill:#f3e5f5
    style TestModules fill:#e8f5e9
```

## 四、请求处理流程图

```mermaid
sequenceDiagram
    participant Client
    participant Filter as Security Filter Chain
    participant Dispatcher as DispatcherServlet
    participant Controller as @RestController
    participant Service as @Service
    participant Repository as @Repository
    participant DB as Database

    Client->>Filter: HTTP Request
    Filter->>Filter: Authentication
    Filter->>Filter: Authorization
    Filter->>Dispatcher: Authenticated Request
    Dispatcher->>Controller: Route to Handler
    Controller->>Service: Business Logic
    Service->>Repository: Data Access
    Repository->>DB: Query
    DB-->>Repository: Result
    Repository-->>Service: Entity
    Service-->>Controller: DTO
    Controller-->>Dispatcher: Response Body
    Dispatcher-->>Filter: HTTP Response
    Filter-->>Client: JSON Response
```

## 五、组件依赖关系图

```mermaid
graph TB
    App["Your Application<br/>@SpringBootApplication"]

    subgraph Boot4["Spring Boot 4.0"]
        Starter1["spring-boot-starter-webmvc"]
        Starter2["spring-boot-starter-data-jpa"]
        Starter3["spring-boot-starter-security"]

        Module1["spring-boot-webmvc"]
        Module2["spring-boot-data-jpa"]
        Module3["spring-boot-security"]

        Core["spring-boot<br/>(core)"]
    end

    subgraph Spring7["Spring Framework 7.0"]
        SpringCore["spring-core"]
        SpringBeans["spring-beans"]
        SpringContext["spring-context"]
        SpringWeb["spring-webmvc"]
        SpringData["spring-data-jpa"]
        SpringSecurity["spring-security"]
    end

    subgraph Runtime["运行时"]
        Jakarta["Jakarta EE 11"]
        JVM["JVM<br/>Java 17-25"]
    end

    App --> Starter1
    App --> Starter2
    App --> Starter3

    Starter1 --> Module1
    Starter2 --> Module2
    Starter3 --> Module3

    Module1 --> Core
    Module2 --> Core
    Module3 --> Core

    Core --> SpringCore
    Module1 --> SpringWeb
    Module2 --> SpringData
    Module3 --> SpringSecurity

    SpringCore --> SpringBeans
    SpringBeans --> SpringContext

    Spring7 --> Jakarta
    Jakarta --> JVM

    style App fill:#e1f5fe
    style Boot4 fill:#fff8e1
    style Spring7 fill:#e8f5e9
    style Runtime fill:#fce4ec
```

## 六、微服务架构图

```mermaid
graph TB
    Client["Client<br/>(Web/Mobile)"]

    subgraph Gateway["API Gateway"]
        GW["Spring Cloud Gateway"]
    end

    subgraph Services["微服务集群"]
        User["User Service<br/>Spring Boot 4<br/>+ WebMVC"]
        Order["Order Service<br/>Spring Boot 4<br/>+ WebFlux"]
        Product["Product Service<br/>Spring Boot 4<br/>+ WebMVC"]
        Payment["Payment Service<br/>Spring Boot 4<br/>+ Security"]
    end

    subgraph Data["数据存储"]
        UserDB[(PostgreSQL)]
        OrderDB[(MongoDB)]
        ProductDB[(PostgreSQL)]
        PaymentDB[(PostgreSQL)]
    end

    subgraph Messaging["消息系统"]
        Kafka["Apache Kafka"]
    end

    subgraph Observability["可观测性"]
        OTel["OpenTelemetry<br/>Collector"]
        Prometheus["Prometheus"]
        Grafana["Grafana"]
        Jaeger["Jaeger"]
    end

    subgraph Discovery["服务发现"]
        Eureka["Eureka Server"]
        Config["Config Server"]
    end

    Client --> GW
    GW --> User
    GW --> Order
    GW --> Product
    GW --> Payment

    User --> UserDB
    Order --> OrderDB
    Product --> ProductDB
    Payment --> PaymentDB

    User --> Kafka
    Order --> Kafka
    Product --> Kafka
    Payment --> Kafka

    User --> OTel
    Order --> OTel
    Product --> OTel
    Payment --> OTel

    OTel --> Prometheus
    OTel --> Jaeger
    Prometheus --> Grafana

    User -.-> Eureka
    Order -.-> Eureka
    Product -.-> Eureka
    Payment -.-> Eureka

    User -.-> Config
    Order -.-> Config
    Product -.-> Config
    Payment -.-> Config

    style Gateway fill:#e3f2fd
    style Services fill:#e8f5e9
    style Data fill:#fff3e0
    style Messaging fill:#fce4ec
    style Observability fill:#f3e5f5
    style Discovery fill:#e0f7fa
```

## 七、Spring Security 7.0 过滤器链

```mermaid
graph TB
    Request["HTTP Request"]

    subgraph FilterChain["Security Filter Chain"]
        F1["DisableEncodeUrlFilter"]
        F2["WebAsyncManagerIntegrationFilter"]
        F3["SecurityContextHolderFilter"]
        F4["HeaderWriterFilter"]
        F5["CsrfFilter"]
        F6["LogoutFilter"]
        F7["UsernamePasswordAuthFilter"]
        F8["OAuth2LoginAuthFilter"]
        F9["BearerTokenAuthFilter"]
        F10["ExceptionTranslationFilter"]
        F11["AuthorizationFilter"]
    end

    Controller["@RestController"]

    Request --> F1
    F1 --> F2
    F2 --> F3
    F3 --> F4
    F4 --> F5
    F5 --> F6
    F6 --> F7
    F7 --> F8
    F8 --> F9
    F9 --> F10
    F10 --> F11
    F11 --> Controller

    style FilterChain fill:#fff3e0
```

## 八、可观测性架构图

```mermaid
graph TB
    subgraph Application["Spring Boot 4 Application"]
        App["Application Code"]
        Micrometer["Micrometer"]
        OTelSDK["OpenTelemetry SDK"]
    end

    subgraph Signals["三大信号"]
        Metrics["Metrics<br/>指标"]
        Traces["Traces<br/>追踪"]
        Logs["Logs<br/>日志"]
    end

    subgraph Collector["收集器"]
        OTelCol["OpenTelemetry<br/>Collector"]
    end

    subgraph Backend["后端存储"]
        Prom["Prometheus"]
        Jaeger["Jaeger/Zipkin"]
        Loki["Loki"]
    end

    subgraph Visualization["可视化"]
        Grafana["Grafana<br/>Dashboard"]
    end

    App --> Micrometer
    Micrometer --> OTelSDK

    OTelSDK --> Metrics
    OTelSDK --> Traces
    OTelSDK --> Logs

    Metrics --> OTelCol
    Traces --> OTelCol
    Logs --> OTelCol

    OTelCol --> Prom
    OTelCol --> Jaeger
    OTelCol --> Loki

    Prom --> Grafana
    Jaeger --> Grafana
    Loki --> Grafana

    style Application fill:#e1f5fe
    style Signals fill:#fff8e1
    style Collector fill:#e8f5e9
    style Backend fill:#fce4ec
    style Visualization fill:#f3e5f5
```

## 九、自动配置加载流程

```mermaid
flowchart TB
    Start["main() 启动"]

    Start --> Run["SpringApplication.run()"]
    Run --> Context["创建 ApplicationContext"]

    Context --> Scan["扫描 AutoConfiguration.imports"]

    subgraph Modules["模块化配置文件"]
        M1["spring-boot-webmvc<br/>/*.imports"]
        M2["spring-boot-data-jpa<br/>/*.imports"]
        M3["spring-boot-security<br/>/*.imports"]
        M4["spring-boot-actuator<br/>/*.imports"]
    end

    Scan --> Modules

    Modules --> Conditional["处理条件注解"]

    subgraph Conditions["@Conditional 注解"]
        C1["@ConditionalOnClass"]
        C2["@ConditionalOnMissingBean"]
        C3["@ConditionalOnProperty"]
        C4["@ConditionalOnWebApplication"]
    end

    Conditional --> Conditions

    Conditions --> Register["注册符合条件的 Bean"]
    Register --> Ready["应用就绪"]

    style Modules fill:#fff3e0
    style Conditions fill:#e8f5e9
```

## 十、数据访问架构图

```mermaid
graph TB
    subgraph Repository["Repository 抽象"]
        R1["Repository&lt;T, ID&gt;"]
        R2["CrudRepository"]
        R3["PagingAndSortingRepository"]
        R4["JpaRepository"]
        R5["ReactiveRepository"]
    end

    R1 --> R2
    R2 --> R3
    R3 --> R4
    R2 --> R5

    subgraph Implementations["实现模块"]
        JPA["Spring Data JPA<br/>(Hibernate)"]
        JDBC["Spring Data JDBC"]
        Mongo["Spring Data MongoDB"]
        Redis["Spring Data Redis"]
        R2DBC["Spring Data R2DBC"]
        ES["Spring Data<br/>Elasticsearch"]
    end

    R4 --> JPA
    R3 --> JDBC
    R3 --> Mongo
    R3 --> Redis
    R5 --> R2DBC
    R3 --> ES

    subgraph Drivers["驱动层"]
        D1["JDBC Driver"]
        D2["MongoDB Driver"]
        D3["Lettuce"]
        D4["R2DBC Driver"]
        D5["REST Client"]
    end

    JPA --> D1
    JDBC --> D1
    Mongo --> D2
    Redis --> D3
    R2DBC --> D4
    ES --> D5

    subgraph Databases["数据库"]
        DB1[(PostgreSQL)]
        DB2[(MySQL)]
        DB3[(MongoDB)]
        DB4[(Redis)]
        DB5[(Elasticsearch)]
    end

    D1 --> DB1
    D1 --> DB2
    D2 --> DB3
    D3 --> DB4
    D5 --> DB5

    style Repository fill:#e3f2fd
    style Implementations fill:#e8f5e9
    style Drivers fill:#fff3e0
    style Databases fill:#fce4ec
```
