

[rei-2/Amalgam]()



# Getting Started

Relevant source files

* [Amalgam/Amalgam.vcxproj]()
* [Amalgam/Amalgam.vcxproj.filters]()
* [README.md]()

This guide covers building and setting up the Amalgam Team Fortress 2 cheat system. It includes information on build dependencies, configuration options, compilation procedures, and initial deployment. For information about the core architecture and systems, see [Core Architecture](). For details about configuring features and settings, see [Configuration System]().

## Prerequisites

Before building Amalgam, ensure you have the following development environment set up:

### Development Tools

| Component | Requirement | Notes |
| --- | --- | --- |
| **Visual Studio** | 2022 or later | Must include MSVC v143 toolset |
| **Windows SDK** | 10.0 or later | Required for platform APIs |
| **C++ Standard** | C++20 | Specified in project configuration |
| **Platform Support** | x86 and x64 | Both 32-bit and 64-bit builds supported |

### Hardware Requirements

* **AVX2 Support**: Optional but recommended for performance builds
* **Memory**: Minimum 4GB RAM for compilation
* **Storage**: ~500MB for source code and build artifacts

**Sources:** [Amalgam/Amalgam.vcxproj70-80]() [Amalgam/Amalgam.vcxproj393-394]() [Amalgam/Amalgam.vcxproj777-778]()

## Build Configurations

Amalgam provides multiple build configurations to support different deployment scenarios and performance requirements:

### Configuration Matrix

| Configuration | Platform | Features | Performance | Size |
| --- | --- | --- | --- | --- |
| `Debug` | Win32/x64 | Standard | Development | Small |
| `DebugFreetype` | Win32/x64 | Custom fonts | Development | Large |
| `DebugAVX2` | Win32/x64 | Vectorized | High | Small |
| `DebugFreetypeAVX2` | Win32/x64 | All features | High | Large |
| `Release` | Win32/x64 | Standard | Optimized | Small |
| `ReleaseFreetype` | Win32/x64 | Custom fonts | Optimized | Large |
| `ReleaseAVX2` | Win32/x64 | Vectorized | High | Small |
| `ReleaseFreetypeAVX2` | Win32/x64 | All features | High | Large |

### Preprocessor Definitions

The build system automatically defines configuration-specific macros:

```
```
// Standard builds
#define __CONFIGURATION__ "Release"
#define __PLATFORM__ "x64"

// Freetype builds add:
#define IMGUI_ENABLE_FREETYPE
#define AMALGAM_CUSTOM_FONTS

// All builds include:
#define _DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR
```
```

**Sources:** [Amalgam/Amalgam.vcxproj391-392]() [Amalgam/Amalgam.vcxproj423-424]() [Amalgam/Amalgam.vcxproj553-554]()

## Build Process

### Directory Structure

The build system uses the following output structure:

### Compilation Steps

1. **Configure Build Environment**

   * Select target configuration and platform
   * Verify all dependencies are available
   * Set up include and library paths
2. **Compile Source Files**

   * Process core systems and utilities
   * Build feature implementations
   * Compile SDK and interface layers
   * Link external dependencies
3. **Generate Output**

   * Create dynamic library (DLL)
   * Generate debug symbols (PDB)
   * Apply optimizations for release builds

### Build Commands

Using Visual Studio:

```
```
# Build specific configuration
msbuild Amalgam.sln -p:Configuration=Release -p:Platform=x64

# Build all configurations
msbuild Amalgam.sln -p:Configuration=Release
```
```

Using Developer Command Prompt:

```
```
# Clean and rebuild
devenv Amalgam.sln /Clean "Release|x64"
devenv Amalgam.sln /Rebuild "Release|x64"
```
```

**Sources:** [Amalgam/Amalgam.vcxproj243-248]() [Amalgam/Amalgam.vcxproj271-276]() [Amalgam/Amalgam.vcxproj299-308]()

## Dependencies and Libraries

### Core Dependencies

### Include Directory Structure

The project uses a centralized include directory:

| Path | Contents |
| --- | --- |
| `include/ImGui/` | ImGui library and extensions |
| `include/MinHook/` | Function hooking framework |
| `include/freetype/` | Font rendering library |
| `src/` | Amalgam source code |

**Sources:** [Amalgam/Amalgam.vcxproj890-904]() [Amalgam/Amalgam.vcxproj246-247]() [Amalgam/Amalgam.vcxproj1086-1139]()

## Deployment

### Injection Methods

Amalgam requires injection into the Team Fortress 2 process. The recommended methods are:

1. **VAC Bypass Loader** (Recommended)

   * Provides anti-cheat evasion
   * Handles process injection automatically
   * Supports manual mapping
2. **Xenos Injector** (Alternative)

   * Manual DLL injection tool
   * Supports various injection techniques
   * Requires manual anti-cheat bypass

### File Placement

After building, the deployment structure should be:

```
tf2_installation/
├── hl2.exe
├── bin/
│   └── AmalgamPlatformConfiguration.dll
└── tf/
    └── cfg/
        └── amalgam/
            ├── configs/
            ├── materials/
            └── logs/
```

### Initial Configuration

1. **First Launch**

   * Inject DLL into TF2 process
   * Menu opens automatically on first run
   * Default configuration is loaded
2. **Menu Access**

   * Default key: `Insert`
   * Can be changed in keybind settings
   * Available in main menu and during gameplay
3. **Configuration Location**

   * Configs stored in `tf/cfg/amalgam/configs/`
   * Auto-generated default configuration
   * JSON format for easy editing

**Sources:** [README.md38-39]() [src/Features/Configs/Configs.cpp]() [src/Features/ImGui/Menu/Menu.cpp]()

## Development Workflow

### Debug Builds

Debug configurations provide:

* Full symbol information
* Runtime error checking
* Detailed crash reports
* Performance profiling support

### Release Builds

Release configurations optimize for:

* Maximum performance
* Minimal file size
* Link-time optimization
* Runtime efficiency

### Version Information

Each build includes embedded version information:

* Configuration name
* Platform target
* Build timestamp
* Commit information

**Sources:** [Amalgam/Amalgam.vcxproj637-669]() [Amalgam/Amalgam.vcxproj769-798]() [src/Core/Core.cpp]()


