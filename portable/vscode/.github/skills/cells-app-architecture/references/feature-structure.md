# Feature Structure

A standard Cells feature (often starting with `bbva-feature-`) follows a strict directory structure within `src/` to ensure maintainability and separation of concerns.

## Directory Layout

```
src/
├── configs/           # Static configuration (constants, mocks, labels)
├── data-manager/      # Data handling components (API logic)
├── mixins/            # Reusable class mixins (WidgetMixin)
├── pages/             # View components (screens)
├── shared-components/ # Reusable UI components internal to this feature
├── utils/             # Helper functions and utilities
├── styles/            # CSS styles (often as .css.js files)
└── BbvaFeatureName.js # Main entry point component
```

## Detailed Description

### 1. `configs/`
Contains JavaScript modules exporting constants or configuration objects.
- `constants.js`: Action IDs, error codes, timeouts.
- `header-config.js`: Configuration for the navigation header.

### 2. `data-manager/`
Contains the `*-data-manager.js` component. This component has no UI (renders nothing) but orchestrates API calls using Global DMs.

### 3. `pages/`
Contains sub-directories for each logical screen in the feature.
- `dashboard/`: The main landing view.
- `multistep/`: For wizard-like flows.
- Each page is a LitElement component.

### 4. `shared-components/`
Components used by multiple pages within the feature but not generic enough to be in the global catalog.
- `help-modal/`
- `transition-wrapper/`

### 5. `mixins/`
- `WidgetMixin.js`: The most critical mixin. It standardizes configuration, localization (`BbvaCoreIntlMixin`), and navigation (`navigateForward`).

### 6. `utils/`
Pure functions for formatting, validation, etc.

## Example File Structure

```
src/
  BbvaFeatureExample.js
  configs/
    header-config.js
    step-completed-config.js
  data-manager/
    example-data-manager.js
  mixins/
    WidgetMixin.js
  pages/
    dashboard/
      dashboard-example.js
    multistep/
      multistep-example.js
  shared-components/
    help-modal/
      help-modal-example.js
  utils/
    constants.js
```
