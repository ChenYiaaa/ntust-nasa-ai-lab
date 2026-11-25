# Browser UAT

Microsoft Edge 158.0.4370.33 ran through Playwright Core 1.65.1 with real
loopback Flask and Node servers. All prior M3 scenario assertions were
retained. The initial screenshot output was redirected to the M4 evidence
directory to preserve M3 evidence.

| Check | Observed |
| --- | --- |
| Startup and selectors | Health and Catalog 200. Unit and Cycle reset on split change. Sensor labels preserve contract units. Verified ranges come from the API. |
| Static module | Browser import fetched `/prompt.mjs` with HTTP 200 and `text/javascript; charset=utf-8`. All four existing static paths remained HTTP 200. |
| Proxy and security | Four approved API responses matched direct Flask bodies. Structured 422 was preserved. Unknown and private routes, plus encoded traversal, returned 404. POST returned 405 and invalid Host returned 400. Assets retained no-store and nosniff. Server diff retained the explicit IPv4 loopback binding and added exactly one static mapping. |
| Prompt generation | Controls start disabled. Valid History enables generation. Train and Test exact counts and source parity are in [verification](verification.md). |
| Prompt invalidation | Split, Unit, Sensor, start and end changes cleared the preview and disabled both actions. Invalid locators or empty results produced no usable prompt. A delayed History response was discarded after a split change. |
| Clipboard | Browser context granted clipboard permissions for localhost. Clicked Copy prompt, waited for success and read actual clipboard content back. Both mandatory queries matched the preview, allowing only Windows native CRLF conversion. |
| Error states | Controlled failures covered M2 response codes, invalid parameters, 500 and network abort. An isolated missing-source Backend returned actual 503. Browser showed the error and disabled prompt actions. |
| Responsive regression | At 375 px, the record table and real chart remained usable. Keyboard selection succeeded. The narrow viewport query also produced and copied a prompt. |

First browser run exited 1 because Windows returned CRLF from clipboard
readback while the textarea value used LF. The rerun checked every character
against the original or its exact native newline form. Final exit code was
0. Browser reported zero uncaught JavaScript exceptions and 16 resource
errors from intentionally failing requests or favicon lookup.

[Public initial screenshot](browser-initial.png) was visually audited before
staging. It contains no measurements, full prompt, private paths or identifiers.
Clipboard access depends on browser permission. The site and tests use
localhost, and browser verification covers Edge on Windows.
