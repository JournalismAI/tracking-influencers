# Diata

Service downloads profile, posts, images, tags, and location data associated with users' accounts available on Instagram via serverless ephemeral cloud functions.

## Setup

```sh
npm install
```

Make sure you create a `env.yaml` file first (see [env-example.yaml](env-example.yaml)) for guidance.

## Getting Started

Few steps are required before service can be used:

- setup GCP project

- create and download service account private key associated with the project in the root directory.

- create `list.csv` in the root directory with `username` header which contains list of usernames

- deploy private cloud functions located in [source](source/) in available regions

## Workflow

Service will automatically download list of user-agents but it can be triggered manually:

```sh
npm run useragents
```

To deploy existing cloud functions to GCP project:

```sh
npm run deploy
```

To start service:

```sh
npm start
```

To delete existing cloud functions from GCP project:

```sh
npm run cleanup
```

## Content Formats

JSON, NDJSON, KML, JPG and WEBP.

## Disclaimer

The use of the research software provided in this release is done at your own discretion and risk and you will be solely responsible for any damage to your computer system or loss of data that results from such activities. You are solely responsible for adequate protection and backup of the data and equipment used in connection with research software.

The research software may contain links to external websites that are not provided or maintained by it and does not guarantee the accuracy, relevance, timeliness, or completeness of any information on these external websites.

You are solely responsible for determining the appropriateness of using and distributing the research software and you assume all risks associated with its use.
