## shootout.py

> Just a side project, y'know?

Evaluate multiple LLMs using the command-line. Feed the results into your system of choice, another LLM, or your preferred evaluations framework. Built on the wonderful [`llm`](https://llm.datasette.io/en/stable/python-api.html).

Write results to a JSON file for you to consume or review with other tooling.

```sh
uv run shootout.py
```

By default it will look for a `model_config.toml` file (see the example included) with your models and API keys. You can pass `--config some_other_file.toml` to pass it an alternative configuration.

## Install plugins

To use models with an [llm plugin](https://llm.datasette.io/en/stable/plugins/installing-plugins.html), install the relevant plugin library for `llm` to use:

```sh
uv pip install llm-anthropic llm-cloudflare llm-deepseek
```

Review the [`llm` plugin directory](https://llm.datasette.io/en/stable/plugins/directory.html) for the list of supported plugins.

## License

Apache 2.0 licensed. See the LICENSE file for details.
