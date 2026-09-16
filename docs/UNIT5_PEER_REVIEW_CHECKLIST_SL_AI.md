# Unit 5 Peer Review Checklist - Sally Little

Recommended module to review: Invoice Extraction backend (`main.py`, `invoice_parser.py`, `ocr_reader.py`, `use_data.py`).

Record at least one concrete observation in each area:

- Code quality/readability: Is the code easy to follow and consistently named?
- Security: Are credentials or configuration hardcoded? Is input controlled?
- Performance: Are full tables loaded unnecessarily? Are expensive operations repeated?
- Integration compatibility: Do API field names/routes match the React frontend?
- Documentation: Can another developer install and run the module from the README?

## Strong review comments already supported by the current repo

1. The code is not particularly easy to read. Modularity seems excessive--is there a good reason to have four different files involved? I think it's a good idea to have ocr\_reader as its own module for replaceability etc. but parse\_invoice\_fields, use\_data, and main could surely be condensed into at least two. (I know I wrote one of these. I take the blame.)
2. Invoices are still being uploaded through a 'dropbox'. Need to shift to integrate with React frontend.
3. Parsed output is still being exported instead of presented to the user. Need to shift to integrate with React frontend.
4. No README written yet specific to this module.

Do not claim a teammate accepted or acted on a review comment until that actually happens in GitHub.
