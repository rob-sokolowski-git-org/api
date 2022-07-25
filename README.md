## api

powers [fir-api.robsoko.tech](https://fir-api.robsoko.tech/docs)


![img](./assets/fir.jpg)


### local dev

While some features will work without credentials, to fully run the app locally, you'll need a local service account credentials file. Write to me if you with to run this code locally and I'll set you up.

While sitting in this directory, you may build the dev docker image:
```bash
./scripts/build.sh
```

You can then use the various `docker-compose up`/`run` services in the `docker-compose.yaml` file located in this directory:
 - `resolve-pip-deps` - resolves pip deps defined in `requirements.in` to the full dep tree, saved to `requirements.txt`
 - `pycharm-dev` - setup I use for pycharm
 - `pytest-dev` - run pytests
 - `upload-creds-to-bucket` - secrets are `.gitignored`, but located in `.private` This script uploads CI and production creds to their intended GCS bucket
 - `api-dev` - run the service outside the context of an IDE, if desired


### testing / deployment flow

tests are broken into two types
 * `internal_tests` - think unit tests, but they may go over the wire / access "real" resources
 * `api_tests` - "integration test" style tests that access the service over HTTP

On every PR issued against `main`, both test suites are run on CloudBuild via `docker-compose`.

Deployments are triggered when cutting a new tag. The intention is to deploy on every change to `main`


### environments
There are 3 environment
 * `local-dev.env` - used for local development
 * `.cloudbuild/ci.env` - used by CloudBuild in a dedicated CI env
 * production env is defined by the series of `--set-env-vars` flags in `.cloudbuild/deploy-to-cloud-run.yaml`

### Cloud Build & Secrets
This service uses Google Secrets Manager to access private resources.

The tests that run have dedicated resources (a CI scoped bucket, for example). This requires some environment variable wiring for CloudBuild, see `.cloudbuild/ci.env`

The `GOOGLE_APPLICATION_CREDENTIALS` variable points to a file in the running container that supplies the credentials for the
service account. There is a service account per environment.

This file gets written to differently depending on the context, in order to prevent committing secrets into GitHub:
 * For local dev, I simply mount the creds `.json`, which I keep in my `.gitignored` `./.private` directory in this repo
 * For CI, the test job first build the base image, fetches the secrets file from GCS, then builds the CI image. See `.cloudbuild/pr-build.yaml`
 * This pattern is repeated for production, but with a different credentials file. See `.cloudbuild/deploy-to-cloudrun.yaml`
