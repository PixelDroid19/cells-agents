# BBVA Cells Intent Map

Use these search seeds when the user describes product intent instead of package names.

## Forms And Data Entry

- Query seeds: `login form validation`, `signup form`, `otp verification`, `date range picker`, `search input`, `file upload`
- Common packages:
  - `bbva-form-input`
  - `bbva-form-container`
  - `bbva-form-select`
  - `bbva-form-checkbox`
  - `bbva-form-toggle`
  - `bbva-form-verification`
  - `bbva-form-uploader`
  - `bbva-form-date-range`

## Actions And CTAs

- Query seeds: `primary action button`, `secondary button`, `button group`, `share action`
- Common packages:
  - `bbva-button-default`
  - `bbva-button-action`
  - `bbva-button-group`
  - `bbva-button-row`
  - `bbva-button-share`
  - `bbva-button-progress`

## Headers And Navigation

- Query seeds: `main header`, `public header`, `navigation menu`, `tab bar`, `tabs`
- Common packages:
  - `bbva-header-main`
  - `bbva-header-navigation`
  - `bbva-header-public`
  - `bbva-navigation-menu`
  - `bbva-navigation-tab-bar`
  - `bbva-tab-default`

## Feedback And Status

- Query seeds: `toast notification`, `status message`, `contextual help`, `skeleton loading`, `progress stepper`
- Common packages:
  - `bbva-notification-toast`
  - `bbva-notification-status`
  - `bbva-notification-message`
  - `bbva-notification-contextual`
  - `bbva-help-tooltip`
  - `bbva-help-modal`
  - `bbva-skeleton-default`
  - `bbva-progress-step`
  - `bbva-progress-stepped-process`

## Tables And Structured Data

- Query seeds: `data table`, `filterable table`, `table header`, `table footer`
- Common packages:
  - `bbva-table-default`
  - `bbva-table-filter`
  - `bbva-table-header`
  - `bbva-table-footer`
  - `bbva-table-body`
  - `bbva-table-row-group`

## Lists, Panels, And Display

- Query seeds: `card list`, `side panel`, `comparison panel`, `bullet list`, `budget list`
- Common packages:
  - `bbva-list-budget`
  - `bbva-list-bullet`
  - `bbva-list-swipe`
  - `bbva-panel-container`
  - `bbva-panel-side`
  - `bbva-panel-comparative`
  - `bbva-panel-photo`

## Charts, Maps, And Rich Visuals

- Query seeds: `bar chart`, `donut chart`, `map view`, `hero banner`, `carousel`
- Common packages:
  - `bbva-data-visualization-bar`
  - `bbva-data-visualization-donut`
  - `bbva-data-visualization-linear`
  - `bbva-data-visualization-maps`
  - `bbva-map-dynamic`
  - `bbva-map-static`
  - `bbva-banner-image`
  - `bbva-carousel-default`

## Typography, Badges, And Media Tokens

- Query seeds: `amount text`, `date text`, `status badge`, `icon badge`, `card clip`, `flag clip`
- Common packages:
  - `bbva-type-amount`
  - `bbva-type-date`
  - `bbva-type-icon`
  - `bbva-type-link`
  - `bbva-type-text`
  - `bbva-badge-default`
  - `bbva-badge-feedback`
  - `bbva-badge-notification`
  - `bbva-clip-card`
  - `bbva-clip-flag`

## Search Strategy

- Start with the user's product language, not package names
- Retry with 2-3 synonyms if the first query is noisy
- For a final recommendation, inspect the winning package with `--package`
- If two packages overlap, compare custom elements, key props, and events before choosing
