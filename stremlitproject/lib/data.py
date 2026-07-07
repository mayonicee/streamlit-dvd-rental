from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from lib.db import can_connect, read_sql


@dataclass(frozen=True)
class DataBundle:
    customer: pd.DataFrame
    rental: pd.DataFrame
    payment: pd.DataFrame
    film: pd.DataFrame
    category: pd.DataFrame
    store: pd.DataFrame
    rental_item: pd.DataFrame


@st.cache_data
def load_dummy_data(seed: int = 42) -> DataBundle:
    rng = np.random.default_rng(seed)

    # customer
    n_customers = 5245
    customer = pd.DataFrame(
        {
            "customer_id": range(1, n_customers + 1),
            "store_id": rng.choice([1, 2], n_customers, p=[0.55, 0.45]),
            "signup_date": pd.date_range("2022-01-01", periods=n_customers, freq="6h"),
        }
    )

    # store
    store = pd.DataFrame({"store_id": [1, 2], "city": ["Jakarta", "Surabaya"]})

    # category + film
    categories = ["Action", "Drama", "Comedy", "Horror", "Sci-Fi", "Animation", "Romance"]
    category = pd.DataFrame({"category_id": range(1, len(categories) + 1), "name": categories})

    film_titles = [
        "The Matrix",
        "Inception",
        "Pulp Fiction",
        "The Dark Knight",
        "Forrest Gump",
        "The Shawshank Redemption",
        "Fight Club",
        "Interstellar",
        "Gladiator",
        "Avatar",
        "Titanic",
        "The Godfather",
        "Jurassic Park",
        "The Avengers",
        "Frozen",
        "Action Hero",
        "Love Story",
        "Comedy Night",
        "Mystery Thriller",
        "Horror House",
    ]
    film = pd.DataFrame(
        {
            "film_id": range(1, len(film_titles) + 1),
            "title": film_titles,
            "category": rng.choice(categories, len(film_titles)),
            "rental_rate": rng.uniform(0.99, 4.99, len(film_titles)).round(2),
            "length": rng.integers(60, 180, len(film_titles)),
        }
    )

    # rental
    n_rentals = 16045
    rental_dates = pd.date_range("2023-01-01", "2023-12-31", freq="15min")
    rental_date = rng.choice(rental_dates, n_rentals)
    rental = pd.DataFrame(
        {
            "rental_id": range(1, n_rentals + 1),
            "customer_id": rng.choice(customer["customer_id"], n_rentals),
            "rental_date": rental_date,
            "return_date": rental_date + pd.to_timedelta(rng.integers(1, 7, n_rentals), unit="D"),
            "store_id": rng.choice([1, 2], n_rentals, p=[0.55, 0.45]),
        }
    )

    # rental_item
    rental_item_rows = []
    for rid in rental["rental_id"]:
        n_items = int(rng.integers(1, 4))
        for _ in range(n_items):
            rental_item_rows.append({"rental_id": int(rid), "film_id": int(rng.choice(film["film_id"]))})
    rental_item = pd.DataFrame(rental_item_rows)

    # payment (Store #2 slightly worse conversion)
    store_payment_prob = {1: 0.965, 2: 0.93}
    payment_rows = []
    for _, r in rental.iterrows():
        film_ids = rental_item.loc[rental_item["rental_id"] == int(r["rental_id"]), "film_id"].to_numpy()
        amount = float(film.loc[film["film_id"].isin(film_ids), "rental_rate"].sum())
        if rng.random() < store_payment_prob[int(r["store_id"])]:
            payment_rows.append(
                {
                    "payment_id": len(payment_rows) + 1,
                    "rental_id": int(r["rental_id"]),
                    "amount": amount,
                    "payment_date": pd.to_datetime(r["rental_date"]) + timedelta(days=int(rng.integers(0, 2))),
                }
            )
    payment = pd.DataFrame(payment_rows)

    return DataBundle(
        customer=customer,
        rental=rental,
        payment=payment,
        film=film,
        category=category,
        store=store,
        rental_item=rental_item,
    )


@st.cache_data(ttl=300)
def load_from_postgres(limit: Optional[int] = None) -> DataBundle:
    """
    Tries to read a Sakila/DVD-rental-like schema:
    - customer, rental, payment, film, category, store, inventory, film_category
    Produces a bundle aligned to the dashboard needs.
    """
    if not can_connect():
        raise RuntimeError("Cannot connect to PostgreSQL with current credentials.")

    lim = f"limit {int(limit)}" if limit else ""

    customer = read_sql(f"select customer_id, store_id, create_date as signup_date from customer {lim}")
    rental = read_sql(f"select rental_id, rental_date, return_date, inventory_id, customer_id, staff_id from rental {lim}")
    payment = read_sql(f"select payment_id, customer_id, rental_id, amount, payment_date from payment {lim}")
    film = read_sql(
        """
        select f.film_id, f.title, f.rental_rate, f.length,
               c.name as category
        from film f
        left join film_category fc on fc.film_id = f.film_id
        left join category c on c.category_id = fc.category_id
        """
    )
    category = read_sql("select category_id, name from category")
    store = read_sql(
        """
        select s.store_id, c.city
        from store s
        left join address a on a.address_id = s.address_id
        left join city c on c.city_id = a.city_id
        """
    )

    # Map rental to store_id via staff->store, plus rental_item via inventory->film
    staff = read_sql("select staff_id, store_id from staff")
    rental = rental.merge(staff, on="staff_id", how="left")

    inventory = read_sql("select inventory_id, film_id, store_id from inventory")
    rental_item = rental[["rental_id", "inventory_id"]].merge(inventory[["inventory_id", "film_id"]], on="inventory_id", how="left")[
        ["rental_id", "film_id"]
    ]

    # Normalize columns to match dummy bundle shapes
    customer = customer.rename(columns={"create_date": "signup_date"})
    rental = rental.rename(columns={"store_id": "store_id"})

    return DataBundle(
        customer=customer,
        rental=rental[["rental_id", "customer_id", "rental_date", "return_date", "store_id"]],
        payment=payment[["payment_id", "rental_id", "amount", "payment_date"]],
        film=film[["film_id", "title", "category", "rental_rate", "length"]],
        category=category,
        store=store,
        rental_item=rental_item,
    )


def load_data(prefer_postgres: bool = True) -> DataBundle:
    if prefer_postgres and can_connect():
        try:
            return load_from_postgres()
        except Exception:
            return load_dummy_data()
    return load_dummy_data()