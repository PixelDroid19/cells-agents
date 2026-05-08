# Cells Bridge Instance

The **Bridge** is the core kernel of a Cells application. It acts as a singleton that initializes the application, manages the navigation (routing), and provides the communication bus (PubSub).

## Initialization

The application starts by calling `window.CellsPolymer.start()`. This is typically found in the main entry point of the app (e.g., `app.js`).

```javascript
window.CellsPolymer.start({
  routes: {
    'home': '/',
    'dashboard': '/dashboard',
    'login': '/login'
  },
  // Other configuration options
  enableperfmonitor: false
});
```

## Responsibilities

1.  **Bootstrap**: Loads necessary resources and config.
2.  **Routing**: Maps URLs to pages.
3.  **State Management**: Can hold global application state (though decentralized state via PubSub is preferred).
4.  **Native Bridge**: Initializes the connection to the native container (in hybrid apps).
