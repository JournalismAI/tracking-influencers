# ![LOGO](https://github.com/jaifp-tracking-influencers/assets/raw/main/img/logo-50x50.png) Tracking influencers

[Tracking influencers](https://tracking-influencers.com/) aims to help journalists investigate influencers on social platforms on a greater scale using AI technologies and developing a replicable methodology. The initial focus of the project is on Instagram and specifically on creating a system to flag those users who are promoting brands or services without complying with the guidelines that mandate disclosure of all commercial relationships.

This project is part of the [2022 JournalismAI Fellowship Programme](https://www.lse.ac.uk/media-and-communications/polis/JournalismAI/Fellowship-Programme). The Fellowship brought together 46 journalists and technologists from across the world to collaboratively explore innovative solutions to improve journalism via the use of AI technologies. You can explore all the Fellowship projects [at this link](https://www.lse.ac.uk/media-and-communications/polis/JournalismAI/Fellowship-Programme).

The project was developed as a collaboration between [Sky News](https://news.sky.com/), [The Guardian](https://www.theguardian.com/international), [Infobae](https://www.infobae.com/) and [Il Sole 24 Ore](https://www.ilsole24ore.com/).

[JournalismAI](https://www.lse.ac.uk/media-and-communications/polis/JournalismAI) is a project of [Polis](https://www.lse.ac.uk/media-and-communications/polis) – the journalism think-tank at the London School of Economics and Political Science – and it’s sponsored by the [Google News Initiative](https://newsinitiative.withgoogle.com/). If you want to know more about the Fellowship and the other JournalismAI activities, [sign up for the newsletter](https://mailchi.mp/lse.ac.uk/journalismai) or get in touch with the team via hello@journalismai.info

## 📃 Project documentation

The report of this adventure: the challenges faced, the goals achieved and those still to be implemented, the mistakes made and the advice to avoid repeating them.

> [https://tracking-influencers.com/](https://tracking-influencers.com/)

## Repos

### ⚙️ backend-influencers

The content management system used to store the data, with the content-types and the relationships implemented.

> [backend-influencers](backend-influencers)

> [More info in the Strapi Rest API section](https://tracking-influencers.com/docs/gathering-data#strapi-rest-api)

### 🇹 tensorquery

Chrome extension to save Tensor Social query locally for the API use

> [tensorquery](tensorquery)

> [More info in the Marketing platforms section](https://tracking-influencers.com/docs/platform-and-accounts-selection#social-media-marketing-platforms)

### 🛠️ tensorsocial

App to interact with Tensor Social API

> [tensorsocial](tensorsocial)

> [More info in the Marketing platforms section](https://tracking-influencers.com/docs/platform-and-accounts-selection#social-media-marketing-platforms)

### ↔️ tensorsocial-to-strapi

Python script to import data from the socialmedia platform Tensor Social to database

> [tensorsocial-to-strapi](tensorsocial-to-strapi)

> [More info in the Marketing platforms section](https://tracking-influencers.com/docs/platform-and-accounts-selection#social-media-marketing-platforms)

### 👁️‍🗨️ influ-post-import

Python script to import scraped posts to database

> [influ-post-import](influ-post-import)

### 🏷️ brands-import

Script to import Instagram profiles of 25,282 brands to database

> [brands-import](brands-import)

### 📈 analysis

The python and R scripts that allowed us to conduct the exploratory analysis of the data collected and to obtain the preliminary results.

> [analysis](analysis)

> [More info in the Analysis section](https://tracking-influencers.com/docs/analysis)

### 📸 frontend-influencers

Project documentation

> [frontend-influencers](frontend-influencers)

### 🔎 lib-test

Python scraping library tests

> [lib-test](lib-test)

## 📬 Contacts

For questions, notices or collaborations, please write to
[jaifp.tracking.influencers@gmail.com](mailto:jaifp.tracking.influencers@gmail.com)
