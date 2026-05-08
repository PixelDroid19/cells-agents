# Monitoring

## Scope

Use this topic for Cells application monitoring, SeMAAS integration, logging, and tracing.

## SeMAAS Integration

Cells Bridge integrates with SeMAAS (BBVA's monitoring platform) for logging and tracing via Omega and RHO services.

Configuration is in the application config file (`app/config/<environment>.json`):

```json
{
  "logs": true,
  "semaas": {
    "tsec2JWTEndpoint": "https://portunus-hub-es.work.global.platform.bbva.com/v1/tsec",
    "policy": "POLICY_VALUE",
    "mrId": "MONITOR_RESOURCE_ID_VALUE",
    "nameSpace": "NAMESPACE_VALUE",
    "consumerId": "CONSUMER_ID_VALUE",
    "dnsTld": "platform.bbva.com",
    "region": "live.es",
    "version": "v1",
    "logLevel": "warn"
  }
}
```

## Monitoring Log Levels

Valid log levels (highest to lowest): `fatal`, `error`, `warn`, `info`, `debug`

Set `logLevel` to filter traces sent to SeMAAS. Only traces at or above the configured level are sent.

## CellsElement / CellsPage Monitoring API

`CellsElement` and `CellsPage` provide a monitoring API for logging and tracing.

### log(logObject)

Send a log to Omega:

```js
this.log({
  mrId: 'monitor-resource-id',
  spanId: 'span-id',
  traceId: 'trace-id',
  creationDate: Date.now(),
  level: 'info',
  message: 'user-action',
  properties: { userId: 123 }
});
```

### createSpan(spanData)

Create a span for tracing:

```js
const span = this.createSpan({
  mrId: 'monitor-resource-id',
  name: 'operation-name',
  traceId: traceId,
  parentSpan: parentSpanId,
  properties: { key: 'value' }
});
span.start();
// ... do work
span.finish();
```

### createUUID()

Generate a UUID for trace identifiers:

```js
const traceId = this.createUUID();
```

### ingest([spans])

Mark spans to be sent to SeMAAS:

```js
this.ingest([pageSpan, networkSpan, processingSpan]);
```

### flush()

Send all enqueued traces immediately (since Cells Bridge 3.16.0):

```js
this.flush();
```

## Span Object

Spans track the duration of operations:

```js
{
  mrId: string,          // monitor resource id (mandatory)
  spanId: string,         // auto-generated
  name: string,           // span name
  startDate: number,      // auto-set on creation
  finishDate: number,     // set on finish()
  traceId: string,
  parentSpan: string,     // parent span id
  duration: number,
  properties: object,
  recordDate: number
}
```

## Inter-Service Tracing (X-RHO Headers)

For distributed tracing across services, propagate trace context via HTTP headers:

```
X-RHO-TRACEID: <trace-id>
X-RHO-PARENTSPANID: <parent-span-id>
```

When using `BGADP` or `cells-generic-dp` with `semaasMonitoring: true`, these headers are sent automatically if `x-rho-traceid` and `x-rho-parentspanid` are in sessionStorage.

## Log Object Schema

```js
{
  mrId: string,           // monitor resource id (mandatory)
  spanId: string,          // associated span id
  traceId: string,         // trace identifier
  creationDate: number,     // auto-set if omitted
  level: string,           // debug/info/warn/error/fatal
  message: string,         // log message (mandatory)
  properties: object       // additional context
}
```

## Signals to extract

- whether monitoring is enabled in config
- logLevel configuration
- custom spans in the codebase
- inter-service trace propagation via X-RHO headers
- flush() usage for real-time logging

## Use when

- setting up monitoring for a Cells app
- adding custom logging to components
- tracing async operations across services
- configuring SeMAAS integration
- reviewing monitoring coverage in a feature
