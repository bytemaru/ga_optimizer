SELECT MIN(t.title) AS movie_title,
       MIN(t.production_year) AS movie_year
FROM movie_info AS mi,
     movie_info_idx AS mi_idx,
     title AS t
WHERE t.production_year BETWEEN 2005 AND 2010
  AND t.id = mi_idx.movie_id
  AND t.id = mc.movie_id
  AND mc.movie_id = mi_idx.movie_id