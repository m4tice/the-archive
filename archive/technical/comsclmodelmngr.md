**ID:** 40001  
**Title:** ComScl_ModelMngr  
**Author:** Nguyen Duc Tuan  
**Date:** 2026-03-08  
**Tags:** MCP, Copilot, Bosch  

---

# ComScl_ModelMngr

## 1. Environment and Terms

**Ecu.WorX**

* Eclipse-based AUTOSAR configuration IDE.
* Uses ARTOP / EMF modeling framework.

**PVER (Project Version)**

* A full AUTOSAR configuration project.
* Contains:

  * `ParamDef.arxml` (configuration schema)
  * `<module>_ecucvalues.arxml` (actual configuration values)
  * System template models (ARTOP).

Teams typically work with **multiple PVERs simultaneously**, and each PVER may use **different ParamDef versions**.

---

## 2. AUTOSAR Configuration Model Structure

### ParamDef

Defines the **schema of configuration components**.

Examples:

* Containers (e.g., `ComIPdu`)
* Parameters (e.g., `ComIPduDirection`)
* Multiplicity rules
* Relationships

When the IDE loads a project:

1. ParamDef files are parsed.
2. Java **accessor classes** are generated.
3. Empty container/parameter instances are created.

---

### ECUCValues

Files like:

```
Com_ecucvalues.arxml
```

Contain actual configuration instances.

Example:

```
ComIPdu_ESP_19
ComIPduDirection = RECEIVE
```

During project loading, these values populate the previously generated containers.

---

## 3. Internal Model Representation

When the project loads:

```
ParamDef
→ Accessor generation
→ Container instantiation
→ ECUCValues loading
→ Full configuration model
```

The model is accessible through a **Context class**.

The Context provides access to:

* ECUC models

  * Com
  * Can
  * CanIf
* ARTOP system models

  * ISignal
  * ISignalIPdu
  * CommunicationCluster

Your current work focuses on **ECUC models only**.

---

## 4. Your Automation Solution

You implemented a **headless Java program** that:

1. Loads the **Context**
2. Accesses ECUC models
3. Exposes a **local server API**

This allows **Copilot (via MCP tools)** to query the configuration models.

Architecture:

```
User Prompt
→ Copilot
→ MCP Tool
→ Local Java Server
→ Context
→ ECUC Model
```

---

## 5. Model Traversal Logic

Your search works using two inputs:

**1. Absolute definition path**

Example:

```
Com/ComConfig/ComIPdu
```

**2. Instance name**

Example:

```
ComIPdu_ESP_19
```

Traversal process:

1. Locate `Com` containers
2. Traverse to `ComConfig`
3. Traverse to `ComIPdu`
4. Find containers whose name matches the search key

Then a second function retrieves **all parameters of the container**.

Example output:

```
ComIPduDirection = RECEIVE
```

You also implemented **fuzzy search** so users do not need to type exact names.

---

## 6. Purpose of the Solution

The goal is to allow **Copilot to interact with AUTOSAR configuration models** and perform operations like:

* search containers
* inspect parameters
* analyze configuration structure

without manually navigating the IDE.

---

## 7. Main Problem

Loading the **Context** is extremely slow.

Full initialization includes:

```
ParamDef parsing
+ accessor generation
+ ECUCValues loading
+ model construction
```

Total time:

**~10 minutes or more**

This makes the solution impractical when:

* switching between PVERs
* reloading configuration after updates

Since PVERs change frequently during development, the server cannot stay alive forever with stale data.

---

## 8. Existing Optimization (Observed)

A solution team implemented an improvement and returned only a **.jar**.

Behavior:

* Provide PVER path
* Model loads in **~15 seconds**

The implementation details were not shared.

---

## 9. Most Likely Technique Used

They likely implemented **Context snapshot serialization**.

Process:

First run:

```
load ParamDef
build model
load ECUCValues
serialize Context
```

Later runs:

```
deserialize Context snapshot
```

This skips the expensive initialization steps.

Result:

```
10 minutes → ~15 seconds
```

---

## 10. Possible Solutions Identified

### 1. Context Snapshot (most impactful)

Serialize the fully built Context or underlying EMF model.

Next startup:

```
load snapshot instead of rebuilding model
```

Expected result:

```
10 min → 10–20 sec
```

---

### 2. PVER Fingerprint

Compute a hash of:

```
ParamDef + ECUCValues
```

If unchanged:

```
reuse snapshot
```

If changed:

```
rebuild snapshot
```

---

### 3. Other Ideas (less practical)

Lazy module loading
Not feasible because model loading is controlled by ARTOP/Ecu.WorX.

Parallel ARXML loading
Also controlled by the framework.

Container indexing
Unnecessary for your use case because search volume is low.

---

## 11. Current Conclusion

Your system already works conceptually:

* headless model loading
* API server
* fuzzy search
* Copilot integration

The **only real blocker** is:

**Context initialization time (~10 minutes)**.

The most effective direction is:

**Implement a Context snapshot / model serialization mechanism similar to the one used by the solution team.**
