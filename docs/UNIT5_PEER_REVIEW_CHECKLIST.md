# Unit 5 Peer Review Checklist - Seth Roth

Recommended module to review: backend/API (`main.py`, `database.py`, `crud.py`, `schemas.py`).

Record at least one concrete observation in each area:

- Code quality/readability: Is the code easy to follow and consistently named?
- Security: Are credentials or configuration hardcoded? Is input controlled?
- Performance: Are full tables loaded unnecessarily? Are expensive operations repeated?
- Integration compatibility: Do API field names/routes match the React frontend?
- Documentation: Can another developer install and run the module from the README?

## Strong review comments already supported by the current repo

1. Database credentials were hardcoded in `database.py`; recommend environment configuration.
2. CORS originally allowed the backend origin instead of the React development origin.
3. The original root repository had no complete backend dependency file/setup guide.
4. Some CRUD field names and schemas were inconsistent, which can break frontend/backend integration.

Do not claim a teammate accepted or acted on a review comment until that actually happens in GitHub.
