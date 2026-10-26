# Useful Commands

## Run locally using flask

### navigate to the project directory:
>developing-the-interactive-web-project-1-group-6/appycampers/src/appycampers

### run the command: 
```sh
uv run flask --app server run --debug
```

# Sources Referenced

## For NavBar
* https://pure-css.github.io/layouts/tucked-menu-vertical/#
* https://pure-css.github.io/menus/

## Database

### Setup Explore Camps Search index
```sql
CREATE INDEX camp_search ON camps USING GIN (
    to_tsvector('english', name || ' ' || COALESCE("campoutDescription", ''))
);
```