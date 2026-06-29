# Link Generator

```{anywidget} ./plugins/link-generator.mjs
{
  "app": [
    {
      "JupyterLab": [
        {
          "shutdown_timeout": {
            "default": 1200,
            "tooltip": "Time in seconds before the JupyterLab server shuts down due to inactivity.",
            "title": "Shutdown Timeout"
          }
        },
        {
          "command": {
            "default": "jupyter lab --no-browser --port=8888 --ip=0.0.0.0 --ServerApp.shutdown_no_activity_timeout={{shutdown_timeout}} --MappingKernelManager.cull_idle_timeout={{shutdown_timeout}} --TerminalManager.cull_inactive_timeout={{shutdown_timeout}}",
            "tooltip": "Command that will be ran to start the environment",
            "title": "Command"
          }
        }
      ]
    },
    {
      "JupyterHub": [
        {
          "shutdown_timeout": {
            "default": 1200,
            "tooltip": "Time in seconds before the JupyterLab server shuts down due to inactivity.",
            "title": "Shutdown Timeout"
          }
        },
        {
          "command": {
            "default": "jupyter lab --no-browser --port=8888 --ip=0.0.0.0 --ServerApp.shutdown_no_activity_timeout={{shutdown_timeout}} --MappingKernelManager.cull_idle_timeout={{shutdown_timeout}} --TerminalManager.cull_inactive_timeout={{shutdown_timeout}}",
            "tooltip": "Command that will be ran to start the environment",
            "title": "Command"
          }
        }
      ]
    }
  ]
}
```