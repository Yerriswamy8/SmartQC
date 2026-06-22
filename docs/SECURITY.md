# Public Demo Safety Checklist

This repository contains only synthetic data and mock hardware adapters.

Never commit:

- company or customer names, logos or datasets
- PLC addresses, DB numbers, tags or network diagrams
- camera/laser serial numbers from production
- trained weights, licensed SDKs or proprietary DLLs
- AWS access keys, database passwords or `.env`
- production recipes, thresholds or inspection outputs
- source code copied from an employer-owned repository

Before a public release, run secret scanning, dependency scanning and license review. Change `DEMO_ALLOW_ANONYMOUS=false`, configure authentication, disable debug mode, rotate secrets and restrict CORS for any non-local deployment.
