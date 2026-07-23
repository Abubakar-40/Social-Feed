# Social Feed API

A simplified social feed system inspired by Facebook's interaction model — posts, comments, one-level-nested replies, likes on all content types, and optional hashtag detection/filtering. Built as a Django/DRF training project focused on relational modeling, ORM querying, and clean API design.

## Tech Stack

- Django 5.2
- Django REST Framework
- django-filter
- django-constance (runtime-editable settings)
- SQLite

## Project Structure

```
config/     project settings, root urls, WSGI/ASGI, BaseModel, custom middleware
users/      custom User model (AbstractUser), admin-managed, no signup/auth flow
feeds/      Post, Comment, Reply, Like, Hashtag models and all feed-related API logic
```

Users are managed entirely through Django Admin — there is no signup/login endpoint. All API requests authenticate via DRF token auth (`Authorization: Token <key>`).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Create auth tokens for users via `/admin/authtoken/tokenproxy/` or the Django shell.

## API Endpoints

All endpoints require authentication. Post endpoints are prefixed with `/api/posts/`; comment, like, and stats endpoints are prefixed with `/api/engagements/`.

### Posts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/` | List posts (search, filter, order, paginate) |
| POST | `/api/posts/` | Create a post (auto-detects `#hashtags`) |
| GET | `/api/posts/{id}/` | Post detail and engagement counts |
| PATCH | `/api/posts/{id}/` | Update a post (owner only) |
| DELETE | `/api/posts/{id}/` | Delete a post (owner only) |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/engagements/{id}/comments/` | List top-level comments on a post |
| POST | `/api/engagements/{id}/comments/` | Comment on a post |
| GET | `/api/engagements/comments/{id}/` | Comment detail, with its replies |
| PATCH | `/api/engagements/comments/{id}/` | Update a comment or reply (owner only) |
| DELETE | `/api/engagements/comments/{id}/` | Delete a comment or reply (owner only) |

### Replies

Replies are comments with a self-referential `reply_to` foreign key. The API permits only one level of nesting.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/engagements/comments/{id}/replies/` | Reply to a comment |

### Likes

Likes use a single generic `Like` model (via `GenericForeignKey`) shared across posts, comments, and replies.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/engagements/posts/{id}/like/` | Toggle like on a post |
| POST | `/api/engagements/comments/{id}/like/` | Toggle like on a comment |

### Hashtags & Filtering

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/hashtags/` | List all hashtags |
| GET | `/api/posts/?hashtag=django` | Filter posts by hashtag |
| GET | `/api/posts/?user={id}` | Filter posts by author |
| GET | `/api/posts/?search=text` | Search posts by content |

### Stats

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/engagements/stats/` | Top liked posts, most active users, content totals |

## Runtime Configuration

`MAX_POST_LENGTH` (default `500`) is editable live via `/admin/constance/config/` without a code deploy or restart.
