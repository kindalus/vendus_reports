# Changelog

## [0.2.3] - 2026-10-14

### Fixed
- Months without receipts (Vendus HTTP 404 with `A001 / No data`) now produce a header-only receipts CSV instead of aborting monthly reports and Google Drive archiving. Other API failures remain fatal.

### Development
- Regenerated the lockfile because its `google-auth-httplib2==0.2.2` wheel returns HTTP 404 from PyPI. No dependencies were changed in the Kubernetes pod during the August recovery.
