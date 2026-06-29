# Link generator

::::{tab-set}

:::{tab-item}  Classic link
```{jsonform}
Schema:
  type: object
  properties:
    gitenv:
      type: object
      properties:
        gitenvrepo:
          type: string
          title: "Git Environment Repository URL"
          description: "Url to a public git repo containing an environment description"
        gitenvbranch:
          type: string
          title: "Environment repository branch"
          description: "For old repositories, use master instead of main"
    gitressources:
      type: object
      properties:
        gitressourcesrepo:
          type: string
          title: "Git Content Repository URL"
          description: "Url to a public git repo containing the ressources you want to open"
        gitressourcesbranch:
          type: string
          title: "Content repository branch"
          description: "For old repositories, use master instead of main"
    filetoopen:
      type: string
      title: "File to open (optional)"
      description: "File to open after checkout"
    app:
      type: string
      title: "Application to open"
      enum: ["Jupyter Lab", "Jupyter Hub"]
    jlapp:
      type: object
      properties:
        shutdowntimeout:
          type: integer
          title: "Shutdown Timeout"
          description: "Timer before the environement shuts himself down due to inactivity"
        command:
          type: string
          title: "Command"
          description: "Command that will be used to lanch the JL environement"
    jhapp:
      type: object
      properties:
        shutdowntimeout:
          type: integer
          title: "Shutdown Timeout"
          description: "Timer before the environement shuts himself down due to inactivity"
        command:
          type: string
          title: "Command"
          description: "Command that will be used to lanch the JH environement"

UISchema:
  type: VerticalLayout
  elements:
    - type: Group
      label: Env
      elements:
        - type: Control
          scope: "#/properties/gitenv/properties/gitenvrepo"
        - type: Control
          scope: "#/properties/gitenv/properties/gitenvbranch"
    - type: Group
      label: Ressources
      elements:
        - type: Control
          scope: "#/properties/gitressources/properties/gitressourcesrepo"
        - type: Control
          scope: "#/properties/gitressources/properties/gitressourcesbranch"
    - type: Control
      scope: "#/properties/filetoopen"
    - type: Control
      scope: "#/properties/app"
    - type: Group
      label: "Jupyter Lab settings"
      rule:
        effect: SHOW
        condition:
          scope: "#/properties/app"
          schema:
            const: "Jupyter Lab"
      elements:
        - type: Control
          scope: "#/properties/jlapp/properties/shutdowntimeout"
        - type: Control
          scope: "#/properties/jlapp/properties/command"
    - type: Group
      label: "Jupyter Hub settings"
      rule:
        effect: SHOW
        condition:
          scope: "#/properties/app"
          schema:
            const: "Jupyter Hub"
      elements:
        - type: Control
          scope: "#/properties/jhapp/properties/shutdowntimeout"
        - type: Control
          scope: "#/properties/jhapp/properties/command"

Data:
  gitenv:
    gitenvbranch: main
  gitressources:
    gitressourcesbranch: main
  app: "Jupyter Lab"
  jlapp:
    shutdowntimeout: 1200
    command: foo
  jhapp:
    shutdowntimeout: 1200
    command: bar
```
:::

:::{tab-item}  Invitation Link
```{jsonform}
Schema:
  type: object
  properties:
    invitelink:
      type: string
      title: "Invitation Link"
      description: "The invitation link for your environment"
    gitenv:
      type: object
      properties:
        gitenvrepo:
          type: string
          title: "Git Environment Repository URL"
          description: "Url to a public git repo containing an environment description"
        gitenvbranch:
          type: string
          title: "Environment repository branch"
          description: "For old repositories, use master instead of main"
    gitressources:
      type: object
      properties:
        gitressourcesrepo:
          type: string
          title: "Git Content Repository URL"
          description: "Url to a public git repo containing the ressources you want to open"
        gitressourcesbranch:
          type: string
          title: "Content repository branch"
          description: "For old repositories, use master instead of main"
    filetoopen:
      type: string
      title: "File to open (optional)"
      description: "File to open after checkout"
    app:
      type: string
      title: "Application to open"
      enum: ["Jupyter Lab", "Jupyter Hub"]
    jlapp:
      type: object
      properties:
        shutdowntimeout:
          type: integer
          title: "Shutdown Timeout"
          description: "Timer before the environement shuts himself down due to inactivity"
        command:
          type: string
          title: "Command"
          description: "Command that will be used to lanch the JL environement"
    jhapp:
      type: object
      properties:
        shutdowntimeout:
          type: integer
          title: "Shutdown Timeout"
          description: "Timer before the environement shuts himself down due to inactivity"
        command:
          type: string
          title: "Command"
          description: "Command that will be used to lanch the JH environement"

UISchema:
  type: VerticalLayout
  elements:
    - type: Control
      scope: "#/properties/invitelink"
    - type: Group
      label: Env
      elements:
        - type: Control
          scope: "#/properties/gitenv/properties/gitenvrepo"
        - type: Control
          scope: "#/properties/gitenv/properties/gitenvbranch"
    - type: Group
      label: Ressources
      elements:
        - type: Control
          scope: "#/properties/gitressources/properties/gitressourcesrepo"
        - type: Control
          scope: "#/properties/gitressources/properties/gitressourcesbranch"
    - type: Control
      scope: "#/properties/filetoopen"
    - type: Control
      scope: "#/properties/app"
    - type: Group
      label: "Jupyter Lab settings"
      rule:
        effect: SHOW
        condition:
          scope: "#/properties/app"
          schema:
            const: "Jupyter Lab"
      elements:
        - type: Control
          scope: "#/properties/jlapp/properties/shutdowntimeout"
        - type: Control
          scope: "#/properties/jlapp/properties/command"
    - type: Group
      label: "Jupyter Hub settings"
      rule:
        effect: SHOW
        condition:
          scope: "#/properties/app"
          schema:
            const: "Jupyter Hub"
      elements:
        - type: Control
          scope: "#/properties/jhapp/properties/shutdowntimeout"
        - type: Control
          scope: "#/properties/jhapp/properties/command"

Data:
  gitenv:
    gitenvbranch: main
  gitressources:
    gitressourcesbranch: main
  app: "Jupyter Lab"
  jlapp:
    shutdowntimeout: 1200
    command: foo
  jhapp:
    shutdowntimeout: 1200
    command: bar
```
:::