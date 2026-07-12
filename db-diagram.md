### Entity–Relationship Diagram

The diagram below is rendered natively by GitHub (Mermaid). A raster copy is
available at [`db-schema.jpg`](db-schema.jpg) and the standalone version with
full notes at [`DB-SCHEMA.md`](DB-SCHEMA.md).

> **Legend** — `PK` primary key · `FK` foreign key · `UK` unique key ·
> `||--o{` one-to-many (mandatory parent) · `|o--o{` one-to-many (nullable parent).

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryTextColor':'#000000','textColor':'#000000','lineColor':'#334155'}}}%%
erDiagram
    CATEGORY   ||--o{ PRODUCT               : "categorizes"
    CATEGORY   ||--o{ SALE                  : "classifies"
    USER       |o--o{ ORDER                 : "places"
    USER       ||--o{ PRODUCT_REVIEW        : "writes"
    USER       |o--o{ PRODUCT_PRICE_HISTORY : "changed_by"
    PRODUCT    ||--o{ PRODUCT_REVIEW        : "receives"
    PRODUCT    ||--o{ PRODUCT_PRICE_HISTORY : "tracked_by"
    PRODUCT    ||--o{ SALE                  : "sold_as"
    PRODUCT    ||--o{ ORDER_ITEM            : "ordered_as"
    ORDER      ||--o{ ORDER_ITEM            : "contains"
    ORDER      |o--o{ SALE                  : "generates"

    CATEGORY {
        bigint   id            PK
        varchar  name              "max 200, indexed"
        varchar  slug          UK  "max 200"
    }

    PRODUCT {
        bigint   id            PK
        bigint   category_id   FK  "-> CATEGORY"
        varchar  name              "max 200, indexed"
        varchar  slug              "max 200, indexed"
        varchar  image             "upload_to products/"
        text     description       "optional"
        decimal  cost_price        "10,2"
        decimal  price             "10,2"
        int      stock             "unsigned"
        bool     available         "default true"
        bool     is_online         "warehouse flag, default false"
        datetime created           "auto_now_add"
        datetime updated           "auto_now"
    }

    USER {
        int      id            PK
        varchar  username      UK  "max 150"
        varchar  email             "max 254"
        varchar  first_name        "max 150"
        varchar  last_name         "max 150"
        varchar  password          "hashed, max 128"
        bool     is_staff
        bool     is_superuser
        bool     is_active
        datetime date_joined
    }

    PRODUCT_REVIEW {
        bigint   id                PK
        bigint   product_id        FK,UK "-> PRODUCT  (unique with user_id)"
        int      user_id           FK,UK "-> USER  (unique with product_id)"
        smallint rating               "1-5"
        varchar  title                "max 200, optional"
        text     comment
        bool     verified_purchase    "default false"
        datetime created              "auto_now_add"
        datetime updated              "auto_now"
    }

    PRODUCT_PRICE_HISTORY {
        bigint   id                PK
        bigint   product_id        FK "-> PRODUCT"
        decimal  cost_price           "10,2"
        decimal  selling_price        "10,2"
        int      changed_by_id     FK "-> USER, SET NULL"
        datetime changed_at           "auto_now_add"
        text     reason               "optional"
    }

    ORDER {
        bigint   id                PK
        int      user_id           FK "-> USER, nullable"
        varchar  first_name           "max 50"
        varchar  last_name            "max 50"
        varchar  email                "max 254"
        varchar  address              "max 250"
        varchar  postal_code          "max 20"
        varchar  city                 "max 100"
        datetime created              "auto_now_add"
        datetime updated              "auto_now"
        bool     paid                 "default false"
        varchar  payment_method       "card/paypal/bank/cash"
        varchar  payment_id           "nullable"
        varchar  status               "pending/processing/shipped/delivered/cancelled"
    }

    ORDER_ITEM {
        bigint   id                PK
        bigint   order_id          FK "-> ORDER"
        bigint   product_id        FK "-> PRODUCT"
        decimal  price                "10,2, price at order time"
        int      quantity             "unsigned, default 1"
    }

    SALE {
        bigint   id                PK
        bigint   order_id          FK "-> ORDER, nullable"
        datetime date                 "auto_now_add"
        bigint   category_id       FK "-> CATEGORY"
        bigint   item_id           FK "-> PRODUCT"
        decimal  sold_price           "10,2"
        int      quantity             "unsigned, default 1"
    }

    %% light app-colored fills with BLACK text for readability
    style USER                  fill:#d1fae5,stroke:#059669,color:#000000
    style CATEGORY              fill:#dbeafe,stroke:#2563eb,color:#000000
    style PRODUCT               fill:#dbeafe,stroke:#2563eb,color:#000000
    style PRODUCT_REVIEW        fill:#dbeafe,stroke:#2563eb,color:#000000
    style PRODUCT_PRICE_HISTORY fill:#dbeafe,stroke:#2563eb,color:#000000
    style SALE                  fill:#dbeafe,stroke:#2563eb,color:#000000
    style ORDER                 fill:#ffedd5,stroke:#ea580c,color:#000000
    style ORDER_ITEM            fill:#ffedd5,stroke:#ea580c,color:#000000
```

> The **shopping cart is session-based** (`request.session['cart']`) and has **no
> database table**, so it does not appear above.
>
> **`PRODUCT_REVIEW`** has a composite `UNIQUE (product_id, user_id)` constraint
> — one review per user per product.