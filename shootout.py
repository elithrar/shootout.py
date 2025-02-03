#!/usr/bin/env python3
import asyncio
import argparse
import datetime
import json
import sys
import tomli
from pathlib import Path
from typing import Dict, Any, Optional
import llm

async def query_model_async(
    model_name: str,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    additional_system: str = ""
) -> Optional[Dict[str, Any]]:
    try:
        print(f"Querying {model_name}...")
        model = llm.get_async_model(model_name)
        model.key = api_key

        full_system_prompt = system_prompt
        if additional_system:
            full_system_prompt = f"{system_prompt}\n{additional_system}"

        response = await model.prompt(user_prompt, system=full_system_prompt)
        result = await response.text()

        return {
            "system_prompt_used": full_system_prompt,
            "user_prompt_used": user_prompt,
            "response": result
        }
    except Exception as e:
        print(f"Error querying {model_name}: {str(e)}", file=sys.stderr)
        return None

def query_model_sync(
    model_name: str,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    additional_system: str = ""
) -> Optional[Dict[str, Any]]:
    try:
        print(f"Querying {model_name}...")
        model = llm.get_model(model_name)
        model.key = api_key

        full_system_prompt = system_prompt
        if additional_system:
            full_system_prompt = f"{system_prompt}\n{additional_system}"

        response = model.prompt(user_prompt, system=full_system_prompt)
        result = response.text()

        return {
            "system_prompt_used": full_system_prompt,
            "user_prompt_used": user_prompt,
            "response": result
        }
    except Exception as e:
        print(f"Error querying {model_name}: {str(e)}", file=sys.stderr)
        return None

async def main():
    parser = argparse.ArgumentParser(description="Query multiple LLMs in parallel")
    parser.add_argument("--config", default="model_config.toml", help="Path to TOML config file")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config file {args.config} not found", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "rb") as f:
        config = tomli.load(f)

    system_prompt = config.get("system_prompt", "")
    user_prompt = config.get("user_prompt", "")
    models = config.get("models", [])

    if not models:
        print("No models configured in TOML file", file=sys.stderr)
        sys.exit(1)

    tasks = []
    sync_results = {}

    for model_config in models:
        if model_config.get("async", True):
            tasks.append(
                query_model_async(
                    model_config["model_name"],
                    model_config["api_key"],
                    system_prompt,
                    user_prompt,
                    model_config.get("additional_system_prompt", "")
                )
            )
        else:
            result = query_model_sync(
                model_config["model_name"],
                model_config["api_key"],
                system_prompt,
                user_prompt,
                model_config.get("additional_system_prompt", "")
            )
            if result is not None:
                sync_results[model_config["model_name"]] = result

    async_results = await asyncio.gather(*tasks)

    output = sync_results.copy()
    for model_config, result in zip([m for m in models if m.get("async", True)], async_results):
        if result is not None:  # Only include successful results
            output[model_config["model_name"]] = result

    # Create results directory if it doesn't exist
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = results_dir / f"{timestamp}-model-shootout.json"

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results written to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
