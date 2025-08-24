- ETL flowchart:
    ```mermaid
    flowchart LR
        Start([Start]) --> Save_Variables[Save_Variables]
        Save_Variables --> Compile_jsonnet[Compile_jsonnet]
        Compile_jsonnet --> Organize_dir[Organize_dir]
        Organize_dir --> daily_task[daily_task]
        daily_task --> Load_head[Load_daily_va_px_txn_head]
        daily_task --> Load_detail[Load_daily_va_px_txn_detail]
        Load_head --> End([End])
        Load_detail --> End([End])
    ```