# Startup Flow

To ensure a smooth, crash-free startup experience, ZANIME follows a strict initialization order.

```mermaid
graph TD
    A[main.py Executed] --> B[Initialize ApplicationManager]
    B --> C[Initialize LoggingManager]
    C --> D[Initialize ConfigurationManager]
    D --> E[Initialize ThemeEngine]
    E --> F[Initialize WindowManager]
    F --> G[Show Splash Screen]
    G --> H[Initialize Core Managers]
    
    subgraph Core Managers
        H --> I[EventBus]
        I --> J[CacheManager]
        J --> K[AssetManager]
        K --> L[ProjectManager]
        L --> M[CommandManager]
        M --> N[WorkspaceManager]
    end
    
    N --> O[Initialize PluginManager]
    O --> P{Check Args / Recent Projects}
    
    P -- "No Project" --> Q[Load Welcome Screen]
    P -- "Demo / Recent" --> R[Load Project via ProjectManager]
    
    Q --> S[Hide Splash Screen]
    R --> T[Show Main Window]
    T --> S
```

## Flow Description

1. **Logging First**: The `LoggingManager` must be initialized immediately to catch errors during the rest of the startup process.
2. **Configuration Second**: `ConfigurationManager` reads user and system preferences.
3. **Theme Third**: `ThemeEngine` needs to be ready so that the `SplashScreen` and all subsequent UI elements look correct immediately.
4. **Splash Screen**: Displayed as soon as basic Qt elements are ready, giving the user immediate visual feedback while heavy managers load.
5. **Core Managers**: Initialized in order of dependency. (e.g., `ProjectManager` might need `AssetManager`).
6. **Plugins Last**: Plugins are loaded last because they rely on the Core Managers being fully initialized and the `EventBus` being active.
