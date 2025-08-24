import json
import yaml
import _jsonnet

tables = json.loads(_jsonnet.evaluate_file("table.libsonnet"))

for table in tables:
    print(table)

    ext_vars = {"table": table}
    input_config_file = "gpload-json-template.jsonnet"

    json_parsed = json.loads(
        _jsonnet.evaluate_file(input_config_file, ext_vars=ext_vars)
    )
    with open(f"{table}.yml", "w") as f:
        yaml.dump(json_parsed, f, default_flow_style=False)
