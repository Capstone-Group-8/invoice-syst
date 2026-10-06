# Code Quality and Performance Benchmarks

Benchmarks were run locally on the final capstone build using Python 3.13.15, the local SQLite database, and CPU-based EasyOCR.
## Test Coverage / Reliability

    53 of 53 automated tests passed
    Overall measured code coverage: 83%
    invoice_parser.py: 90%
    main.py: 87%
    crud.py: 86%
    validation.py: 97%
    Test suite completed in 6.95 seconds

Formal peer-review evidence is also available through the team's GitHub pull requests.
## API Performance

Local benchmark of GET /invoices/all:

    100 total requests
    10 concurrent workers
    100/100 successful responses
    100% success rate
    Average response time: 581.98 ms
    Median response time: 563.00 ms
    95th percentile response time: 684.38 ms
    Maximum response time: 725.58 ms
    Throughput: 16.62 requests/second

These figures represent a local development environment using Uvicorn and SQLite and should not be treated as production-scale hosting benchmarks.
## OCR / Parsing Performance

A real invoice PDF was processed through the OCR/parser pipeline:

    644 OCR results extracted
    76 invoice line items parsed
    OCR processing time: 56.31 seconds
    Parsing time: 0.11 seconds
    Total OCR + parsing time: 56.42 seconds

The benchmark shows that OCR is currently the primary processing bottleneck in the local CPU-only configuration, while structured parsing adds very little additional processing time.
## Summary

The current build successfully passed all automated tests, achieved 83% measured code coverage, handled the local concurrent API test without request failures, and successfully processed a real invoice through the OCR pipeline.
