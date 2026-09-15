'''Planned upload/orchestration module.

The original repository contained pseudocode in this .py file. The functions are
kept as valid stubs so automated tests and tooling can import the project safely.
OCR integration remains a team Alpha task.
'''


def upload_invoice():
    return None


def use_ocr(payload):
    raise NotImplementedError("OCR-to-main-API integration is still in progress")


def push_initial_read(invoice_file):
    raise NotImplementedError("Initial OCR persistence workflow is still in progress")


def push_updated_read():
    raise NotImplementedError("Updated invoice persistence workflow is still in progress")
