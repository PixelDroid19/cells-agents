# Component API

## Scope

Use this topic for public component contracts and package exposure.

## Core rules

- A component package API includes custom element API, styling API, and package entry points.
- Public custom element API includes properties, attributes, methods, events, and slots.
- Public properties should have matching attributes when appropriate.
- Property names and attribute names should follow standard Cells and Lit conventions, usually kebab-case for attributes.
- Do not overwrite public property values internally; compute internal state separately.
- Events should document their type and, when relevant, detail payload and bubbling behavior.
- Package entry points and exports are part of the public API and affect versioning.
- Exported classes should remain available for extension.
- `custom-elements.json` and package exports are authoritative for package-level API shape.
- Packaging should expose only the files needed as dependency entry points.

## Signals to extract

- exported class names
- custom element names
- reflected attributes
- events and detail payloads
- slots
- package exports and entry points

## Use when

- researching component contracts
- validating API claims
- checking packaging and public exports
