# Learning Fit

The app tracks lightweight feedback and usage events to help tune whether it supports learning:

- response length
- too much rate
- deepen rate
- session fragmentation
- patch rejection rate
- source usage
- map opening

This is not gamification. It is a tuning loop for response budget, map granularity, and overwhelm.

Use:

```sh
curl http://127.0.0.1:8787/api/learning-fit/report
```

