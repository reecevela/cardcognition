SELECT ec.card_name, ec.commander_id, ec.synergy_score
FROM public.edhrec_cards ec
WHERE ec.card_name IN (
	SELECT card_name
	FROM public.edhrec_cards
	GROUP BY card_name
	HAVING COUNT(DISTINCT commander_id) > 1
)
ORDER BY ec.card_name DESC

