main_query = """
SELECT 
    f.title,
    c.name as category,
    f.rental_rate as price,
    COUNT(r.rental_id) as rental_count,
    COUNT(r.rental_id) * f.rental_rate as revenue,
    DATE_TRUNC('month', r.rental_date) as month
FROM film f
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
GROUP BY f.title, c.name, f.rental_rate, month
"""