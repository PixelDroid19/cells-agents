# Cells CLI Commands

## Application Commands

### `cells lit-component:create`
- **Usage**: `cells lit-component:create <name> [namespace]`
- **Description**: Scaffolds a new LitElement component with standard structure.

### `cells lit-component:serve`
- **Usage**: `cells lit-component:serve`
- **Description**: Serves a component demo locally.

### `cells lit-component:lint`
- **Usage**: `cells lit-component:lint`
- **Description**: Performs static analysis on the component code.

### `cells lit-component:locales`
- **Usage**: `cells lit-component:locales`
- **Description**: Generates locale files for component demos.

### `cells lit-component:documentation`
- **Usage**: `cells lit-component:documentation`
- **Description**: Generates README.md and custom-elements.json from JSDoc.

### `cells app:serve`
- **Usage**: `nvm use 18 && cells app:serve -c <config>`
- **Example**: `nvm use 18 && cells app:serve -c co/web-dev.js`
- **Mandatory**: **MUST** include the `-c` flag with a relative path (e.g., `co/web-dev.js`).

### `cells app:build`
Builds the application for deployment.
- **Usage**: `cells app:build -c <config>`
- **Important**: Mandatory configuration flag `-c co/<filename>` is required.
- **Example**: `cells app:build -c co/android-dev.js`
- **Options**:
    - `--compress`: Use compression for LitElement builds.
    - `--sourcemaps`: Generate source maps.
    - `--dark-mode`: Compose dark mode theme.

### `cells app:create`
Creates the scaffolding of a Cells application.
- **Usage**: `cells app:create`
- **Interactive**: Prompts for scaffold type (web/mobile) and E2E support.

### `cells app:lint`
Static analysis for applications.
- **Usage**: `cells app:lint`

### `cells app:test`
Run unit tests on in-app LitElement components.
- **Usage**: `cells app:test`

### `cells app:install`
Install applications dependencies.
- **Usage**: `cells app:install`

## Component Commands

### `cells lit-component:serve`
Serves the component locally for development.
- **Usage**: `cells lit-component:serve`
- **Features**:
    - Lints JavaScript code.
    - **Compiles SCSS to CSS automatically**. (Do not compile manually).
    - Watches for changes and reloads.
- **Note**: This command is the ONLY approved way to preview style changes. Manual CSS editing is forbidden.

### `cells lit-component:create`
Creates a new LitElement WebComponent.
- **Usage**: `cells lit-component:create <name> [namespace] [--e2e]`
- **Arguments**:
  - `name`: Component name (must contain a hyphen).
  - `namespace`: Optional (defaults to `@bbva-web-components`).
- **Options**:
  - `--e2e`: Create an e2e test scaffold.
  - `-i, --install-deps`: Install dependencies after creation.
- **Structure**: Generates `src/ComponentName.js`, `ComponentName.scss`, `demo/`, `test/`.

### `cells lit-component:test`
Runs unit tests for the component.
- **Usage**: `cells lit-component:test`
- **Details**: Runs **Web Test Runner** and provides code coverage via Istanbul/c8.

### `cells lit-component:lint`
Runs static analysis on the component.
- **Usage**: `cells lit-component:lint`
- **Details**: Uses ESLint with strict project rules.

### `cells lit-component:locales`
Generates the `locales.json` file for the demo.
- **Usage**: `cells lit-component:locales`
- **Details**:
    - Merges `locales.json` from dependencies.
    - Component's own `locales.json` takes precedence.
    - Outputs to `/demo/locales` (mandatory path in Cells projects).
    - Do not place locale files outside `demo/locales`.

### `cells lit-component:documentation`
Generates component documentation.
- **Usage**: `cells lit-component:documentation`
- **Details**: Updates `README.md` and `custom-elements.json`.
