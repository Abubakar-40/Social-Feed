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

All endpoints are prefixed with `/api/posts/` and require authentication.

### Posts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/` | List posts (search, filter, order, paginate) |
| POST | `/api/posts/` | Create a post (auto-detects `#hashtags`) |
| GET | `/api/posts/{id}/` | Post detail, with nested comments and replies |
| PATCH | `/api/posts/{id}/` | Update a post (owner only) |
| DELETE | `/api/posts/{id}/` | Delete a post (owner only) |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/{id}/comments/` | List comments on a post |
| POST | `/api/posts/{id}/comments/` | Comment on a post |
| GET | `/api/posts/comments/{id}/` | Comment detail, with nested replies |
| PATCH | `/api/posts/comments/{id}/` | Update a comment (owner only) |
| DELETE | `/api/posts/comments/{id}/` | Delete a comment (owner only) |

### Replies

Replies are a separate model from comments (not self-referential), which structurally enforces one level of nesting.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/comments/{id}/replies/` | List replies on a comment |
| POST | `/api/posts/comments/{id}/replies/` | Reply to a comment |
| GET | `/api/posts/replies/{id}/` | Reply detail |
| PATCH | `/api/posts/replies/{id}/` | Update a reply (owner only) |
| DELETE | `/api/posts/replies/{id}/` | Delete a reply (owner only) |

### Likes

Likes use a single generic `Like` model (via `GenericForeignKey`) shared across posts, comments, and replies.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/posts/{id}/like/` | Toggle like on a post |
| POST | `/api/posts/comments/{id}/like/` | Toggle like on a comment |
| POST | `/api/posts/replies/{id}/like/` | Toggle like on a reply |

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
| GET | `/api/posts/stats/` | Top liked posts, most active users, content totals |

## Runtime Configuration

`MAX_POST_LENGTH` (default `500`) is editable live via `/admin/constance/config/` without a code deploy or restart.
