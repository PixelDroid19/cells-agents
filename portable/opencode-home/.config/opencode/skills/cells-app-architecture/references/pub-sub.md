# PubSub (Publish/Subscribe)

Cells applications use a **Publish/Subscribe** pattern to decouple components. Components communicate by broadcasting messages on channels rather than invoking methods directly on other components.

## API

### Publishing

To send a message to a channel:

```javascript
// Basic publish
this.publish('my-channel', { some: 'data' });

// Publish with options
this.publish('my-channel', { some: 'data' }, {
  keep: true, // Keep last value for new subscribers
  forwardToNative: true // Send to native container (hybrid)
});
```

### Subscribing

To listen for messages on a channel:

```javascript
// In a component
this.subscribe('my-channel', (data) => {
  console.log('Received:', data);
});
```

## Best Practices

1.  **Decoupling**: Do not assume who is listening.
2.  **Naming**: Use namespaced channel names (e.g., `channel-name` is generic; prefer domain-specific like `login-success`).
3.  **Global vs. Local**: Most channels are global. Be careful of collisions.
