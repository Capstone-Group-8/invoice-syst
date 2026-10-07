# Unit 5 Peer Review Checklist - Sally Little

Recommended module to review: Frontend uploader/PR 31 (`App.jsx`, `invoice_parser.py`, `uploader.py`).

Record at least one concrete observation in each area:

- Code quality/readability: Is the code easy to follow and consistently named?
- Security: Are credentials or configuration hardcoded? Is input controlled?
- Performance: Are full tables loaded unnecessarily? Are expensive operations repeated?
- Integration compatibility: Do API field names/routes match the React frontend?
- Documentation: Can another developer install and run the module from the README?

## Comments

1. Code is largely readable, but some comments that make it easier to work with were deleted.
2. Improper inputs are largely controlled. Allow-Origin is left as * in one place, but I deleted this in the code I'm about to push, so no action needed.
3. Performance updates coming through on next push.
4. Schema updated.Integration apparently working fine.
5. Documentation updates TBD.

Do not claim a teammate accepted or acted on a review comment until that actually happens in GitHub.
