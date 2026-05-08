# Troubleshooting

## Node.js Version Issues

**Issue**: `Error: No such module: http_parser`
This error occurs when using a newer version of Node.js (e.g., v24.x) that has removed the `http_parser` binding required by older Cells CLI versions.

```
Error: No such module: http_parser
    at process.binding (node:internal/bootstrap/realm:162:11)
    at Object.<anonymous> (.../node_modules/http-deceiver/lib/deceiver.js:22:24)
    ...
```

**Solution**:
1.  Check your current Node.js version:
    ```bash
    nvm list
    ```
2.  Switch to Node.js 18:
    ```bash
    nvm use 18
    ```
3.  Ensure you use this version when running any Cells CLI commands.
