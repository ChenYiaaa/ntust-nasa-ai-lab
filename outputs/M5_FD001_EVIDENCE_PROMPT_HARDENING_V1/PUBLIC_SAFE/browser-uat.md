# Browser UAT

Microsoft Edge 158.0.4370.33, via Playwright Core 1.65.1 on Windows, ran
against the real Flask and Node loopback listeners. The browser command
exited 0. It logged zero uncaught JavaScript exceptions and 17 resource
errors from deliberate negative paths or the favicon request.

| Case | Observation |
| --- | --- |
| M3/M4 behavior | Existing scenarios covered initial load, Train/Test, Unit, Sensor and Cycle selection, loading, stale History cancellation, chart, statistics and source records. The module and four approved API proxy routes passed the existing HTTP checks. |
| Nine sections | Every heading matched the required order. Real Train and Test prompts matched selected identity, all eight Catalog fields, every source locator, measurement and independently calculated statistic. |
| Evidence classes | Observed, calculated, inferred and unknown content remained distinct. The real cases reported no additional inference, and kept physical meaning, fault, cause, RUL and Health Score unestablished. |
| Copy | Clicked the real Copy button, waited for success and read the actual clipboard. Compared every character allowing only the pre-existing Windows native LF-to-CRLF conversion. |
| Invalidation | New split, Unit, Sensor, start or end selection removed the old prompt. Invalid source locators and a deliberately inconsistent Catalog source field left generation and copy disabled. |
| Failure states | Empty responses, network abort and controlled API errors disabled prompt controls. A real isolated Backend HTTP 503 was shown as an error with no new prompt. |
| Layout and keyboard | At 375 px the chart, source table, prompt and copy remained usable. The split selector accepted keyboard navigation. |

The initial-state screenshot was reviewed for private information and shows
an empty preview before selection. Browser coverage is limited to Windows
Edge at desktop and narrow viewport widths. Actual clipboard operations
depend on browser permission.
