### AERIS — Short Description

> **AERIS (Adaptive Enterprise Reliability & Intelligence System)** is an extensible enterprise Data & AI platform that unifies data products, governance, reliability, and AI across Snowflake, Databricks, and open data technologies—enabling scalable, governed, and engine-agnostic data intelligence.

### Mermaid Architecture

```mermaid
flowchart TD
    %% Node Definitions
    consumers["<b>Enterprise Consumers</b><br><span style='font-size:12px; color:#aaa;'>Analytics • APIs • Applications • Data Science</span>"]
    
    subgraph aeris["<b>AERIS Platform Services</b>"]
        direction TB
        subgraph row1[" "]
            direction LR
            dp["<b>Data Products</b><br><span style='font-size:11px; color:#aaa;'>Contracts • Semantic models • Lifecycle</span>"]
            gov["<b>Governance</b><br><span style='font-size:11px; color:#aaa;'>Identity • Policy • Lineage • Access</span>"]
        end
        subgraph row2[" "]
            direction LR
            ro["<b>Reliability & Observability</b><br><span style='font-size:11px; color:#aaa;'>SLIs/SLOs • Quality • Audit • Recovery</span>"]
            df["<b>Delivery & FinOps</b><br><span style='font-size:11px; color:#aaa;'>CI/CD • Security • Cost • Optimization</span>"]
        end
    end

    compute["<b>Data & Compute Engines</b><br><span style='font-size:13px;'>Snowflake</span><br><span style='font-size:11px; color:#aaa;'>Warehouse • SQL • Native processing</span>"]
    
    aiml["<b>AI / ML Engines</b><br><span style='font-size:11px; color:#aaa;'>ML • GenAI • Model Services<br>Training • Inference • Evaluation</span>"]

    storage["<b>Open Data & Storage Layer</b><br><span style='font-size:12px; color:#aaa;'>Apache Iceberg • Parquet • Object Storage • Open Table Formats</span>"]

    portable["<b>Portable Data Assets</b>"]
    future["<b>Future Engines / Services</b>"]

    %% Connections
    consumers --> aeris
    aeris --> compute
    aeris --> storage
    aeris --> aiml
    compute --> storage
    aiml --> storage
    storage --> portable
    storage --> future

    %% Styling to match dark theme
    classDef default fill:#1e2227,stroke:#3b4048,stroke-width:1px,color:#fff;
    classDef dashedBox fill:#1a1d21,stroke:#555d68,stroke-width:1.5px,stroke-dasharray: 5 5,color:#fff;
    classDef plainBox fill:transparent,stroke:none;

    class storage dashedBox;
    class row1,row2 plainBox;
    style aeris fill:#171a1e,stroke:#2060b0,stroke-width:2px,color:#fff;
    linkStyle default stroke:#4b535d,stroke-width:1.5px;
```
