

[rei-2/Amalgam]()



# Overview

Relevant source files

* [Amalgam/Amalgam.vcxproj]()
* [Amalgam/Amalgam.vcxproj.filters]()
* [Amalgam/src/Core/Core.cpp]()
* [Amalgam/src/Utils/CrashLog/CrashLog.cpp]()
* [README.md]()

## Purpose and Scope

Amalgam is a comprehensive Team Fortress 2 cheat system that provides aim assistance, visual enhancements, and game manipulation capabilities. This document provides a high-level architectural overview of the system's core components and their relationships.

For detailed information about specific subsystems, see [Core Architecture](), [Configuration System](), [Aimbot Systems](), [Visual Systems](), and [Game Integration]().

## System Architecture

The following diagram illustrates the primary architectural layers and their relationships within Amalgam:

Sources: [Amalgam/src/Core/Core.cpp1-157]() [Amalgam/Amalgam.vcxproj.filters1-581]()

## Core System Components

### CCore - System Initialization

The `CCore` class manages the entire lifecycle of the Amalgam system, from initial loading through cleanup and unload procedures.

| Component | Responsibility | Key Methods |
| --- | --- | --- |
| `CCore::Load()` | System initialization and dependency verification | Process validation, signature scanning, interface setup |
| `CCore::Loop()` | Main execution loop | User input monitoring, unload condition checking |
| `CCore::Unload()` | Clean shutdown and resource cleanup | Hook removal, state restoration, memory cleanup |

The initialization process validates the target process (`tf_win64.exe`), establishes game interfaces, and loads all feature modules in a specific order to ensure proper dependency resolution.

Sources: [Amalgam/src/Core/Core.cpp68-157]()

### Build Configuration Matrix

Amalgam supports multiple build configurations optimized for different use cases:

| Configuration | AVX2 | Freetype | Debug Info | Use Case |
| --- | --- | --- | --- | --- |
| `Release` | ❌ | ❌ | ❌ | Standard production build |
| `ReleaseAVX2` | ✅ | ❌ | ❌ | Optimized for modern CPUs |
| `ReleaseFreetype` | ❌ | ✅ | ❌ | Enhanced text rendering |
| `ReleaseFreetypeAVX2` | ✅ | ✅ | ❌ | Full-featured build |
| `Debug*` | Varies | Varies | ✅ | Development builds |

Each configuration produces a `DynamicLibrary` targeting both `Win32` and `x64` platforms with optimizations enabled (`WholeProgramOptimization`).

Sources: [Amalgam/Amalgam.vcxproj3-188]()

## Subsystem Integration Flow

The following diagram shows how the major subsystems integrate during runtime:

Sources: [Amalgam/src/Core/Core.cpp93-104]() [Amalgam/src/Utils/Hooks/Hooks.cpp]()

## Exception Handling and Crash Recovery

Amalgam includes a comprehensive crash logging system that captures detailed debugging information when exceptions occur:

The crash logging system uses `ImageHlp.lib` for symbol resolution and generates detailed stack traces including module names, file locations, and function names when debug symbols are available.

Sources: [Amalgam/src/Utils/CrashLog/CrashLog.cpp93-164]()

## Configuration and State Management

Amalgam employs a sophisticated configuration system that supports multiple layers of customization:

* **Variables System**: Type-safe configuration storage with metadata
* **Bind System**: Conditional configuration based on keys, classes, and weapons
* **Config Persistence**: JSON-based save/load functionality
* **Runtime Menu**: ImGui-based interface for real-time configuration

The system maintains configuration state across game sessions and supports both global settings and context-specific binds that activate based on game conditions.

Sources: [Amalgam/src/Features/Configs/Configs.cpp]() [Amalgam/src/Features/Binds/Binds.cpp]()

## Project Structure and Dependencies

Amalgam integrates several key external libraries:

* **ImGui**: Provides the immediate-mode GUI framework for the configuration menu
* **MinHook**: Enables function hooking for game integration
* **FreeType** (optional): Enhanced font rendering capabilities

The codebase follows a modular architecture with clear separation between utilities, SDK abstraction, feature implementations, and user interface components.

Sources: [Amalgam/Amalgam.vcxproj.filters28-92]() [README.md29-39]()


