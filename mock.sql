SELECT MIN(mc.note) AS production_note,
       MIN(t.title) AS movie_title,
       MIN(t.production_year) AS movie_year
FROM title AS t,
     movie_info AS mi,
     movie_info_idx AS mi_idx,
     movie_link AS ml, 
     complete_cast AS cc
WHERE t.production_year BETWEEN 2005 AND 2010
  AND t.id = mi_idx.movie_id
  AND ml.movie_id = mi.movie_id
  AND t.id = cc.movie_id