---
theme: default
class: text-center
---

# CineVerse
## A Modern, Scalable IMDb Experience
A rapid 5-minute technical walkthrough of the project architecture, features, and design decisions.

---

## 1. Project Overview & Architecture

**CineVerse** is a feature-rich, scalable web application designed to let users discover, rate, review, and curate movies and TV shows.

### The Tech Stack
* **Backend:** Django 6.0 + Python 3.14
* **Database:** PostgreSQL (leveraging advanced search and indexing features)
* **Authentication:** `django-allauth` (Email + Google Social Login)
* **External APIs:** The Movie Database (TMDB) API
* **Infrastructure:** Docker Compose (Elasticsearch & Redis)

### Architectural Philosophy
* **Modular "Apps" Design:** Code is strictly segregated by domain (`accounts`, `titles`, `interactions`, `lists`, `social`, `search`).
* **Base Model Pattern:** Every model inherits from `apps.core.models.BaseModel`, providing UUIDs (for security), automatic timestamps, and **soft-delete** capabilities to preserve data integrity.

---

## 2. Core Domain: Titles & People

The heart of CineVerse lies in its catalog functionality.

* **Titles Engine:** Handles Movies, TV Shows, and Episodes. It natively supports self-referential foreign keys linking episodes to shows.
* **Denormalization for Speed:** `avg_rating` and `rating_count` are stored directly on the `Title` model. This avoids expensive database aggregations on the homepage or browse grid.
* **Smart URLs:** Image paths are stored as strings (e.g., TMDB short paths) and converted into full URLs dynamically via Python `@property` methods, with fallbacks to local uploads.

---

## 3. The "Lazy Loading" TMDB Sync

Instead of scraping and storing millions of movies upfront, CineVerse uses a highly efficient **on-demand sync**.

### How It Works:
1. **Search Fallback:** If a user searches for something not in the local database, CineVerse reaches out to the TMDB API, fetches the data, and silently syncs it to the local Postgres database (`sync_tmdb_to_local`).
2. **Detail Hydration:** When a user clicks a newly generated movie, CineVerse notices it lacks cast/crew data. It hits TMDB's detail endpoint, instantly syncing genres, actors, directors, and even YouTube trailer keys.
3. **The Result:** The database organically grows with only the content that users actually care about and interact with.

---

## 4. Engagement: Ratings & Reviews

We treat interactions carefully to ensure database consistency.

* **Decoupled Yet Integrated:** `Rating` and `Review` are separate models in Postgres to constrain them properly (e.g., enforcing 1-10 rating limits). However, they are bundled together logically in the Views for a seamless user frontend.
* **Atomic Transactions:** When a user rates a movie, `InteractionService.create_or_update_rating` triggers a `@transaction.atomic` block. It updates the user's rating and instantaneously recalculates the `Title`'s denormalized average rating, ensuring the UI is never out of sync.

---

## 5. Curation & Social Features

CineVerse elevates the user experience beyond a simple database by adding powerful community features.

### Custom Lists
* Users can build unlimited **Public or Private** lists.
* **Save / Bookmark:** Users can save other people's public lists to their own library as a reference.
* **Clone / Fork:** A one-click clone feature uses Django's `bulk_create` to instantly duplicate an entire list and all its movies into the user's private account, allowing them to remix someone else's curation!

### User Profiles
* A completely custom `User` model allowing localized bios, avatars, and social links.
* Public profiles neatly aggregate a user's recent reviews, ratings, and public custom lists.

---

## 6. Lightning Fast Discovery

Finding content must be instant and forgiving.

* **PostgreSQL Trigram Search:** Searches use `TrigramSimilarity` for fuzzy text matching, allowing users to make typos and still find the right movie.
* **Gin Indexes & SearchVectors:** The `Title` model uses advanced Postgres features to weight Titles ('A' weight) over Descriptions ('B' weight).
* **Dynamic Filtering:** The Browse view allows composable filtering (by Genre, Year ranges, and Minimum Ratings) while paginating elegantly.

*(Note: The codebase also contains foundational setups for Elasticsearch (`django_elasticsearch_dsl`), preparing the app for enterprise-grade distributed search scaling in the future.)*

---

## 7. Production-Ready Backbone

CineVerse is built to be deployed.

* **Settings Split:** It utilizes a modular settings pattern (`base.py`, `local.py`, `prod.py`) alongside `django-environ` for secure `.env` variable handling.
* **Security Middleware:** Includes `EnforceDomainMiddleware` to redirect raw IP address visits to a stable domain (like `.nip.io`), alongside proxy-IP handlers to ensure correct request routing behind reverse proxies like Nginx.
* **Fat Models, Skinny Views:** Complex logic (like the soft-delete manager, aggregate recalculations, and TMDB URL building) is pushed down to the Models and Services layer, keeping the HTTP Views clean and readable.

---
## End of Presentation
**Thank you for exploring CineVerse!**
