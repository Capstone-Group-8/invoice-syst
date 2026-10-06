# CI/CD Evidence

The project uses GitHub Actions for continuous integration on pull requests to main.

Current automated checks include:

    backend-tests — runs the Python backend test suite
    frontend-build — verifies the React/Vite production build

Latest verification:

    53 backend tests passed
    React/Vite production build passed
    Both GitHub Actions checks completed successfully on PR #31

The current project is run/deployed locally for the capstone demonstration. A production hosting/deployment pipeline is not currently configured, so the GitHub Actions workflow is being used primarily for automated integration and build validation.
